# OpenAI mathematics: repository review and first selected avenue

Prepared October 17, 2026 for Sherman Gaucia Laing / Quantum.Earth.Laing.
Supporting review and independently authored checks: Codex. This study is prepared
for the owner's research repository. No submission has been made to OpenAI.

The owner invites an intellectual discussion with OpenAI and the wider mathematical
community: examine the assumptions, reproduce the checks, and identify where the
reasoning can be improved. The aim is a constructive contribution that gives credit
and helps others learn. Original review code and commentary retain the existing
owner license; upstream-derived documentation retains Apache-2.0.

## What is complete

The full file inventory and structural pass cover pinned commit `1581d4cbdd69a0faf34b2089614fe2a814316a6a`.
All **133,956 files** match their Git blob identities. There are **133,166 UTF-8
text files**, covering **30,198,391 physical text lines**, plus 790 binary files
checked for byte identity. These counts include prior versions, proof modules,
supporting material and generated-looking files; they are not counts of discoveries.

The corrected catalogue contains **719 unique current manuscript links in 372
families**. All point to retained files. All 416 parsed Comparator configurations
point to existing challenge and solution modules, and list `propext`, `Quot.sound`
and `Classical.choice` as their permitted axioms. No unresolved `OAI.*` import path
was found by the lexical import scan. No JSON parse exception was recorded.

These are structural checks. **No Lean compilation or Comparator execution has
occurred, and the collection has not received a complete semantic proof review.**
The catalogue's 300/719 formalization claim is OpenAI's stated metric. Our 416
configurations, 173 YAML source identifiers and 341 scope-note paper links are
different populations; none replaces that metric or independently validates it.

## Selected avenue: quantum Heisenberg ferromagnets, family 271

This is a substantial mathematical-physics direction with a concrete connection
to our earlier work on observables, matrix invariants and simulation limits. Its
four papers concern spontaneous magnetization, Bloch's law, the first lattice
correction, and the spherical magnetization law. The formalization scope note
specifically covers spontaneous magnetization. It is not blanket coverage of
all four manuscripts.

The first completed mathematical checks concern the finite capacity comparison
and ideal-magnon coefficient in the lattice-correction paper. **72 exact rational
cases pass the identities; 60 also pass an applicable energy-dual stability
certificate.** Four matrix scenarios detect the intentionally incorrect use of
the forward operator in place of the adjoint. The coefficient calculation agrees
with the paper. No new mathematical error is established by these checks.

The next deep work is the uniform pin-conditioned estimates, the forward and
adjoint residual bounds, and the stated order of thermodynamic, field and
temperature limits. Those steps remain open in our review. The accompanying
[foundation review](FOUNDATION_REVIEW.md) explains what was checked and why the
finite results do not settle the infinite-system claims.

## Findings and retained state

[Findings](FINDINGS.json) separate passed checks, an existing version-navigation
mismatch, known upstream corrections, and our own corrected parser error.
[The proposed scope note](TAMING_SCOPE_NOTE.proposed.md) links the revised and
previous editions of family 342 without extending the formalization claim.
It is a proposed Apache-2.0 derivative, not an installed repair or an upstream submission.

[The review queue](REVIEW_QUEUE.json) retains all 372 families. [The source
receipt](SOURCE_RECEIPT.json) binds the snapshot and selected evidence.
[Reproduction instructions](REPRODUCE.md) cover the small independent check.
The published scan and mapping scripts make the structural procedure inspectable.
The complete compressed archive and SQLite review ledger are retained locally,
so unchanged sources need not be downloaded or fully rescanned by the author.

[Official release](https://openai.com/index/sharing-ai-progress-in-mathematics/)
and [pinned repository](https://github.com/openai/math/tree/1581d4cbdd69a0faf34b2089614fe2a814316a6a/).
