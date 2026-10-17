"""Offline integration checks against the released Agents SDK; no API calls."""

from __future__ import annotations

import asyncio
import unittest

from agents import Agent, RunConfig, Runner
from agents.decorators import tool
from agents.testing import ScriptedModel, assistant_message, function_call

from owned_stream import owned_stream


class StreamIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.results = []
        self.tasks = []
        self.releases = []

    async def asyncTearDown(self):
        for release in self.releases:
            release.set()
        for result in self.results:
            if not result.is_complete:
                result.cancel()
            try:
                async with asyncio.timeout(3):
                    async for _ in result.stream_events():
                        pass
            except Exception:
                pass
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    def run_result(self, model, tools=()):
        result = Runner.run_streamed(
            Agent(name="offline-ownership-test", model=model, tools=list(tools)),
            "synthetic input",
            run_config=RunConfig(tracing_disabled=True),
        )
        self.results.append(result)
        return result

    async def blocked_tool(self, delayed_cleanup=False):
        started = asyncio.Event()
        release = asyncio.Event()
        cleanup_started = asyncio.Event()
        cleanup_release = asyncio.Event()
        settled = asyncio.Event()
        self.releases.extend([release, cleanup_release])

        @tool
        async def controlled_work() -> str:
            """Run a synthetic cancellable operation."""
            started.set()
            try:
                await release.wait()
                return "synthetic success"
            finally:
                cleanup_started.set()
                if delayed_cleanup:
                    await cleanup_release.wait()
                settled.set()

        model = ScriptedModel([
            [function_call("controlled_work", {}, call_id="synthetic-call")],
            [assistant_message("done")],
        ])
        result = self.run_result(model, [controlled_work])
        await asyncio.wait_for(started.wait(), 3)
        return result, cleanup_started, cleanup_release, settled

    def assert_settled(self, result, settled):
        self.assertTrue(result.is_complete)
        self.assertTrue(settled.is_set())
        self.assertTrue(result.run_loop_task.done())

    async def test_normal_completion_preserves_output(self):
        result = self.run_result(ScriptedModel([[assistant_message("done")]]))
        async with owned_stream(result) as events:
            observed = [event async for event in events]
        self.assertTrue(observed)
        self.assertEqual(result.final_output, "done")
        self.assertTrue(result.run_loop_task.done())

    async def test_break_after_event_stops_and_settles_tool(self):
        result, _, _, settled = await self.blocked_tool()
        async with owned_stream(result) as events:
            async for _ in events:
                break
        self.assert_settled(result, settled)

    async def test_exit_before_first_event_settles_tool(self):
        result, _, _, settled = await self.blocked_tool()
        async with owned_stream(result):
            pass
        self.assert_settled(result, settled)

    async def test_body_failure_is_preserved_after_cleanup(self):
        result, _, _, settled = await self.blocked_tool()
        expected = ConnectionError("synthetic downstream failure")
        with self.assertRaises(ConnectionError) as caught:
            async with owned_stream(result) as events:
                async for _ in events:
                    raise expected
        self.assertIs(caught.exception, expected)
        self.assert_settled(result, settled)

    async def test_cancel_in_body_settles_tool_before_propagating(self):
        result, _, _, settled = await self.blocked_tool()
        handling = asyncio.Event()
        hold = asyncio.Event()

        async def consume():
            async with owned_stream(result) as events:
                async for _ in events:
                    handling.set()
                    await hold.wait()

        consumer = asyncio.create_task(consume())
        self.tasks.append(consumer)
        await asyncio.wait_for(handling.wait(), 3)
        consumer.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await consumer
        self.assert_settled(result, settled)

    async def test_cancel_during_next_event_wait_settles_tool(self):
        result, _, _, settled = await self.blocked_tool()
        waiting = asyncio.Event()

        async def consume():
            async with owned_stream(result) as events:
                async for _ in events:
                    waiting.set()

        consumer = asyncio.create_task(consume())
        self.tasks.append(consumer)
        await asyncio.wait_for(waiting.wait(), 3)
        # Let finite queued events drain so cancellation reaches the source wait.
        async with asyncio.timeout(3):
            while not result._waiting_on_event_queue:
                await asyncio.sleep(0)
        consumer.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await consumer
        self.assert_settled(result, settled)

    async def test_repeated_cancellation_does_not_abandon_cleanup(self):
        result, cleanup_started, cleanup_release, settled = await self.blocked_tool(True)

        async def consume():
            async with owned_stream(result) as events:
                async for _ in events:
                    break

        consumer = asyncio.create_task(consume())
        self.tasks.append(consumer)
        await asyncio.wait_for(cleanup_started.wait(), 3)
        consumer.cancel()
        await asyncio.sleep(0)
        consumer.cancel()
        await asyncio.sleep(0)
        self.assertFalse(consumer.done())
        self.assertFalse(settled.is_set())
        cleanup_release.set()
        with self.assertRaises(asyncio.CancelledError):
            await consumer
        self.assert_settled(result, settled)

    async def test_error_with_late_cancellation_retains_original_error(self):
        result, cleanup_started, cleanup_release, settled = await self.blocked_tool(True)
        expected = ConnectionError("synthetic downstream failure")

        async def consume():
            async with owned_stream(result) as events:
                async for _ in events:
                    raise expected

        consumer = asyncio.create_task(consume())
        self.tasks.append(consumer)
        await asyncio.wait_for(cleanup_started.wait(), 3)
        consumer.cancel()
        await asyncio.sleep(0)
        cleanup_release.set()
        with self.assertRaises(ConnectionError) as caught:
            await consumer
        self.assertIs(caught.exception, expected)
        self.assert_settled(result, settled)


class CleanupFailureContract(unittest.IsolatedAsyncioTestCase):
    async def test_cleanup_failure_preserves_original_without_payload_note(self):
        class FailedResult:
            is_complete = False

            def cancel(self):
                self.is_complete = True

            async def stream_events(self):
                yield "synthetic event"
                raise RuntimeError("synthetic private cleanup payload")

        expected = ValueError("synthetic body failure")
        with self.assertRaises(ValueError) as caught:
            async with owned_stream(FailedResult()) as events:
                async for _ in events:
                    raise expected
        self.assertIs(caught.exception, expected)
        self.assertIn("RuntimeError", " ".join(expected.__notes__))
        self.assertNotIn("private cleanup payload", " ".join(expected.__notes__))

    async def test_cleanup_failure_without_body_error_is_visible(self):
        class FailedResult:
            is_complete = False

            def cancel(self):
                self.is_complete = True

            async def stream_events(self):
                yield "synthetic event"
                raise RuntimeError("synthetic cleanup failure")

        with self.assertRaisesRegex(RuntimeError, "synthetic cleanup failure"):
            async with owned_stream(FailedResult()) as events:
                async for _ in events:
                    break


if __name__ == "__main__":
    unittest.main(verbosity=2)
