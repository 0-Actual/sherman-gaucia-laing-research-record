# Corporate ownership, political spending and disclosed relationships

**Sherman Gaucia Laing · Word.Quantum.Earth**  
Source cutoff: October 31, 2026. Publication review: November 1, 2026. Research assistance: ChatGPT and session research agents.

[Read the complete report](corporate/REPORT.md) · [Browse the 78-source register](corporate/SOURCE_REGISTER.md) · [Download the source table](corporate/source_register.csv) · [Review corrections](corporate/CORRECTIONS.md)

This public investigation examines selected records concerning OpenAI, Microsoft and Alphabet/Google: ownership and voting rights, political contributions, lobbying, state-linked commercial and institutional relationships, and disclosed leadership affiliations. The review window is October 31, 2020–October 31, 2026, with dated background and full-calendar-2020 baselines identified separately. It is not a complete transaction census.

## Findings to examine

- Alphabet's specified founder holdings represented approximately **52.7446% of A/B votes on April 6, 2026**. Voting control and equity ownership are different quantities. [Sources and arithmetic](corporate/REPORT.md)
- Microsoft's September 30, 2026 disclosure reported an **approximately 24% as-converted OpenAI investment interest**. Historical ownership percentages from other dates do not form a current capitalization table. [Input bindings](corporate/input_bindings.json)
- Selected 2025 lobbying filings sum to **$9.36 million for Microsoft, $13.10 million for Google, and $2.99 million for OpenAI**. Microsoft's Method C and Google/OpenAI's Method A use different reporting definitions; these figures are not a comparable ranking of influence. [Dated filings and method rules](corporate/REPORT.md)
- The linked Google corporate political-contribution PDF yields **$9,102,075 across 264 rows for 2025**, and **$537,800 across 74 rows for 2020**. These are separate from PAC disbursements and lobbying. A parsing correction and its effect remain documented. [Corrections](corporate/CORRECTIONS.md)

The records establish specific disclosed relationships and financial quantities. They do not establish hidden intent, a shared covert purpose, or a causal effect on a particular AI response.

## Inspect and reproduce

The [corporate directory](corporate/) contains all **21 files from the original corporate packet**, preserved byte for byte. It includes the report, source register, frozen inputs, input-to-source bindings, calculator, expected outputs, verification programs, capture metadata, corrections and unresolved reproduction status.

From that directory, using Python 3:

```text
python verify_manifest.py
python verify.py
python calculate.py --inputs inputs.json
```

The offline replay passed the original 20-payload integrity check and **149 arithmetic, count and policy checks**, with repeatable output matching the stored fixture. These are internal checks, not 149 external reviewers. See the [November 1 publication review](PUBLICATION-REVIEW.md).

The original source documents are linked, not bundled. Capture hashes identify previously retrieved bytes; a later download may differ. The [source capture record](corporate/source_capture_manifest.json) and [PAC reproduction status](corporate/msvp_pac_reproduction_status.json) preserve failures and gaps. Three external review assignments remain unfilled in the [audit register](corporate/external_audit_register.json).

## Open review: identify errors and bias

Readers are invited to examine the source selection, missing periods, reporting definitions, denominators, assumptions, calculations and framing. Submit a [repository issue](https://github.com/0-Actual/sherman-gaucia-laing-research-record/issues) with the exact claim or file, a primary-source reference, and a reproducible correction or alternative calculation. Disagreement is welcome. Corrections will be dated and preserve the earlier record.

## Free use

The original report and data in this edition are licensed **CC BY 4.0**; the Python code is **MIT licensed**. Both permit free reuse, including commercial reuse, subject to their attribution/notice terms. This edition's specific grant takes precedence over the repository's general noncommercial notice for these files. Original third-party documents retain their own rights. Read [LICENSE.md](LICENSE.md) and [LICENSE-MIT.txt](LICENSE-MIT.txt).

The original packet's references to a review copy and no publication describe its October 31 preparation state. This dated wrapper records the subsequent owner-authorized publication without rewriting those originals. File hashes establish byte integrity, not source truth, independent peer review or an owner cryptographic signature.
