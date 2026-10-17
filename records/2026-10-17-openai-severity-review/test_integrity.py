"""Synthetic runner regressions. No shell commands or model API requests are made."""
from __future__ import annotations

import copy
import json
import unittest

from agents import Agent, RunConfig, Runner, RunState, function_tool
from agents.exceptions import ModelBehaviorError
from agents.items import ToolCallOutputItem
from agents.testing import ModelStep, ScriptedModel, assistant_message, function_call
from agents.tool import ShellCallOutcome, ShellCommandOutput, ShellResult, ShellTool
from openai.types.responses import (
    Response, ResponseCompletedEvent, ResponseFunctionShellToolCall,
    ResponseOutputItemDoneEvent,
)


async def run_agent(agent, data, mode):
    config = RunConfig(tracing_disabled=True)
    if mode == "stream":
        result = Runner.run_streamed(agent, data, max_turns=6, run_config=config)
        async for _ in result.stream_events():
            pass
        return result
    return await Runner.run(agent, data, max_turns=6, run_config=config)


class ApprovalControls(unittest.IsolatedAsyncioTestCase):
    async def scenario(self, mode, case):
        executed = []

        @function_tool(needs_approval=True)
        async def record(value: int) -> str:
            """Record a synthetic value in memory."""
            executed.append(value)
            return "recorded"

        @function_tool
        async def permitted_sibling(value: int) -> str:
            """Record a permitted synthetic sibling action in memory."""
            executed.append(value)
            return "recorded"

        steps = [[function_call("record", {"value": 1}, call_id="approved-id")]]
        if case == "changed_id_with_sibling":
            steps.append([
                function_call("record", {"value": 2}, call_id="approved-id"),
                function_call("permitted_sibling", {"value": 3}, call_id="sibling-id"),
            ])
        steps.append([assistant_message("finished")])
        model = ScriptedModel(steps)
        agent = Agent(name="approval-controls", model=model, tools=[record, permitted_sibling])
        paused = await run_agent(agent, "synthetic input", mode)
        self.assertEqual(executed, [])
        self.assertEqual(len(paused.interruptions), 1)
        self.assertEqual(len(model.calls), 1)
        if case == "pause_without_permission":
            return
        state = paused.to_state()
        if case == "reject":
            state.reject(paused.interruptions[0])
        else:
            state.approve(paused.interruptions[0])
        # Real JSON round-trip at the supported trusted-storage boundary.
        # This does not claim that from_json authenticates untrusted state.
        state = await RunState.from_json(agent, json.loads(json.dumps(state.to_json())))
        if case == "changed_id_with_sibling":
            with self.assertRaises(ModelBehaviorError):
                await run_agent(agent, state, mode)
            self.assertEqual(executed, [1])
        else:
            completed = await run_agent(agent, state, mode)
            self.assertEqual(completed.final_output, "finished")
            self.assertEqual(executed, [] if case == "reject" else [1])
            self.assertEqual(completed.interruptions, [])
            model.assert_complete()


def shell_call(*, cap=None):
    action = {"type": "shell_command", "commands": ["synthetic-no-execution"]}
    if cap is not None:
        action["max_output_length"] = cap
    return ResponseFunctionShellToolCall(
        id="shell-id", call_id="shell-call", type="shell_call", action=action,
        status="completed",
    )


class ShellIntegrity(unittest.IsolatedAsyncioTestCase):
    async def scenario(self, mode, case):
        executed = []
        cap = None
        if case == "empty":
            value = ShellResult(output=[])
            expected = []
        elif case == "empty_with_metadata":
            cap = 9
            value = ShellResult(output=[], max_output_length=4, provider_data={"label": "synthetic"})
            expected = []
        elif case == "quiet_success":
            value = ShellResult(output=[ShellCommandOutput(outcome=ShellCallOutcome(type="exit", exit_code=0))])
            expected = [{"stdout": "", "stderr": "", "outcome": {"type": "exit", "exit_code": 0}}]
        elif case == "unknown_exit":
            value = ShellResult(output=[ShellCommandOutput()])
            expected = [{"stdout": "", "stderr": "", "outcome": {"type": "exit", "exit_code": None}}]
        elif case == "failure":
            value = ShellResult(output=[ShellCommandOutput(stdout="partial", stderr="failed", outcome=ShellCallOutcome(type="exit", exit_code=7))])
            expected = [{"stdout": "partial", "stderr": "failed", "outcome": {"type": "exit", "exit_code": 7}}]
        elif case == "timeout":
            value = ShellResult(output=[ShellCommandOutput(stderr="timeout", outcome=ShellCallOutcome(type="timeout"))])
            expected = [{"stdout": "", "stderr": "timeout", "outcome": {"type": "timeout"}}]
        elif case == "multiple":
            value = ShellResult(output=[ShellCommandOutput(stdout="one"), ShellCommandOutput(stdout="two")])
            expected = [{"stdout": x, "stderr": "", "outcome": {"type": "exit", "exit_code": None}} for x in ("one", "two")]
        elif case == "plain_empty":
            value = ""
            expected = []
        elif case == "zero_limit":
            cap = 0
            value = ShellResult(output=[])
            expected = []
        elif case == "executor_exception":
            value = RuntimeError("synthetic executor failure")
            expected = [{"stdout": "synthetic executor failure", "stderr": "", "outcome": {"type": "exit", "exit_code": 1}}]
        elif case == "literal_placeholder":
            value = "(no output)"
            expected = [{"stdout": "(no output)", "stderr": "", "outcome": {"type": "exit", "exit_code": 0}}]
        elif case == "rejected":
            value = ShellResult(output=[])
            expected = None
        else:
            raise AssertionError(case)

        original = copy.deepcopy(value)

        async def synthetic_executor(request):
            executed.append(request.data.call_id)
            if isinstance(value, Exception):
                raise value
            return value

        call = shell_call(cap=cap)
        first_step = [call]
        if mode == "stream":
            # Shell calls require explicit normalized events in ScriptedModel.
            response = Response(
                id="synthetic-response", created_at=0, model="synthetic",
                object="response", output=[call], tool_choice="auto", tools=[],
                parallel_tool_calls=True,
            )
            first_step = ModelStep.stream([
                ResponseOutputItemDoneEvent(type="response.output_item.done", sequence_number=0, output_index=0, item=call),
                ResponseCompletedEvent(type="response.completed", sequence_number=1, response=response),
            ], output=[call])
        model = ScriptedModel([first_step, [assistant_message("finished")]])
        agent = Agent(name="shell-integrity", model=model, tools=[
            ShellTool(executor=synthetic_executor, needs_approval=(case == "rejected"))
        ])
        result = await run_agent(agent, "synthetic input", mode)
        if case == "rejected":
            self.assertEqual(executed, [])
            self.assertEqual(len(result.interruptions), 1)
            state = result.to_state()
            state.reject(result.interruptions[0])
            result = await run_agent(agent, state, mode)
            self.assertEqual(executed, [])
            self.assertEqual(result.final_output, "finished")
            return

        self.assertEqual(executed, ["shell-call"])
        if not isinstance(value, Exception):
            self.assertEqual(value, original)
        outputs = [x for x in result.new_items if isinstance(x, ToolCallOutputItem)]
        self.assertEqual(len(outputs), 1)
        item = outputs[0]
        self.assertEqual(item.raw_item["output"], expected)
        self.assertEqual(item.to_input_item()["output"], expected)
        replayed = [x for x in model.last_call.input if x.get("type") == "shell_call_output"]
        self.assertEqual(len(replayed), 1)
        self.assertEqual(replayed[0]["output"], expected)
        if expected == []:
            self.assertNotIn("shell_output", item.raw_item)
        if case == "empty_with_metadata":
            self.assertEqual(item.raw_item["provider_data"], {"label": "synthetic"})
            self.assertEqual(item.raw_item["max_output_length"], 4)
        if case == "zero_limit":
            self.assertEqual(item.raw_item["max_output_length"], 0)
        if case == "executor_exception":
            self.assertEqual(item.raw_item["status"], "failed")
        if case in ("empty", "empty_with_metadata"):
            self.assertEqual(item.output, "(no output)" if case == "empty" else "(no ")
        self.assertEqual(result.final_output, "finished")
        model.assert_complete()


def install_cases(cls, cases):
    for mode in ("run", "stream"):
        for case in cases:
            async def test(self, selected_mode=mode, selected_case=case):
                await self.scenario(selected_mode, selected_case)
            setattr(cls, f"test_{mode}_{case}", test)


install_cases(ApprovalControls, ("pause_without_permission", "reject", "approved_json_resume", "changed_id_with_sibling"))
install_cases(ShellIntegrity, ("empty", "empty_with_metadata", "quiet_success", "unknown_exit", "failure", "timeout", "multiple", "plain_empty", "literal_placeholder", "rejected", "zero_limit", "executor_exception"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
