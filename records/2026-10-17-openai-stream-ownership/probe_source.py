"""Offline source-method probe; this is not a full Agents SDK integration test."""

import ast
import asyncio
import hashlib
import json
import logging
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "upstream_result.py"
METHODS = {
    "stream_events", "cancel", "_cleanup_tasks", "_await_task_safely",
    "_drain_event_queue", "_drain_input_guardrail_queue",
}
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
original = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "RunResultStreaming")
selected = [n for n in original.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in METHODS]
assert {n.name for n in selected} == METHODS
module = ast.Module(body=[
    ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
    ast.ClassDef(name="ExtractedMethods", bases=[], keywords=[], body=selected, decorator_list=[]),
], type_ignores=[])
ast.fix_missing_locations(module)


class QueueCompleteSentinel:
    pass


class MaxTurnsExceeded(Exception):
    pass


namespace = {
    "asyncio": asyncio,
    "QueueCompleteSentinel": QueueCompleteSentinel,
    "MaxTurnsExceeded": MaxTurnsExceeded,
    "logger": logging.getLogger("offline-source-probe"),
    "_should_drain_stream_events_before_raising": lambda error: False,
}
exec(compile(module, str(SOURCE), "exec"), namespace)


class Harness(namespace["ExtractedMethods"]):
    """Minimal state; error, model-provider and sandbox behavior is excluded."""

    def __init__(self):
        self._event_queue = asyncio.Queue()
        self._input_guardrail_queue = asyncio.Queue()
        self._active_stream_consumers = 0
        self._stream_consumers_stopped = asyncio.Event()
        self._stream_consumers_stopped.set()
        self._waiting_on_event_queue = False
        self._stored_exception = None
        self._cancel_mode = None
        self.is_complete = False
        self.run_loop_task = None
        self._sandbox_wrapped_run_loop_task = None
        self._input_guardrails_task = None
        self._output_guardrails_task = None

    def _check_errors(self):
        pass

    async def _await_model_provider_cleanup(self):
        pass

    async def _run_sandbox_cleanup(self):
        pass


OBSERVATIONS = []


class OwnershipProbe(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.result = Harness()
        self.release = asyncio.Event()
        self.started = asyncio.Event()
        self.settled = asyncio.Event()
        self.iterator = None
        self.child_tasks = []

        async def producer():
            self.started.set()
            try:
                await self.release.wait()
                self.result.is_complete = True
                self.result._event_queue.put_nowait(QueueCompleteSentinel())
            finally:
                self.settled.set()

        self.result.run_loop_task = asyncio.create_task(producer())
        await asyncio.wait_for(self.started.wait(), 2)

    async def asyncTearDown(self):
        self.result.cancel()
        self.release.set()
        for task in self.child_tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.child_tasks, return_exceptions=True)
        await asyncio.gather(self.result.run_loop_task, return_exceptions=True)
        if self.iterator is not None:
            await asyncio.wait_for(self.iterator.aclose(), 2)

    async def prime(self):
        self.result._event_queue.put_nowait("synthetic-event")
        self.iterator = self.result.stream_events()
        self.assertEqual(await anext(self.iterator), "synthetic-event")

    def record(self, name):
        OBSERVATIONS.append({
            "case": name,
            "cancel_mode": self.result._cancel_mode,
            "producer_done": self.result.run_loop_task.done(),
            "producer_cancellation_requested": bool(self.result.run_loop_task.cancelling()),
            "active_consumers": self.result._active_stream_consumers,
            "producer_finally_observed": self.settled.is_set(),
        })

    async def test_normal_exhaustion(self):
        await self.prime()
        self.release.set()
        self.assertEqual([event async for event in self.iterator], [])
        self.assertTrue(self.settled.is_set())
        self.assertEqual(self.result._active_stream_consumers, 0)
        self.assertIsNone(self.result._cancel_mode)
        self.record("normal exhaustion")

    async def test_cancel_during_queue_wait(self):
        entered = asyncio.Event()

        async def consume():
            entered.set()
            self.iterator = self.result.stream_events()
            async for event in self.iterator:
                pass

        task = asyncio.create_task(consume())
        self.child_tasks.append(task)
        await asyncio.wait_for(entered.wait(), 2)
        self.assertTrue(self.result._waiting_on_event_queue)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        await asyncio.gather(self.result.run_loop_task, return_exceptions=True)
        self.assertEqual(self.result._cancel_mode, "immediate")
        self.assertTrue(self.result.run_loop_task.cancelled())
        self.record("consumer cancelled in queue wait")

    async def consumer_exits_in_body(self, cancellation):
        handling = asyncio.Event()
        hold = asyncio.Event()
        self.result._event_queue.put_nowait("synthetic-event")
        self.iterator = self.result.stream_events()

        async def consume():
            async for event in self.iterator:
                handling.set()
                if cancellation:
                    await hold.wait()
                else:
                    raise ConnectionError("synthetic downstream failure")

        task = asyncio.create_task(consume())
        self.child_tasks.append(task)
        await asyncio.wait_for(handling.wait(), 2)
        if cancellation:
            task.cancel()
        with self.assertRaises(asyncio.CancelledError if cancellation else ConnectionError):
            await task
        # Flush the registered task-done callback, without a wall-clock delay.
        await asyncio.sleep(0)
        self.assertEqual(self.result._active_stream_consumers, 0)
        self.assertFalse(self.result.run_loop_task.done())
        self.assertFalse(self.result.run_loop_task.cancelling())
        self.assertIsNone(self.result._cancel_mode)
        self.record("consumer cancelled in body" if cancellation else "consumer raises in body")

    async def test_cancel_in_body_does_not_cancel_producer(self):
        await self.consumer_exits_in_body(True)

    async def test_raise_in_body_does_not_cancel_producer(self):
        await self.consumer_exits_in_body(False)

    async def test_close_without_cancel_waits_for_producer(self):
        await self.prime()
        closer = asyncio.create_task(self.iterator.aclose())
        self.child_tasks.append(closer)
        # The close task runs to its first suspension, awaiting the producer.
        await asyncio.sleep(0)
        self.assertFalse(closer.done())
        self.assertEqual(self.result._active_stream_consumers, 0)
        self.assertFalse(self.result.run_loop_task.cancelling())
        self.record("explicit close before producer release")
        self.release.set()
        await asyncio.wait_for(closer, 2)
        self.assertTrue(self.settled.is_set())

    async def test_explicit_cancel_then_close_settles_producer(self):
        await self.prime()
        self.result.cancel()
        await asyncio.wait_for(self.iterator.aclose(), 2)
        self.assertTrue(self.result.run_loop_task.cancelled())
        self.assertTrue(self.settled.is_set())
        self.assertEqual(self.result._active_stream_consumers, 0)
        self.record("explicit cancel then close")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OwnershipProbe)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "upstream_revision": "9abc9182d06dbd28330af888306031269d57a175",
        "methods_executed_unmodified": sorted(METHODS),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "observations": OBSERVATIONS,
        "limits": [
            "Source-method harness, not full SDK import or Runner integration.",
            "Synthetic producer and queues; no model, tool, provider, billing, tracing or sandbox execution.",
            "Error and provider/sandbox cleanup boundaries are stubbed; full lifecycle safety is unverified.",
            "Existing issue 5386 is independently authored; this is corroboration, not a new discovery.",
        ],
    }
    (ROOT / "SOURCE_PROBE_REPLAY.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)
