> This is a preview of the archive README. Relative links below refer to files inside the corresponding ZIP after extraction.

# Anthropic SDK streaming completion research — October 20, 2026

This public edition contributes bounded independent verification of two **existing** TypeScript proposals and a separate Python behavior characterization. It includes code, source pins, recorded results, reproduction instructions and contributor credit. No upstream acceptance, merge, release readiness or live-service failure is established.

## Existing work and contribution

- **qiyuhuating** reported incomplete completion in [TypeScript issue #1264](https://github.com/anthropics/anthropic-sdk-typescript/issues/1264).
- **ax3cubed** proposed the completion guard in [PR #1265](https://github.com/anthropics/anthropic-sdk-typescript/pull/1265), reviewed head `4354ccd218975d482c89d637a5d13bcebacf4864`.
- **sylvesterkaczmarek** reported the paused-reader problem in [issue #1247](https://github.com/anthropics/anthropic-sdk-typescript/issues/1247) and proposed retained iterator errors in [PR #1248](https://github.com/anthropics/anthropic-sdk-typescript/pull/1248), reviewed head `dd68af161096bd7688a5b4709f8a950bdb8f708f`.

The local contribution is a 24-case interaction test and a comparison of those existing fixes on the pinned base. The source integration adds 12 lines to each helper. It preserves that base's raw-event handling, tracing calls and beta delivery hook. This is not a new-discovery or original-patch authorship claim. Both PRs were open and unmerged at the publication review.

## TypeScript: 123 selected tests

Tested base: `accbdd899218b49fcb3b5124319e99b64d51de90`. The population is **99 existing tests plus 24 added cases**, not the whole SDK suite. Each row is a separate sequential run of that population.

| Source state | Existing passed | Added passed | Added failed | Process exit |
|---|---:|---:|---:|---:|
| Pinned baseline | 99 | 8 | 16 | 1 |
| #1265 completion guard only | 99 | 10 | 14 | 1 |
| #1265 guard plus #1248 retained error | 99 | 24 | 0 | 0 |
| Final formatted source and typed test | 99 | 24 | 0 | 0 |

The guard detects EOF before `message_stop`. With only the guard, an already-waiting iterator rejects, but paused or queued consumers can miss the error after draining available events. Retaining the iterator error closes that delivery gap in these cases. The added tests use public `MessageStream.fromReadableStream` and `BetaMessageStream.fromReadableStream` factories with deterministic NDJSON. They cover paused/queued/waiting readers, typed transport errors and abort identity, explicit abort before EOF, and valid `end_turn`/`max_tokens` completion.

The original PR tests are included for provenance but were **not installed or run verbatim**. Four existing test files supply the 99 existing cases. Final formatting, ESLint, focused TypeScript compilation and whitespace checks exited zero. Initial failures are retained. Fixture-object aliasing was corrected before baseline execution; a later test-only shared interface and type import resolved compiler failures without changing runtime assertions. The final test's bytes therefore differ from the baseline/guard test manifest, as recorded.

Refreshed main was `9c6562472002aa451b6f672acafd6d454e31840f`; both helper files still matched the earlier baseline blobs. This file comparison does not turn the recorded execution into a run at the newer commit.

## Python: 32 behavior characterizations

Tested base: `2d555d1416344a44af9322c88cb04b75df9c878d`. Eight scenarios ran across stable/beta and sync/async public helpers. All 32 matched their expected description of existing behavior. **These are not 32 fixes or 32 confirmed bugs.** No Python source change was implemented.

| Scenario group | Cases | Observed behavior |
|---|---:|---|
| Clean EOF after start or partial text | 8 | `until_done()` succeeds; final-message access returns the partial snapshot. |
| Named server error or transport read error, then another final read | 8 | First getter raises; later getters return the retained partial snapshot. |
| Stop bytes without the final SSE blank delimiter | 4 | No stop event is dispatched; final-message access succeeds. |
| Correctly delimited terminal message | 4 | Stop is dispatched and the expected message is returned. |
| Explicit close before reading or after start | 8 | Remaining chunks are not drained. |

Each case made one in-memory mocked request and recorded a closed response. The five monitored source/fixture hashes matched before and after. The mock uses a `.invalid` host, synthetic credentials, disabled tracing and no live model calls.

The Python [tracing implementation](https://github.com/anthropics/anthropic-sdk-python/blob/2d555d1416344a44af9322c88cb04b75df9c878d/src/anthropic/lib/_tracing/_streaming.py#L107) deliberately records missing-stop EOF as a failed span while leaving application behavior non-raising. Existing fixtures also accept a final stop without its dispatching delimiter. Changing finalization semantics needs an explicit compatibility decision. This research did not execute tracing-enabled cases.

The contract question is whether final getters should provide snapshots after failed/incomplete streams or require terminal completion and retain earlier failures. An actual affected workflow and a maintainer decision should guide any change. Bounded searches found no exact Python duplicate, which does not prove novelty. Adjacent [PR #1959](https://github.com/anthropics/anthropic-sdk-python/pull/1959), by **feiiiiii5**, concerns unnamed SSE errors, a different trigger. The [maintainer response](https://github.com/anthropics/anthropic-sdk-python/pull/1959#issuecomment-6179575394) asks for real-usage evidence before reopening. This edition does not request a speculative new upstream bug report.

Refreshed Python main was `5738a256035e35285857fde0e89ae9b11b805f2f`. The stable/beta helper, tracing helper and reviewed contribution-policy files match their earlier blob identities. No execution at the refreshed commit is claimed.

## Environment and limits

Windows 11; Node 24.20.0, Vitest 4.1.11, TypeScript 6.0.3; Python 3.12.14, httpx2 2.9.1, Pydantic 2.12.5. A pinned pnpm installation failed on Windows symlink creation; a script-disabled npm install succeeded without changing SDK manifests/lockfiles. The npm inventory is included; this is not the exact frozen-pnpm environment. Python dependencies were constrained from the pinned `uv.lock`.

Not covered: full SDK/platform suites, distribution builds and published types, other operating systems, the full Python/Pydantic matrix, live providers, arbitrary-readable abort latency, async cancellation, multi-message NDJSON streams, getters after explicit Python close, tracing-enabled execution or every malformed event ordering. Python's script is an ad hoc characterization, not the repository test entry point. Agent source reviews are not external peer review.

## Contents and provenance

- `source/typescript/`: exact added test, combined patch, two baseline/final helper snapshots, four selected existing tests and shared fixture support.
- `source/upstream/`: saved original source/test patches from #1248 and #1265.
- `scripts/`: exact Python characterization, constraints and focused TypeScript configuration; a clearly marked portable derivative of the execution runner.
- `evidence/`: results, process receipts, source manifests, dependency inventory, setup observations and retained initial failures. Local absolute paths are sanitized where present.
- [REPRODUCE.md](REPRODUCE.md): exact pins, staging order and limitations.
- [SANITIZATION.md](SANITIZATION.md), [PROVENANCE.json](PROVENANCE.json): derivative rules and original/edition byte hashes.
- [CREDITS.md](CREDITS.md), `LICENSES/`: attribution and original MIT notices.
- [LICENSE-MIT-CONTRIBUTIONS.txt](LICENSE-MIT-CONTRIBUTIONS.txt): scoped MIT grant for the new contribution test, Python characterization, execution runner and focused configuration, copyright 2026 Sherman G. Laing. It does not relicense unrelated original research, mathematics/history records or third-party material.
- [MANIFEST.json](MANIFEST.json): every edition file except the manifest itself, with exact path, byte count and SHA-256.

The private source evidence remains preserved. Sanitized files are explicitly derivatives; original hashes inside receipts refer to the private originals and are not silently relabeled as hashes of the sanitized copies. No test, installer, compiler or SDK request was run while preparing this edition. Publication is established only by the hosting repository and publication receipt, not by this filename or a local package.
