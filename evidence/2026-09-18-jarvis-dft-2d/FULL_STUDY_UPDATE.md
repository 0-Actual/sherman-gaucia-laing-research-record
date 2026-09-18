# JARVIS full-study follow-up — 18 September 2026 UTC

Owner: **Sherman Gaucia Laing / Quantum.Earth.Laing**. Analysis and preparation: **GAUCIA through ChatGPT/Codex**. This is a dated documentary update, not a signed software release.

## What changed

The original inspection correctly recorded **42 differences between `nat` and the supplied atom-array length**, **355 missing exfoliation values**, and **1,103 records in the downloaded file**. Those counts remain unchanged. The fuller study adds evidence about interpretation and examines all **65 fields**; it does not replace the source values or classify the 42 records as corrupt.

A periodic-translation diagnostic at **0.001 Å** finds structural support for a repeated-cell interpretation in **40 of the 42 records**. It tests whether candidate translations map each site to a distinct same-species site in the periodic structure. It does not establish why the historical exporter wrote a different `nat`, and it is not a full crystallographic standardization. **JVASP-60484 (HgBr2, 3 versus 9 atoms) and JVASP-6751 (PbBr2, 3 versus 6) remain unresolved.** Failing this particular tolerance-based diagnostic is not proof that no smaller representation exists.

The [initial publication](https://github.com/0-Actual/sherman-gaucia-laing-research-record/tree/2b3d0363b2ed30ba333723347dc36c6a4fadb3ce/evidence/2026-09-18-jarvis-dft-2d) remains in history. Its original missing-value list, atom-count list, and replay evidence are retained. The current landing page points here so readers encounter the fuller interpretation immediately. The catalog's listed 1,109 versus this archive's 1,103 remains unexplained.

## Additional findings from the complete acquired snapshot

| Area | Observation | Interpretation or remaining limit |
|---|---|---|
| Coverage | 1,103 records; 65 top-level fields; all nested values traversed | Entire acquired snapshot, not every dataset or linked calculation in JARVIS |
| Missing properties | 15 fields entirely empty, including superconducting transition temperature | Missing values remain unknown and are never replaced with zero |
| Atomic structures | Consistently shaped, finite lattice and coordinate arrays | Four formula strings disagree with compositions counted from the atom lists; source values retained |
| Formula disagreements | JVASP-60545, JVASP-27866, JVASP-20042, JVASP-28027 | A digit-formatting explanation is plausible but unverified |
| Elasticity | 229 tensors; four contain 20 NaN components; JVASP-28262 has an extreme finite component near 2.10 × 10^17 | Component units, slab scaling, and raw calculations require review before physical conclusions |
| Energy above hull | All 1,103 stored `ehull` values are zero | No stability ranking can be derived from this constant field |
| Formation energy | 952 negative values and 151 positive values | Negative formation energy alone does not establish stability against competing compounds |
| Vibrations | 187 mode lists; each includes a negative entry | Finite-cell effects and exporter handling prevent a sign-only stability verdict |
| OptB88 bandgaps | 397 zero; 706 positive | Calculated under this workflow, not an experimentally established classification |
| Method comparison | On the same 246 rows, mBJ gaps are higher in 160, equal in 44, and lower in 42 | Compare matched records; differing subset averages do not establish method accuracy |
| Descriptors | All 1,717,371 values finite; 77 constant-zero columns | Finiteness does not establish physical validity |
| Duplicate inputs | 34 exact descriptor pairs, also equal in OptB88 gap and formation energy | Keep pairs together in later train/test splits to avoid inflated scores; do not silently fill missing targets |
| Descriptor flags | Nine extremely negative entries at the current packing-fraction position; 1,007 descriptor/top-level density differences above 0.001 | Current column mapping is known; the exact historical generation revision and causes remain unverified |
| Transport | Raw thermal-transport export scaling is not interchangeable with the conductivity scaling | Do not assign thermal-conductivity units to raw `nkappa`/`pkappa` or calculate a device figure of merit without resolving conventions |
| Wannier fields | `maxdiff_mesh` and `maxdiff_bz` are populated in 431 rows | Specific Wannier-versus-DFT comparison measures, not a general dataset error rate |

The measured IDs, counts, translation diagnostics, duplicate groups and caveats are supplied in [machine-readable follow-up evidence](followup_evidence.json). The full-field profile and structure evidence each reproduced exactly on their recorded replay. Detailed analysis code, full source archives and private project implementations remain in the owner's preserved record; this public selection is not a self-contained executable package.

## Scientific meaning and scope

These are calculated properties of periodic slab models. A cell includes vacuum; cell density and response quantities therefore require their geometry and normalization conventions. Formation energy, exfoliation energy, bandgap, and transport each answer different physical questions. Missingness, calculation settings and units must remain attached to those results.

The current upstream source helps explain intended fields but does not prove the precise exporter revision used for each historical row. The 4,666 raw-file pointers in this snapshot were examined as metadata; those linked archives were not downloaded for this census. No new DFT calculation, physical experiment, quantum-circuit simulation, claim of quantum advantage, or finding of misconduct is established by this study.

The responsible project agent is GAUCIA. Scientific execution claims are recorded separately: the census used documented Python inspection routines and numerical diagnostics. An agent attribution alone is not evidence that a particular simulator or emulator executable ran. This update does not disclose or benchmark the owner's private simulator implementation.

## Publication practice

The owner has directed that the complete agreed scope be studied before a dataset statement is published. [Publication review requirements](../../PUBLICATION_REVIEW.md) now specify source identity, field coverage, units, alternative explanations, replay, unresolved findings and exact execution attribution. Early observations must be explicitly marked preliminary if the owner authorizes publishing them. Later evidence is appended with its date; prior observations are not silently erased. This practice reduces avoidable revisions without claiming that scientific interpretation can never change.

## Sources and rights

Kamal Choudhary, [JARVIS-DFT 2D dataset, Figshare version 8](https://doi.org/10.6084/m9.figshare.6815705.v8), file 38521268, `d2-12-12-2022.json.zip`, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These are selected and analyzed source fields; the original archive was not modified. Existing rights in third-party data and bare facts remain intact. QEL's noncommercial documentary terms retain their stated scope and do not replace the source license. No NIST or source-author endorsement is claimed.

Method references: [JARVIS DFT methods](https://jarvis-materials-design.github.io/dbdocs/jarvisdft/), [atomic representations](https://github.com/usnistgov/jarvis/blob/master/jarvis/core/atoms.py), [CFID descriptor definitions](https://github.com/usnistgov/jarvis/blob/master/jarvis/ai/descriptors/cfid.py), [VASP exporter](https://github.com/usnistgov/jarvis/blob/master/jarvis/db/vasp_to_xml.py), [VASP output conventions](https://github.com/usnistgov/jarvis/blob/master/jarvis/io/vasp/outputs.py), and [Wannier comparison source](https://github.com/usnistgov/jarvis/blob/master/jarvis/io/wannier/outputs.py).

The actual update time is recorded by the new commit. The earlier owner-supplied 9:15 p.m. EST label is preserved only for its original record; it is not used to backdate this follow-up. QEL's earlier inception and research chronology are unchanged. No owner signature or SGL Prime witness is claimed.
