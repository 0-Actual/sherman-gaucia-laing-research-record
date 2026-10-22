# GitHub Actions exec callback correction — current-source follow-up

This packet updates the [17 October output-integrity study](https://github.com/0-Actual/sherman-gaucia-laing-research-record/tree/main/records/2026-10-17-github-actions-output-review) against actions/toolkit commit [0c3a9c332b678ff1e776f93d728a4ad279803abe](https://github.com/actions/toolkit/commit/0c3a9c332b678ff1e776f93d728a4ad279803abe), retrieved 21 October 2026. It is a local correction candidate and reproduction record, not an upstream release or installed repair.

Two mechanisms are addressed: public `stdline/errline` callbacks can miss the last fragment when no newline follows it, and decoding each received Buffer separately can corrupt UTF-8 when a character crosses chunks. Raw-buffer delivery and `getExecOutput()` use other paths and are not claimed to lose all output. FrancisRussell's existing [issue 1313](https://github.com/actions/toolkit/issues/1313) already reported the final-fragment symptom in January 2023.

## Changes from the earlier candidate

Upstream [PR 2552](https://github.com/actions/toolkit/pull/2552), merged 20 October 2026, changed line recognition from host `os.EOL` to LF with optional preceding CR. This candidate preserves that correction. It adds separate streaming UTF-8 decoders, delivers nonempty final fragments through the same guarded option-callback path, and preserves existing direct ToolRunner tail events.

The current upstream tests directly invoke the private line parser with Buffers. The parser now consumes decoded text; the existing parser test is correspondingly updated to pass its string chunks. The new focused tests also cover mixed LF/CRLF, lone CR, a final CR, and CR immediately before CRLF, in addition to the original byte-boundary, interleaving, error, delayed-close, invalid/incomplete UTF-8 and native-process cases.

## Fresh local evidence

On Windows with Node 24.19.0, Jest 29.7.0, ts-jest 29.1.1 and TypeScript 5.2.2 (TypeScript diagnostics enabled):

| Population | Unchanged current source | Candidate |
|---|---:|---:|
| 111 controlled cases | 27 passed, 84 failed | 111 passed |
| 14 real child-process cases | 3 passed, 11 failed | 14 passed |
| Total focused cases | 30 passed, 95 failed | 125 passed |

The 95 failures are test cases exercising the two mechanisms, not 95 independent defects. Test counts are platform-specific because the original vectors include the host newline.

The existing current `packages/exec/__tests__/exec.test.ts` suite was also checked using Node 24.20.0: 34 of 35 tests passed. The one failure was the environment's `ls.exe` starting with exit 3221225794. RESULTS.json records the unchanged-upstream control separately. Four changed files pass Prettier 3.0.3. Full ESLint was not completed because its dependencies are absent from the available local harness; direct network source/dependency access was unavailable. This is not a clean full-repository or hosted-platform pass.

The first compatibility attempt stopped before running tests because the older private-helper test still passed a Buffer to the new string signature. The test was updated and the compatibility suite rerun. A separate nearby-test control selected four tests and passed all four; only the exact failing-test control is relevant to the `ls.exe` comparison.

## Files and reproduction

- `correction.patch` changes the upstream production file and its existing parser test; both retain upstream MIT treatment.
- `output-lines.test.ts` and `output-lines-integration.test.ts` are the updated original study tests. Their existing owner license remains in effect; see RIGHTS.md.
- `SOURCE_MANIFEST.json` lists 43 selected upstream files whose raw content matched the Git blob IDs before testing. This was an isolated verified subset, not a full Git clone.
- `RESULTS.json` and `CASE_RESULTS.json` distinguish fresh focused, compatibility and control outcomes.

To evaluate: obtain the exact upstream commit, apply `correction.patch`, and place the two test files under `packages/exec/__tests__/` within the permissions of their existing license. The local harness mapped `@actions/io` and `@actions/io/lib/io-util` to the selected upstream TypeScript sources, transpiled with ts-jest and enabled TypeScript diagnostics. No upstream dependency code was modified. The complete original locked harness instructions remain in the earlier study.

The invariant assumes nonthrowing line callbacks and bytes received before the existing process completion deadline. A throwing listener remains best-effort; the correction does not redesign completion deadlines, signal handling or hosted Actions logging.

## Submission scope

The current upstream README still pauses contributions while explicitly welcoming bug reports; .github/CONTRIBUTING.md describes tests, formatting and lint expectations. This packet supports factual follow-up on issue 1313 and a distinct UTF-8 report. It does not claim maintainer approval, agreement acceptance, a grant of broader rights over the original tests, or an accepted upstream patch. Sherman Gaucia Laing directed the work; ChatGPT/Codex performed the source comparison, implementation and local validation.

