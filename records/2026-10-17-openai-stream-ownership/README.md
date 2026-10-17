# Priority Zero — explicit ownership of streamed agent runs

Sherman G. Laing / Quantum.Earth.Laing · October 17, 2026 · Prepared with ChatGPT/Codex assistance.

This packet contains an optional application wrapper for the OpenAI Agents Python SDK. When its single consumer exits early, the wrapper requests cancellation and waits for the SDK's cleanup path. Normal completion preserves the final output. The implementation, tests and evidence are published here for noncommercial research and evaluation under the project's existing license, with third-party rights retained separately.

This addresses the scenario in the existing report [openai/openai-agents-python#5386](https://github.com/openai/openai-agents-python/issues/5386), opened by `sushantsimpplr`. It is corroboration and an application-level remedy, not a claim to have discovered that issue or an accepted OpenAI patch. OpenAI's repository is unchanged.

## Use

Python 3.11 or newer is required by this packet. Validation used Python 3.12.14 on Windows and `openai-agents==0.24.0`. Install the SDK separately and put `owned_stream.py` beside your research application:

```python
from agents import Runner
from owned_stream import owned_stream

result = Runner.run_streamed(your_agent, "your research input")
async with owned_stream(result) as events:
    async for event in events:
        await process_event(event)
        if should_stop():
            break
# The context has passed through its cleanup boundary before returning.
```

The names `your_agent`, `process_event` and `should_stop` represent your application. This snippet is illustrative; the test file below supplies complete runnable examples without a model service or API key. Use the wrapper around exactly one consumer. Do not share its result with another simultaneous stream reader or start consumption outside the context. Leaving early intentionally requests immediate cancellation. To use the SDK's after-turn cancellation, continue reading until exhaustion rather than breaking from the context.

## Reproduce

In a fresh environment, from this directory:

```text
python -m pip install --only-binary=:all: -r requirements.txt
python -B test_owned_stream.py
python -B probe_source.py
```

`requirements.txt` pins the SDK version. For the exact tested Windows dependency set, use `requirements-tested-windows.txt` instead. That complete Windows lock includes platform-specific packages and is not claimed to install unchanged on other operating systems. Package installation requires network access; the tests use `ScriptedModel`, synthetic tools and disabled tracing, with no live model calls or API credentials.

The final adapter suite passed **10 cases: 8 against the installed SDK and 2 protocol-level cleanup-error cases**. A separate **6-case source-method probe** corroborated cancellation behavior in a pinned main-branch source file. That probe compiles selected unchanged method bodies into a small harness; it is not a full SDK integration run. These counts describe test cases, not research discoveries. Results and exact versions are in [VALIDATION.json](VALIDATION.json) and [SOURCE_PROBE_RESULTS.json](SOURCE_PROBE_RESULTS.json).

## Read the evidence

- [FINDINGS.md](FINDINGS.md): purpose, state invariant, counterexamples, cause, remedy and limits.
- [owned_stream.py](owned_stream.py): original optional wrapper using public SDK APIs.
- [test_owned_stream.py](test_owned_stream.py): reproducible integration and protocol checks.
- [probe_source.py](probe_source.py): method-level baseline probe; writes a new `SOURCE_PROBE_REPLAY.json` without replacing the retained result.
- [upstream_result.py](upstream_result.py): exact pinned upstream source for that probe, under [OpenAI's MIT license](UPSTREAM_LICENSE.txt).
- [LICENSE-SCOPE.md](LICENSE-SCOPE.md): attribution and the separation of original additions from third-party material.
- [CHANGELOG.md](CHANGELOG.md): development and correction history, including unsuccessful setup attempts.
- [MANIFEST.json](MANIFEST.json): file sizes and SHA-256 identities for the published payload.

## Limits

Cancellation is cooperative. The wrapper cannot forcibly stop a tool that suppresses cancellation, undo completed side effects, provide a sandbox, or guarantee a bounded shutdown time. Waiting for cleanup can take as long as the underlying operation requires. Exception notes added by the wrapper name only secondary error types; this is not general redaction of application exceptions or logs.

No live model billing, real transport, external storage, real sandbox, GPU or physical quantum execution was tested. The full upstream suite and other platforms were not run. There was a focused self-review, not an independent peer certification. No new contributor agreement, upstream submission, commercial license or compensation is established by this publication.
