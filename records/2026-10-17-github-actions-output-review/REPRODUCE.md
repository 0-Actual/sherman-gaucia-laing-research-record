# Reproducing the study

Use a disposable checkout of actions/toolkit at commit `7e25f67e8fd17369aa21e6e816ac99654106e0dc`, Python 3.10+ and Node 24.20.0. This study was executed on Windows. Other operating systems may produce a different number of parameterized byte-split cases because the platform separator has a different byte length.

From this study directory, prepare the selected source snapshot:

```text
python prepare_review.py --checkout PATH_TO_TOOLKIT --output reproduction
cd reproduction
npm ci --prefix tools --ignore-scripts --no-audit --no-fund
node setup-tests.cjs
node prepare-candidate.cjs
```

The helper checks 33 file sizes/Git blob identities before copying them. It refuses a nonempty output directory. It copies the exact test harness, dependency lock, test files and source-preparation script into the new directory. The tools folder's package lock pins the executed harness; no global install or configuration change is required.

Run these commands one at a time. The baseline command is expected to return a failing exit status; retain its output and continue with the candidate comparison:

```text
node tools/node_modules/jest/bin/jest.js --config upstream/review-jest.config.cjs --runInBand --runTestsByPath upstream/packages/exec/__tests__/output-lines.test.ts upstream/packages/exec/__tests__/output-lines-integration.test.ts
node tools/node_modules/jest/bin/jest.js --config candidate/review-jest.config.cjs --runInBand --runTestsByPath candidate/packages/exec/__tests__/output-lines.test.ts candidate/packages/exec/__tests__/output-lines-integration.test.ts
node tools/node_modules/jest/bin/jest.js --config candidate/review-jest.config.cjs --runInBand --runTestsByPath candidate/packages/exec/__tests__/exec.test.ts
```

The first two recorded Windows results are 30 pass / 70 fail and 100 pass. The existing suite has the limitations documented in README.md; do not suppress or count its environment failures as passes. Use a Node path without spaces and make the required ls executable available for that existing suite; those are test-environment prerequisites, not a production patch. The local failing ls startup case remains reproducible on unchanged upstream.

The local harness maps @actions/io to pinned source and enables TypeScript diagnostics. It does not claim equivalence to the entire repository's build/CI environment. The three-file correction.patch can alternatively be checked/applied in a clean upstream checkout with `git apply --check` and `git apply`; this was verified separately to recreate the tested bytes. For broader validation, follow the upstream build/bootstrap, format-check and lint instructions. Those full checks have not been completed here.

Source baseline identities are in SOURCE_MANIFEST.json; published-file SHA-256 identities are in MANIFEST.json. Neither file is a cryptographic signature. Review RIGHTS.md before reuse or any proposed upstream submission; the repository currently pauses code contributions.
