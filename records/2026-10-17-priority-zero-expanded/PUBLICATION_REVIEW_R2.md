# Publication corrections — October 17, 2026, revision 2

This review corrects the published package and a reproduced GAUCIA shutdown defect.
The original publication is preserved at commit
`9219be1567682d29cd574a6e8e1748404516a4d2`; its receipt and hashes describe that
earlier edition. Use this revision's manifest for the revised bytes. The owner's
dedication, attributed statement and exact noncommercial license are unchanged.

## Findings and corrections

| Finding | Evidence and correction | Verification and limit |
|---|---|---|
| Stop request reported as completed cleanup | The r3 backend discarded its child handle immediately after `kill()`, including a false return. R4 retains ownership until an exit event or already-observed exit, rejects failed/uncertain stops, and makes both service callers await the result. | Two baseline counterexamples, pending-exit/refusal/timeout/error/concurrent-stop checks and service regressions; 55 isolated tests pass. No live model or USB installation. |
| Residual device metadata | Forty-two historical file entries contained device-name or execution-annotation matches that the earlier targeted screen missed. R2 redacts device identity and removes standalone execution annotations from derivative files. | Targeted readback of changed files; original evidence remains preserved. This is not a claim that every possible identifying detail has been ruled out. |
| Broken public document references | Local working paths and copied-document relative paths did not resolve in the distributed layout. 241 link occurrences now resolve to supplied files; 66 references are labeled unresolved instead of being presented as working links. | Resolved targets were selected from supplied path/content identities. Three mathematical expressions flagged by the simple link scanner were false positives and were not changed. |
| Non-JSON annotation appended to a policy file | A standalone tool execution annotation followed the closing JSON object. It is removed from the public derivative. | The revised policy parses as JSON; the historical annotated bytes remain preserved. |
| Verifier did not bound all reads or validate manifest shape | The initial verifier read top-level files before checking observed size and could expose a traceback for a non-object manifest. R2 checks size/type first, hashes payloads in bounded chunks, bounds combined archive members, rejects archive symlinks and validates manifest shapes. | Fifteen valid/tampered-input checks pass. This is integrity checking, not authenticated authorship or scientific validation. |

The initial broad pattern scan reported no matches for its credential/contact/path
patterns, but it did not cover device execution annotations. The subsequent targeted
check found them. That omission is an error in the earlier review scope, not evidence
that the original files had never contained identifiers. Current derivatives and the
new manifest correct the distributed package; older Git history still contains the
previously published bytes. No history rewrite or erasure is claimed.

## What the review covered

The structural pass read 13,276 distributed entries: archive payloads/manifests and
top-level non-archive files. It parsed 144 Python entries (113 distinct byte versions)
and 11,340 JSON entries (9,987 distinct byte versions). The four initial
parse candidates were interpreted: the policy annotation is corrected; the upstream
Python reference is an exported notebook with an IPython shell cell; the remaining
two JSON-named entries are empty historical stdout/posture captures. The latter
three files are retained as evidence and are not advertised as executable Python
or usable JSON data. No invented results were substituted.

The notebook file belongs to a cited
upstream reference, not newly authored project code. Existing scientific reviews
and results remain dated evidence; they were not rerun as part of packaging review.
This is not an exhaustive new semantic review of every prose line, scientific claim
or historical program, and it is not independent peer certification.

## Mathematical and engineering purpose

The shutdown defect collapses two different states: a termination request was
accepted, and the process actually exited. The invariant is that successful cleanup
requires observed completion, while an uncertain process must retain its owner
reference. The analogous verifier invariant compares observed size and bytes with
the declared record without trusting an unbounded read. These are concrete boundary
and state-model findings, not proof of one universal cause across the project.

## Reading and reproducing the revision

Download or clone the repository, then work inside this edition directory. Use
Python 3.10 or newer:

    python -B verify_release.py --manifest-sha256 EXPECTED_REVISION_MANIFEST_SHA256
    python -B test_release_verifier.py

Obtain the actual reference from the revision identity/receipt, not this placeholder.
The first command verifies files and archive contents without extracting or running
research code. The second uses temporary synthetic fixtures and cleans them up.

For cross-collection Markdown links, extract each archive into a separate directory
with exactly its archive basename, all under one common parent. For example,
`collections/Priority-Zero-Teaching/TEACHING_MATRIX.md` links to sibling collection
folders. Do not extract all archives into a shared flat directory.

Use `GAUCIA-service-corrections-r4.zip` for the new backend/service correction and
its isolated tests. Retained `GAUCIA-repair-r3.zip` remains the prior comparison.
QRF remains documentary; two GAUCIA audit dependencies remain absent from this local
selection. Source availability still does not establish a complete fresh install.
No new Library or USB save, credential setup, agreement, monitor or deployment is
claimed. The same disclosure boundary and unchanged license apply.
