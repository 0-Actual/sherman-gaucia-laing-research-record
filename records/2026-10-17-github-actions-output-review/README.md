# GitHub Actions: preserving command-output evidence

Sherman Gaucia Laing / Quantum.Earth.Laing. Investigation and implementation with ChatGPT/Codex; existing reports and upstream authors are credited below.

This study reproduces and corrects lost final lines and UTF-8 corruption in the line callbacks of GitHub Actions Toolkit's `@actions/exec`. It publishes a tested **local correction candidate**, not an upstream release or an installed repair. Work began at the owner's reported October 17, 2026, 7:39 p.m. Eastern marker; GitHub records the actual publication commits separately.

Pinned source: [`actions/toolkit` at 7e25f67](https://github.com/actions/toolkit/tree/7e25f67e8fd17369aa21e6e816ac99654106e0dc). [FrancisRussell's existing issue 1313](https://github.com/actions/toolkit/issues/1313) reported the missing final-line behavior. This study adds executed reproduction, a correction candidate, and broader boundary tests; it does not claim discovery of that original report. Signal termination already has [PR2328](https://github.com/actions/toolkit/pull/2328) and was not duplicated.

## What failed, and why

The line callback receives complete platform-separated lines while the child process runs. At completion, the original code sends leftover text through a different event channel that the public `exec` function does not connect to those callbacks. The last diagnostic can therefore disappear from line-based consumers. Separately, decoding each byte chunk independently corrupts a UTF-8 character when its bytes span chunks. Whole-output collection and raw-buffer callbacks have different paths; this is not a claim that every output API loses the same data.

The intended invariant is straightforward: for each stream, concatenate the received bytes, decode UTF-8, and split by the existing platform separator. Deliver those lines in order, including a nonempty final fragment, independently of how the transport divided the bytes. The candidate keeps separate decoders for stdout and stderr and flushes remaining text through the same guarded callback path. Existing direct ToolRunner tail events and raw-buffer delivery remain available. The invariant assumes nonthrowing callbacks and covers bytes received before the existing completion timeout.

## Observed results

| Test population | Unchanged source | Candidate |
| --- | --- | --- |
| 89 controlled chunk/event cases | 27 pass, 62 fail | 89 pass |
| 11 real local child-process cases | 3 pass, 8 fail | 11 pass |
| Total new regression cases | 30 pass, 70 fail | 100 pass |

These are test cases, not 70 distinct bugs. Tests cover final fragments, blank lines, byte splits inside Unicode characters, independent interleaved streams, incomplete/invalid UTF-8, failure paths, delayed closure, callback exceptions and 128 KiB output. Expected text is derived by whole-buffer decoding, independently of the incremental decoder implementation.

There is passing evidence for **31 distinct existing execution tests across two runs**. One remaining local `ls.exe` startup failure also occurs on unchanged upstream. This is not a clean full-suite pass. Formatting passes; TypeScript diagnostics were enabled in the regression run. Full lint, hosted Actions, other operating systems and full-repository testing remain unverified. See [case-level results](CASE_RESULTS.json), [summary](RESULTS.json), and [corrections and limits](CORRECTIONS_AND_LIMITS.md).

## Reproduce and inspect

Start with [REPRODUCE.md](REPRODUCE.md). The [patch](correction.patch), [corrected source](toolrunner.corrected.ts), [controlled tests](output-lines.test.ts), [native-process tests](output-lines-integration.test.ts), pinned source inventory and locked small test harness are included. Thirty-three selected original files matched their Git blob identities, and applying the patch recreated the three tested file bodies. This is selected source coverage, not a whole-GitHub audit.

The repository's [README note](https://github.com/actions/toolkit/blob/7e25f67e8fd17369aa21e6e816ac99654106e0dc/README.md#note) currently pauses code contributions even though its contribution guide welcomes them. The assistant checked that README too late; the selection error is preserved in this study. No upstream pull request, agreement acceptance, maintainer approval, certification or compensation is established by this publication.

Original study material uses the owner's unchanged [noncommercial research license](LICENSE.md). GitHub-derived production source retains [MIT](UPSTREAM_LICENSE.txt); see the precise [rights map](RIGHTS.md). This publication does not include private project implementations or personal conversation data. File hashes establish byte identity, not scientific validity or an author-controlled cryptographic signature. GitHub commit signatures must be evaluated separately on the actual publication commits.
