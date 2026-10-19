# Automated publication checks

Prepared October 18, 2026 at Sherman Gaucia Laing / Quantum.Earth.Laing's direction with Codex assistance. These new maintenance utilities follow the repository's existing noncommercial research license. They do not modify the preserved research editions.

These checks cover publication integrity and branch-preservation settings. They do not establish scientific correctness, exclusive origin, upstream acceptance or later-commit coverage by an earlier signature.

Run with Python 3.12 from the repository root:

```text
python -B verify_publications.py manifests
python -B test_publication_checks.py
python -B verify_publications.py attestation
python -B verify_publications.py protection
python -B records/2026-10-17-priority-zero-expanded/verify_release.py
python -B records/2026-10-17-priority-zero-expanded/test_release_verifier.py
```

The attestation command requires GnuPG. It imports only the published public key into a temporary isolated key store and checks the exact historical manifest, detached signature and expected owner fingerprint. It never requests a private key or signing operation. The fingerprint and signed manifest identity are pinned to the independently verified October 18 owner record. A later authorized attestation needs a reviewed update; it must not silently extend the earlier record.

All seven edition manifests are required. Both existing size schemas (`bytes` and `size`) are supported. Listed payload hashes and sizes are recomputed; missing, extra, colliding or unsafe paths are rejected. The existing expanded-release verifier also reads and validates its archive contents without extracting or executing research code. Other historical inventories are not treated as current manifests.

The protection command makes read-only GitHub requests and checks active all-branch coverage, the three preservation/signature rules, no exclusions and every visible branch. If GitHub exposes bypass actors, that list must be empty. If it omits the field for the caller, the output explicitly leaves bypass review to authorized administration; it does not infer an empty list or request broader credentials. Network or permission failures are reported as failures to verify, not as proof of an unprotected repository. This is an observation at run time, not continuous settings monitoring.

The workflow runs on pushes and pull requests without path filters, and can be launched manually. Only branches containing this workflow can run it on push; historical branches are retained unchanged. Pull requests into the updated default branch receive the checks. No scheduled maintenance, AI review, paid service, automatic fixes or upstream workflow approval is created.

The Windows and Ubuntu checks use fixed action commit IDs and read-only permissions. Action updates require review of the official source and a passing candidate run. Full repository histories, external links, every archived research implementation, and scientific replication remain outside this bounded integrity check.
