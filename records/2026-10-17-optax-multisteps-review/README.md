# Optax MultiSteps: non-finite masking and recovery

Prepared for Sherman Gaucia Laing's research record on October 17, 2026 (Eastern).
AI-assisted analysis, implementation and documentary preparation: Codex under the owner's direction.
This edition preserves work first published in the owner's Optax fork earlier that day; it is not a new date of discovery or a Google-accepted contribution.

**Result:** the recorded baseline has **30 failures and 4 passes in 34 added regression cases**. The correction passes the selected two-file suite: **55 tests plus 30 subtests**, with zero failures, errors or skips. These populations differ; 85 JUnit records are not 85 independent tests. Evidence comes from the completed [hosted run](https://github.com/0-Actual/optax/actions/runs/39010905993).

MultiSteps accumulates gradients and emits an optimizer update only on the designated step. Arithmetic zero masks can leak NaN or infinity into a supposedly zero update, or fail to clear a completed accumulator. The preserved patch replaces two arithmetic masks with explicit selection. It does not introduce a general policy to reject non-finite inputs.

| Read | Purpose |
| --- | --- |
| [Findings](FINDINGS.md) | Mathematical contract, counterexample, mechanism, correction and limits |
| [Results](RESULTS.json) | Counts with units, times, source identities and evidence provenance |
| [Reproduce](REPRODUCE.md) | Pinned source and commands for independent CPU verification |
| [Patch](contribution.patch) | Previously published two-file correction and regression tests |
| [Hosted evidence](HOSTED_TEST_EVIDENCE.txt) | Preserved baseline failures and successful terminal summary |
| [Environment](environment-observed.txt) | Observed installed versions; not a complete environment lock |
| [Corrections and limits](CORRECTIONS_AND_LIMITS.md) | Earlier mistakes, local setup failure and unresolved validation limits |
| [Source references](SOURCE_REFERENCES.json) | Immutable commits, file hashes, workflow and artifact references |
| [Rights](RIGHTS.md) | Owner commentary license and separate Apache-2.0 rights |
| [Manifest](MANIFEST.json) | Exact published file sizes and SHA-256 hashes, excluding the manifest itself |

The selected correction and regression tests were already public in [0-Actual/optax](https://github.com/0-Actual/optax/tree/1c7e94b42f47899bd98021ed03fe4e0088be4a41). Google’s Individual CLA was declined. No upstream pull request, maintainer acceptance, merge or certification is claimed. The original unsigned fork commits remain unchanged; a later signed publication does not retroactively sign them.

**License boundary:** original new commentary uses the existing [Quantum.Earth.Laing noncommercial license](LICENSE.md). The Optax-derived patch and tests retain [Apache-2.0](UPSTREAM_LICENSE.txt); the owner license does not restrict rights already granted in those materials. No additional agreement is accepted by this publication.
