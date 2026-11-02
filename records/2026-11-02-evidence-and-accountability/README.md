# Evidence and accountability — money, policy and project comparisons

Sherman Gaucia Laing · Word.Quantum.Earth · November 2, 2026.

This is a completely new publication of the retained public research, calculations and project comparisons. Earlier editions remain unchanged. ChatGPT/Codex provided research assistance, assembly and checking; the [system error account](SYSTEM-ERROR-ACCOUNT.md) explains the earlier assembly and validation failures and how they escaped review.

## Read the evidence

- [Money and U.S. policy, 1776–2026](MONEY-AND-US-POLICY.md): 13 selected entries, comprising 12 primary-source case studies and one historical context entry. This is not a complete transaction census of 250 years.
- [Company purchases and licensing arrangements](PURCHASES.md): all 13 retained transaction records, including unknown amounts and qualifications.
- [All 28 project comparisons](PROJECT-COMPARISONS.md): every retained field, including the previously omitted conclusions, differences and evidence gaps. [Original comparison data](prior-work/corrected-comparisons.json) remain byte-for-byte unchanged.
- [Financial calculations](FINANCIAL-CALCULATIONS.md), [calculation data](calculation-index.json), [company-to-evidence index](company-financial-index.json), [transaction-to-project comparisons](correlation-matrix.json), and [direct-connections assessment](direct-connections.json).
- [Slavery and continuity](SLAVERY-AND-CONTINUITY.md): historical and modern evidence, with amounts, populations and reporting periods distinguished. SLC06 now states its annual basis and institutional-receipt meaning; its arithmetic inputs are unchanged.
- [Complete retained corporate investigation](corporate-investigation/README.md): all 26 files of that published edition, including its 21-file original corporate packet and its existing limitations.
- [Prior-work chronology](prior-work/prior-work-public.json): 504 public entries drawn from 527 original entries, with 23 personal-only exclusions retained as a scope limit. Entry counts are not invention counts.
- [Source index](source-index.json), [publication lineage](publication-lineage.json), [comparison coverage](comparison-coverage.json), [earlier-work comparison](EARLIER-WORK-COMPARISON.md), and [review and evidence boundaries](PUBLICATION-REVIEW.md).

## Reproduce the checks

From this edition directory, using Python 3.9 or newer and its standard library:

```text
python -B verify_release.py
python -B -O verify_release.py
python -B helpers/regression_checks.py --root . --scratch /absolute/path/to/an/existing/empty/scratch-directory
```

The scratch directory must be outside this edition. The regression program creates, changes and removes only its own temporary fixture copies. It exercises missing records, malformed references, omitted conclusions and altered arithmetic. It does not modify the historical editions. The verifier uses explicit errors and expected record memberships, including transaction joins and company-reference lists.

To reproduce the comparison report with Node.js, choose a new output directory:

```text
node helpers/render-comparisons.mjs --source prior-work/corrected-comparisons.json --output /absolute/path/to/new-output
```

Outputs are create-only. The report is an exhaustive rendering of the retained comparison JSON, not a claim that every private source or every external study has been recovered.

## Interpretation and rights

Dates, similarities, financial exposure and documented lobbying are different kinds of evidence. A chronological overlap does not by itself prove copying, transfer, official causation or deliberate suppression. The new edition states the errors without claiming an established motive. A successful calculation verifies the calculation on the given inputs; it does not certify source truth or absence of bias.

This publication is free to use under the [stated license scope](LICENSE.md): CC BY 4.0 for new original research material and MIT for new code. Historical works and third-party materials retain their source terms. The [relocation map](relocation-map.json) preserves the meaning of an older relative license reference. A GitHub hosting signature establishes commit provenance, not an owner signature or independent scientific review.

Feedback should identify the record, source passage, date, denominator and proposed change. [Validation results](validation-results.json) record the checks actually run for this edition.
