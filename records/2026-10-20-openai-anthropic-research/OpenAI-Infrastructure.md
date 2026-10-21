> This is a preview of the archive README. Relative links below refer to files inside the corresponding ZIP after extraction.

# OpenAI Agents Python: patches, regression coverage and bounded research

Prepared October 20, 2026 by Sherman G. Laing with disclosed Codex assistance. This technical edition contains completed source, tests and recorded results. It combines the previously published shell/stream contributions with later candidate and verification work. It is research disclosure, not an SDK release, maintainer acceptance, production validation or certification.

The later source baseline is `openai/openai-agents-python` revision `64cd5dfc5a1579870dcbed0ea42b27aa84033fee`. The original shell/stream checks used `openai-agents==0.24.0`, Python 3.12.14 on Windows. The original records and frozen local packages are preserved separately; this edition removes private filesystem and environment identifiers from labelled derivative evidence. See [SANITIZATION.md](SANITIZATION.md) and [source-copy provenance](provenance/SOURCE-COPIES.json).

## Contributions and their scope

**Empty structured shell output — issue #5348.** `None` means no structured payload; `[]` is a supplied structured payload with no entries. A truthiness check treated both as absent and turned the human display placeholder `"(no output)"` into fabricated structured stdout. The one-line `is not None` correction preserves `output: []` while leaving display rendering and the existing execution/approval paths intact. Empty entries do not establish a successful command exit. This is a representation distinction, not a binary-arithmetic change.

The [published shell contribution](https://github.com/openai/openai-agents-python/issues/5348#issuecomment-6297534362) includes the correction and complete 32-case suite. Its additional value is regression coverage, not original discovery: credit belongs to reporter BlueX888, maintainer jbeckwith-oai, zhgao's prior proposal, and other participants. [released/shell](released/shell) contains the exact contribution code. The later pinned-source patch is [followup/patches/5348-empty-shell-output.patch](followup/patches/5348-empty-shell-output.patch).

**Opt-in stream ownership — issue #5386.** The [published helper and tests](https://github.com/openai/openai-agents-python/issues/5386#issuecomment-6297538696) give one consumer explicit responsibility for requesting cancellation and waiting for cleanup on early exit. Normal exhaustion does not request cancellation. The helper uses public APIs and preserves the SDK's intentional abandoned-consumer behavior outside this opt-in context. It does not reverse completed effects, impose a timeout or force uncooperative tools/providers to stop. Credit remains with the original issue's reporters and prior lifecycle discussion. The exact helper and ten-case suite are in [released/stream](released/stream); [additional failure-path checks](followup/checks/test_stream_failure_paths.py) exercise model errors, wrapped tool errors/finalizers, turn limits and a blocking input guardrail.

**Experimental replay candidate — issue #5342.** The [candidate patch](followup/patches/5342-history-replay.patch) and [final 13-case test source](followup/tests/models/test_history_replay_regression.py) address manually supplied Responses-format histories containing a pending call and multiple text/refusal messages before matching results. They keep those messages together with the pending calls, preserve covered reasoning/signature/ID/input boundaries, and separate later turns.

This candidate does **not** answer the [maintainer's originating-workflow request](https://github.com/openai/openai-agents-python/issues/5342#issuecomment-6153988440). Built-in Chat Completions ordinary/streamed producers emit one output message per turn. The tests construct the disputed history and fake the provider transport; no real producer, live HTTP 400 or production impact was established. Concatenating refusals across messages also remains an intended-contract question: existing handling retains the last refusal part inside one message. Timotty, Ayushraj06-bit and zhgao already proposed the same-turn text merge; our additional material is broader coverage and the explicit two-refusal candidate. Publication does not resolve these questions or make the candidate ready to merge.

**Redis and repeated-history characterization.** Existing Redis session tests were checked without a new Redis implementation. The [operation-count probe](followup/checks/performance_probe.py) measures repeated historical invocation canonicalization in one synthetic workload; it implements no optimization.

## Recorded results

Rows name different, overlapping populations. Do not add them into a unique-test total. No SDK test was executed while preparing this edition.

| Population or attempt | Recorded result | Evidence |
|---|---|---|
| Released shell suite, baseline | 32 tests: 28 pass, four fail | `released/evidence/shell-baseline.txt` |
| Released shell suite, process-local candidate | 32 pass; installed source unchanged | `released/evidence/shell-corrected.txt`, `VALIDATION-20261020.json` |
| Stream helper deliberately omitted | One expected negative-control failure | `released/evidence/stream-negative-control.txt` |
| Restored published stream helper | Ten pass | `released/evidence/stream-corrected.txt` |
| Initial history loading attempt | Import failure for `pywintypes`, return code 4; no test verdict | `followup/evidence/history-baseline.*` |
| Pinned baseline, initial history file | 11 regression cases fail | `followup/evidence/history-baseline-runtime-fixed.*` |
| Corrected runtime with initial 11-case file | 169 focused tests pass | `followup/evidence/corrected-upstream-focused.*` |
| Final history file, two reasoning cases added | 13 pass | `followup/evidence/history-reasoning-boundary.*` |
| Unchanged published shell suite against corrected pinned source | 32 pass | `followup/evidence/published-shell-current-main.*` |
| Initial expanded stream check | Two fail, 12 pass; test expectations were wrong | `followup/evidence/stream-current-main-failures.*` |
| Corrected expanded stream checks plus published suite | 14 tests pass, two subtests pass, reported separately | `followup/evidence/stream-current-main-corrected-checks.*` |
| Existing Redis session tests | 106 pass, four real-server routes skipped | `followup/evidence/redis-current-contract.*`, `provenance/REDIS-SCOPE.json` |
| First genuine-checkout history invocation | Assertions print 13 passed; process exits 1 during temporary-directory cleanup | `verification/initial-attempt/` |
| Workspace-temporary-directory retry, same pytest plugins | 13 passed in 7.42 seconds; exit 0; zero-byte stderr; all three candidate hashes unchanged | `verification/workspace-temp-retry/` |

The two expanded-stream harness corrections were to check an empty recorded-call collection without assuming a list instead of a tuple, and to inspect the original tool exception through the SDK's `UserError` cause. The SDK and helper were not changed to satisfy those checks. Both attempts remain included.

The history-count probe records 55, 210 and 820 historical canonicalizations at 10, 20 and 40 turns respectively, for each of ordinary and streamed modes. These counts follow `n(n+1)/2` in the supplied scenario. They are not elapsed-time, cost, general scaling or speedup measurements. Results are in `followup/evidence/history-fingerprint-counts.json`.

The quiet Redis log supplies the total of four skips; inspection of the pinned tests supplies the specific real-server-route mapping. No live Redis server or Redis Cluster write support is established.

## Source, review and reproduction boundaries

The initial work used a source archive. A later genuine Git checkout used the same pin, and the final three candidate hashes matched the review manifest. Two agents' reviews of two revisions are retained under `followup/review/`. Later independent origin/refusal assessments are in `verification/`. These are bounded semantic records, not strict clean-review receipts. Historical recommendations to keep work local explain the earlier decision; the current edition discloses it as candidate research while preserving the unresolved technical questions. The strict final-review protocol and complete final SDK verification stack remain incomplete.

For the original released-package reproduction, copy `released/` into a scratch directory, provide Python 3.12 and the listed dependencies, and inspect `run_checks.py` before running it. That harness verifies an exact installed source hash and replaces one class only inside its test process. It writes its own logs and receipt. The captured Windows dependency list describes the recorded environment; it is not a cross-platform lockfile.

For the later tests, obtain the pinned upstream source and compatible development dependencies. Apply only the issue-specific candidate patch being evaluated, place the history regression under the checkout's `tests/models/` when appropriate, and run the relevant focused checks. Do not apply both the combined review diff and separate patches. The combined review diffs are historical review snapshots, not additional changes.

The expanded stream check is an unchanged byte copy with its historical relative-layout import. Make this edition's `released/stream` and the pinned SDK's `src` importable through `PYTHONPATH`; the test can then import the unchanged helper. Its old path insertion is retained for evidence identity. The performance probe also requires the pinned SDK source. `provenance/run_focused.py` and `verification/focused_temp_retry.py` preserve historical capture procedures; they assume their original layout and are not portable package launchers. Sanitized path placeholders are not executable locations.

An earlier environment bootstrap issue was recorded in the work plan without a separate command log; no receipt is invented for it. Raw virtual environments, `.pth` configuration, private progress records, caches, source archives and unrelated personal/governance material are excluded. The recorded environment was not sealed into a reproducible image. Synthetic models/transports and disabled tracing avoid paid model requests in these checks; the records do not validate live providers or all cancellation schedules.

## Licensing and integrity

Contribution copies retain the existing [MIT license](LICENSE), Sherman G. Laing attribution, and upstream-derived patch attribution. The separate [upstream MIT license](UPSTREAM-LICENSE) is preserved. This does not relicense unrelated work or imply OpenAI endorsement. Full original technical issue-comment copies are under `published-comments/`; the author's separate personal note is outside this technical edition.

[MANIFEST.json](MANIFEST.json) lists every delivered file except itself, with exact bytes and SHA-256. `provenance/SOURCE-COPIES.json` connects copied/derived files to the original artifact labels and original hashes. Sanitized evidence has new hashes; its original hash identifies the preserved source and does not validate the derivative by itself. Hashes establish byte identity, not authorship, scientific validity, acceptance or deployment.
