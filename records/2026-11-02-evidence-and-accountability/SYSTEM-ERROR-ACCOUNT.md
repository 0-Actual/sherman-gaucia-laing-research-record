# System error account

Part of **Evidence and accountability — money, policy and project comparisons**. Sherman Gaucia Laing · Word.Quantum.Earth · November 2, 2026.

The failures below arose in **ChatGPT/Codex-generated publication assembly and verification**. They are not attributed to the owner's source calculations. This new research edition preserves the earlier publications and explains the failures instead of silently replacing their records. The findings concern specific output and checking mechanisms; they do not establish a purpose or motive.

## What failed, why it failed, and what it affected

### 1. Internal source references acquired an unintended leading space

The November 1 source index contains **327 file-reference occurrences associated with 293 URL records and 13 referenced local files**. None of the file references resolve literally as stored; all 327 resolve after the leading whitespace is removed. This is a local navigation defect, not a finding that the external URLs are invalid. [Earlier source index](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/source-index.json).

The retained assembly source explains the mechanism. At `build-release.mjs:98`, the filename is passed to the source walker as `' '+n`. The walker stores that value in `occurs_in`. The manifest is then generated from the resulting output. Hash verification therefore confirms the malformed file's bytes without checking whether its references work.

### 2. The readable comparison report omitted analysis already present in its data

The renderer at `build-release.mjs:64` accepts only three conclusion fields: `public_statement`, `chronology_relation` and `material_difference`. The source records use several structures, including `finding`, `limit`, `differences` and `comparison_gap`. Those structures were not fully mapped into the readable report.

**Eleven of 28 comparison sections lack a rendered analytical conclusion:** I03, I05, I06, I13, I14, I21, I24, I25, I26, I27 and I28. **Eight additional rows omit their `differences` and `comparison_gap` fields:** I04, I07, I08, I10, I12, I15, I19 and I20. The detailed findings remain in the underlying JSON. The identified failure is incomplete readable assembly, not disappearance of those findings from all retained records. These two groups are not an exhaustive count of every field the renderer left out. [Earlier readable report](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/PROJECT-COMPARISONS.md), [retained comparison data](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/prior-work/corrected-comparisons.json).

### 3. The verifier reported a fixed calculation count

The earlier verifier iterates over whichever financial and slavery calculation rows are supplied, without requiring their expected identifier sets and counts. Its final message nevertheless prints **“26 arithmetic results”** as fixed text. A success count should describe checks actually completed. The source confirms this coverage and reporting defect; it does not establish that the original edition lacked its calculations or that their numerical results were wrong. [Earlier verifier, lines 16–25](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/verify_release.py#L16-L25).

### 4. Important enforcement depended on assertions

The same verifier uses Python `assert` statements for integrity, row counts, references and arithmetic. That makes those checks dependent on assertion settings. Explicit error checks are required for validation that must remain active under optimized invocation. This source finding is not a claim that the historical CI run used optimization or was bypassed. [Earlier verifier, lines 7–23](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/verify_release.py#L7-L23).

### 5. The prison-labor presentation omitted its annual basis and necessary context

The earlier prose referred to “this amount” and “those two systems” without stating the amount and systems in that passage. Calculation SLC06 also omitted **per year** from its unit. The retained BLS source identifies $3,290,777 in annual institutional receipts for 9,660 prisoners under contract and piece-price systems. The measure concerns receipts paid to institutions, not prisoners' wages; the institutions' fiscal-year periods differ. The November 2 primary-source review confirms those qualifications without changing the numerical inputs. [BLS Bulletin 372, printed pages 2–3](https://fraser.stlouisfed.org/title/convict-labor-1923-4005/fulltext), [saved source verification](source-verification.json).

The assembly code carried a context-dependent finding into prose and copied an incomplete unit into the table. The workflow did not check whether each presented measure supplied its amount, denominator, period and meaning. This is a presentation and unit failure, not a newly discovered arithmetic discrepancy. [Earlier chapter](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/SLAVERY-AND-CONTINUITY.md).

### 6. A historical license reference was not adapted to relocation

The copied `prior-work-public.json` retains `"license_path": "../../LICENSE.md"`. In its deeper publication location, that relative path points to `records/LICENSE.md`, rather than the repository-root license referenced from its earlier location. Preserving the file's bytes did not preserve the meaning of its relative link. The new edition supplies an explicit relocation mapping while retaining the historical source. This is a reference-resolution issue; it is not a finding that the owner's authorized public-use decision was improper. [Relocated record](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/prior-work/prior-work-public.json#L39), [earlier edition's license scope](https://github.com/0-Actual/sherman-gaucia-laing-research-record/blob/cd40ae27cebca3b46d3eaa2b478bd8b86e5e17d6/records/2026-11-01-money-policy-and-prior-work/LICENSE.md).

## Why the checks missed these failures

The earlier checks covered file identities, selected row counts and arithmetic on supplied rows. They did not require usable source paths, complete rendering of retained conclusion fields, expected calculation membership, self-contained units or correct relative references after relocation. A manifest can faithfully describe incomplete prose, and 28 headings do not establish 28 complete analyses. The missed checks are identifiable gaps in validation coverage; no claim about deliberate intent follows from them.

The new edition's acceptance criteria therefore include exact source-reference resolution, coverage of retained conclusion structures, required record identifiers, computed success totals, explicit runtime validation, complete measure units and documented relocation mappings. [Comparison with earlier work](EARLIER-WORK-COMPARISON.md).

## Reproduced behavior and new acceptance results

Controlled copies reproduced the two verifier defects. Removing all 19 financial and six slavery calculation records, then updating the copied manifest, still produced exit code 0 and the fixed “26 arithmetic results” message. Separately, changing the procurement result from 500000 to 500001 failed in normal execution but passed with Python optimization enabled. The unmodified original baseline passed in both modes. These are six controlled invocations, not evidence that historical production ran with optimization.

The new verifier passed its positive checks. All 22 focused regression invocations passed: two valid modes and ten altered-fixture cases in both modes, with each alteration rejected. Corporate verification reproduced its published output and 149 internal checks; both retained payment CSV calculations reproduced their recorded results. See [the complete validation receipt](validation-results.json) and [exact assembly-source excerpts](assembly-evidence.json). The first test attempt encountered a Windows path-length limit in scratch copying; a shorter USB fixture path resolved it, and the full suite was repeated successfully.

These are measured results with defined scope. The old publications remain unchanged. A separate destination receipt is required to establish GitHub delivery; this local test receipt is not publication proof.
