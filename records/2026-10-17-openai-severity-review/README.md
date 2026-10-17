# OpenAI Agents SDK: approval controls and faithful shell results

Sherman G. Laing / Quantum.Earth.Laing. Prepared with ChatGPT/Codex assistance under the owner's direction. October 17, 2026. This study continues the [stream ownership assessment](../2026-10-17-openai-stream-ownership/README.md).

The owner requested severity-first review: check authorization and side effects before silent result corruption, explicit availability failures, performance and typing. This edition supplies a bounded approval regression review and a reproducible correction for an already reported shell-output integrity defect. It is not an audit of every OpenAI repository or a claim that every severe issue has been found.

## Result

Against Agents SDK **0.24.0**, the final 32-case baseline has **28 passes and four failures**. The failures reproduce empty structured shell results turning into invented stdout and a zero exit code. With the isolated one-line candidate correction, **32 cases pass**: eight approval/state checks and 24 shell-result checks, covering normal and streamed execution. See [baseline evidence](BASELINE_RESULTS.json) and [candidate evidence](CANDIDATE_RESULTS.json), which bind the tested source files by SHA-256.

The eight approval checks verify pause before execution, rejection without execution, approved execution after a trusted JSON state round-trip, and rejection of changed arguments under a reused call ID before a separately permitted sibling can run. They found no defect in these selected scenarios. They do not establish that all authorization, sandbox, credential or persistence controls are secure.

The shell correction keeps an empty structured result empty. It preserves genuine quiet success, unknown exit status, nonzero exit codes, timeouts, output order, plain strings, explicit zero output limits, executor exceptions, metadata and shell approval rejection in the tested cases. The existing human-display placeholder is retained in its display channel. The next synthetic model request receives the corrected structured output.

## Reproduce

Use a clean virtual environment with Python 3.12. Install [requirements.txt](requirements.txt). The recorded environment is Windows/Python 3.12.14; exact installed dependency versions are retained in [requirements-tested-windows.txt](requirements-tested-windows.txt). No API key or paid model call is needed. The executors change only an in-memory list; they never run the synthetic command string as a real shell command. Tracing is disabled.

```text
python -m pip install -r requirements.txt
python evaluate.py --output local-baseline.json
python evaluate.py --candidate --output local-candidate.json
```

The first command that runs tests is expected to exit **1** with exactly the four documented empty-result assertion failures. The candidate is expected to exit **0** with all 32 cases passing. Installation/environment errors or additional failures are not the expected reproduction and must be investigated separately. Baseline and candidate use the same tests and handwritten expected outcomes.

The evaluator refuses a different installed `tool_actions.py` byte identity. This prevents silently testing a different SDK revision. Candidate mode loads [candidate_tool_actions.py](candidate_tool_actions.py) and replaces one class only inside the test process, restoring it afterward. It does not edit the installed SDK, change an application, deploy a service or repair OpenAI's public repository. This isolated replacement is evaluation machinery, not a supported production extension point.

For source review, [empty_structured_shell.diff](empty_structured_shell.diff) shows the complete one-line change against the pinned upstream source. A deployment would require an application-specific review and testing of a patched SDK build. A documented existing alternative is to return an explicit `ShellCommandOutput` with the actual known command outcome, including empty stdout/stderr when appropriate. Do not invent an exit status merely to avoid the defect; an empty result alone does not prove success.

## Evidence, credit and limits

Pinned upstream main: [`9abc9182d06dbd28330af888306031269d57a175`](https://github.com/openai/openai-agents-python/tree/9abc9182d06dbd28330af888306031269d57a175). The installed `tool_actions.py` is byte-identical to that pinned source. The existing defect was reported by **BlueX888** in [issue 5348](https://github.com/openai/openai-agents-python/issues/5348); the maintainer acknowledged its mechanism, and `zhgao` posted a related fork proposal. We credit those records and do not claim discovery of this defect or the general fix direction. The reporter explicitly described a scripted reproduction, not a known production incident.

The copied/modified SDK implementation and its patch retain OpenAI's MIT license. Original test/evaluation material and original explanatory material use the owner's unchanged noncommercial license, to the extent of rights controlled by the owner. Read [LICENSE-SCOPE.md](LICENSE-SCOPE.md). No upstream submission, new contributor agreement, maintainer acceptance, endorsement, compensation or ownership of independent work is implied.

Read [FINDINGS.md](FINDINGS.md) for the invariant and cause, and [REVIEW_QUEUE.md](REVIEW_QUEUE.md) for the ranked remaining work. This edition runs synthetic models and checks in-memory output/state. It does not test live providers, actual shell processes, billing, external databases, distributed storage, every tracing path, other operating systems or the full upstream suite. Its JSON round-trip uses trusted application state; the SDK does not authenticate arbitrary user-supplied state. Successful tests are bounded evidence, not certification.

## Preserved development mistakes

The initial Windows async test loop was blocked by the chat's network restriction before SDK execution. Runtime access was then granted for the local loop. The first shell fixture incorrectly relied on automatic `ScriptedModel` shell streaming: ten stream cases failed in the fixture before reaching the shell executor. It was corrected to provide explicit supported stream events. The first sibling check required approval for the sibling, weakening its evidence about preflight ordering; the final test uses a separately permitted sibling. Early logs and source variants remain in the private review record. Final results above use the corrected fixture and stronger check; the earlier counts are not additional distinct tests.
