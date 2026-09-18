# JARVIS data evidence — owner record at 9:15 p.m. EST

Sherman Gaucia Laing / Quantum.Earth.Laing. Analysis and documentary preparation by GAUCIA through ChatGPT/Codex.

**Owner-supplied timestamp: 9:15 p.m. EST, preserved verbatim.** The actual analysis and replay timestamps below are machine-recorded UTC values. The owner label is not used to backdate execution or GitHub publication, and neither is claimed to be a trusted or signed timestamp. This review does not change QEL's inception chronology.

## Current interpretation — updated 18 September 2026 UTC

**Read the [full-study follow-up](FULL_STUDY_UPDATE.md) alongside the original observations below.** The count of 42 atom-count differences is unchanged. A later geometric diagnostic supports a repeated-cell interpretation in 40 cases; JVASP-60484 and JVASP-6751 remain unresolved. It does not prove the historical cause. The follow-up also documents the complete 65-field study, additional missingness, formula/tensor issues, and duplicate descriptors. [Structured follow-up evidence](followup_evidence.json).

## Initial inspection scope and findings

This is an inspection of published JARVIS DFT data. No new DFT calculation, quantum-circuit simulation, AI training, materials discovery, or quantum advantage demonstration was performed.

| Observation | Result |
|---|---:|
| Records in the selected archive | 1,103 |
| Distinct record IDs | 1,103 |
| Current catalog's listed records | 1,109 |
| Numeric exfoliation-energy values | 748 |
| Missing exfoliation-energy values (`na`) | 355 |
| Atom-count metadata differences | 42 |
| Deterministic replay outputs with identical bytes | 3 of 3 |

The catalog/file difference is unresolved. Missing values were excluded from numeric summaries and never substituted with zero. See [all 355 missing-value records](missing_exfoliation_values.json).

## Analysis replay

Two separate Python processes ran the final analysis implementation against the same included source archive. Their `analysis.json`, `record_index.json`, and `checks.json` outputs matched byte-for-byte. Runtime/environment metrics were excluded from that comparison because their timestamps and timings vary. The raw run timestamps, metrics, checks, and comparison record are in [replay evidence](replay_evidence.json).

The analysis ran with the Python standard library and no network operations. Its source code and the complete input/output archive are preserved in the owner's private review package. This public evidence selection does not itself include that code or claim to be a self-contained replay package. Published record IDs and source provenance support independent checks of the dataset findings.

Two review checks remain flagged: the catalog/file count difference and the atom-count metadata differences. Reproducing a finding does not resolve its cause. There is no claim that all data-quality checks passed.

## All 42 atom-count differences

For these records, the `nat` metadata field differs from the number of elements in the supplied `atoms` structure. The coordinate count matches the element count. Forty-one structures contain twice the `nat` count and one contains three times that count. The initial inspection proposed a cell-representation difference as a possible explanation, **not a verified cause**. The later [full-study diagnostic](FULL_STUDY_UPDATE.md) supplies structural support for that interpretation in 40 cases while leaving two unresolved; the historical export cause remains unverified. Records were preserved unchanged and were not classified as corrupt or deleted. The scalar summaries did not use `nat`.

| Record ID | Formula | `nat` field | Supplied structure atoms | Structure / `nat` |
|---|---|---:|---:|---:|
| JVASP-13526 | YBr3 | 8 | 16 | 2 |
| JVASP-75379 | S | 1 | 2 | 2 |
| JVASP-68932 | WS2 | 6 | 12 | 2 |
| JVASP-60484 | HgBr2 | 3 | 9 | 3 |
| JVASP-6895 | CS2 | 3 | 6 | 2 |
| JVASP-19586 | SnS | 4 | 8 | 2 |
| JVASP-5926 | TaSe2 | 3 | 6 | 2 |
| JVASP-9044 | BaS | 4 | 8 | 2 |
| JVASP-27848 | TbCBr | 6 | 12 | 2 |
| JVASP-28270 | BiS2 | 6 | 12 | 2 |
| JVASP-9023 | Rb2Pd3S4 | 9 | 18 | 2 |
| JVASP-5959 | TaS2 | 3 | 6 | 2 |
| JVASP-9032 | Li4O | 5 | 10 | 2 |
| JVASP-5890 | PbS | 4 | 8 | 2 |
| JVASP-27741 | SiP | 12 | 24 | 2 |
| JVASP-6100 | AlCl3 | 8 | 16 | 2 |
| JVASP-6397 | CrI2 | 3 | 6 | 2 |
| JVASP-6256 | NbS2Cl2 | 10 | 20 | 2 |
| JVASP-6202 | IrBr3 | 8 | 16 | 2 |
| JVASP-6943 | CrCl3 | 8 | 16 | 2 |
| JVASP-6136 | IrCl3 | 8 | 16 | 2 |
| JVASP-6955 | BiI | 8 | 16 | 2 |
| JVASP-6148 | RhCl3 | 8 | 16 | 2 |
| JVASP-6085 | RhBr3 | 8 | 16 | 2 |
| JVASP-6751 | PbBr2 | 3 | 6 | 2 |
| JVASP-6802 | TaCl4 | 10 | 20 | 2 |
| JVASP-27781 | BaB2Se6 | 9 | 18 | 2 |
| JVASP-28106 | CoH2O2 | 5 | 10 | 2 |
| JVASP-20004 | HgI2 | 3 | 6 | 2 |
| JVASP-27775 | Te2Au | 3 | 6 | 2 |
| JVASP-730 | MoS2 | 3 | 6 | 2 |
| JVASP-31379 | CoO2 | 3 | 6 | 2 |
| JVASP-6823 | NbCl4 | 10 | 20 | 2 |
| JVASP-9008 | BaSe | 4 | 8 | 2 |
| JVASP-6322 | CdPS3 | 10 | 20 | 2 |
| JVASP-20014 | YCl3 | 8 | 16 | 2 |
| JVASP-14420 | NbSe2Br2 | 10 | 20 | 2 |
| JVASP-5917 | PbS | 4 | 8 | 2 |
| JVASP-20054 | PS | 8 | 16 | 2 |
| JVASP-28006 | ThTe2I2 | 10 | 20 | 2 |
| JVASP-28013 | Tl2O | 3 | 6 | 2 |
| JVASP-153104 | B | 4 | 8 | 2 |

Machine-readable values: [atom-count differences](atom_count_differences.json).

## Source, attribution, and license scope

Kamal Choudhary, **JARVIS-DFT 2D dataset (jdft_2d.json), Figshare version 8**, [DOI 10.6084/m9.figshare.6815705.v8](https://doi.org/10.6084/m9.figshare.6815705.v8), [file 38521268](https://ndownloader.figshare.com/files/38521268). Selected file: `d2-12-12-2022.json.zip`, 8,394,653 bytes; one JSON member of 24,758,679 bytes. Version published December 12, 2022. [Official source metadata](https://api.figshare.com/v2/articles/6815705), [NIST catalog](https://pages.nist.gov/jarvis/databases/), [JARVIS access mapping](https://github.com/usnistgov/jarvis/blob/master/jarvis/db/figshare.py).

The dataset is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This evidence selects source fields and calculates counts; it is not an unchanged full dataset. Existing CC BY rights in the original data and these data extracts remain intact. The repository's noncommercial terms apply only to protectable QEL-owned expression within their stated scope, not to third-party data, bare facts, or rights already granted under CC BY. No NIST or author endorsement is implied. No contribution to an upstream NIST repository was made.

This record documents our review of a pre-existing public dataset. It does not claim original authorship of JARVIS data, that these discrepancies are newly discovered by us, experimental validation, or a finding of misconduct. No owner signature or SGL Prime witness is claimed. Actual GitHub publication time is independently shown in the repository commit history.
