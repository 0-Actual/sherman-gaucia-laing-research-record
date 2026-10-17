"""Run the synthetic checks against the installed baseline or an isolated candidate.

Candidate mode replaces a class only within this single test process. It makes no
changes to site-packages and is not an application integration or deployment tool.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import types
import unittest
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from agents import set_tracing_disabled
from agents.run_internal import tool_actions

import test_integrity

BASE_SHA256 = "d7c5000ce55675eb016c0cf53fd89c3cc0d40d66cc7f86459c14a60d40238d70"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--output", default="evaluation.json")
    args = parser.parse_args()
    set_tracing_disabled(True)
    root = Path(__file__).resolve().parent
    source_bytes = Path(tool_actions.__file__).read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != BASE_SHA256:
        raise SystemExit("This evaluation requires the exact documented baseline tool_actions.py.")
    started = datetime.now(timezone.utc).isoformat()
    with ExitStack() as scope:
        if args.candidate:
            candidate = root / "candidate_tool_actions.py"
            module = types.ModuleType("agents.run_internal._priority_zero_shell_evaluation")
            module.__package__ = "agents.run_internal"
            module.__file__ = str(candidate)
            exec(compile(candidate.read_bytes(), str(candidate), "exec"), module.__dict__)
            scope.enter_context(patch.object(tool_actions, "ShellAction", module.ShellAction))
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_integrity)
        outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    data = {
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "isolated_candidate" if args.candidate else "installed_baseline",
        "python": platform.python_version(), "platform": sys.platform,
        "sdk_version": importlib.metadata.version("openai-agents"),
        "baseline_sha256": BASE_SHA256,
        "test_sha256": hashlib.sha256((root / "test_integrity.py").read_bytes()).hexdigest(),
        "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256((root / "candidate_tool_actions.py").read_bytes()).hexdigest() if args.candidate else None,
        "tests_run": outcome.testsRun,
        "failed_tests": [case.id() for case, _ in outcome.failures],
        "error_tests": [case.id() for case, _ in outcome.errors],
        "skipped_tests": [case.id() for case, _ in outcome.skipped],
        "passed": outcome.wasSuccessful(),
        "live_model_requests": False, "real_shell_commands": False,
        "installed_files_changed": False,
    }
    Path(args.output).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if outcome.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
