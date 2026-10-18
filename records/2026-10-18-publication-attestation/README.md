# Present-day signature for the prior publication record

Owner: **Sherman Gaucia Laing / 0-Actual**  
Attestation date: **October 18, 2026** (America/New_York)  
Prepared with GAUCIA through ChatGPT/Codex at the owner's explicit request.

The owner-controlled OpenPGP signature in this directory authenticates the exact
bytes of [publication-manifest.json](publication-manifest.json). The manifest
identifies earlier publication versions without changing their original commits.
It acknowledges the record, including preserved mistakes and corrections; it does
not endorse every historical assertion as currently correct.

## Exact coverage

| Population | Coverage |
| --- | --- |
| Research record | All 36 commits reachable from main at `f988f284a904591f266b6ade672d0635bcede0f2` |
| Bible replay | All nine commits reachable from main at `433dd2a8b1e561fb12801de54bf1b8250252cef5` |
| Four contribution forks | 16 unique contribution commits across 11 observed non-main branches of Responsible AI Toolbox, ONNX Runtime, Optax and math |
| Total | 61 distinct commit references across six repositories |
| Current research/Bible snapshot inventories | 246 files; all 31 directory-tree identities reconstructed and matched |

The contribution section labels public preparation and staging branches separately
from contribution and validation branches. It records the four Microsoft PRs as
references. Inclusion does not imply upstream acceptance. The forks' main branches
are upstream baseline references, not claims of owner authorship of upstream work.
All 13 references in the earlier unsigned draft are included.

At this review, GitHub reported valid original signatures for 34 of these commits
and no original signature for 27. Those original states are retained. This new
signature attests to the references today; the older 27 commit objects remain
unsigned. The attestation does not change their GitHub badges or backdate signing.

## Verify the signature independently

Signing fingerprint:

```text
FA8C7305ABE0E48D4CECEF700097816F47090DA3
```

Key ID: `0097816F47090DA3`. The public key is registered to
[0-Actual](https://github.com/0-Actual). Download the three files below together,
then use GnuPG:

```sh
gpg --show-keys --with-fingerprint owner-signing-public.asc
gpg --import owner-signing-public.asc
gpg --verify publication-manifest.json.asc publication-manifest.json
```

Compare the entire fingerprint with a trusted owner key record. A public key
obtained from this same download is not, by itself, an independent identity
anchor. On a fresh key store, an unknown-trust warning is distinct from an invalid
signature. The expected manifest SHA-256 is:

```text
9914d0cec786dc711b2d20a5cfadcb016a651f46b7d85059d14ba16e17006556
```

- [Manifest](publication-manifest.json)
- [Detached owner signature](publication-manifest.json.asc)
- [Public signing key](owner-signing-public.asc)

The manifest records complete commit identifiers, tree identifiers, parent links,
recorded author/committer dates and the original GitHub signature observations.
For the current research and Bible snapshots it also lists every file's Git object
identity. A reviewer can fetch a listed commit, compare `git rev-parse <commit>^{tree}`
with its recorded tree, and inspect `git ls-tree -r <commit>` against the inventory.
Git commit and tree identifiers bind the earlier versions; the OpenPGP signature
authenticates this exact reference manifest.

## Scope and preservation

The two main histories were checked through their root commits without missing
parents. Every observed publication branch head was contained in those histories.
All 11 contribution comparisons were complete, and their listed authors were
associated with the 0-Actual account. Current snapshot tree identities were
reconstructed from GitHub's complete recursive inventories. This verification
did not re-download every file body or rerun earlier scientific experiments.

Git author and committer dates remain recorded metadata, not independently proven
creation dates. The OpenPGP signature records its actual new signing time.
This attestation does not establish exclusive originality, ownership of public
mathematics, scientific certification, institutional endorsement or compensation.
Private, deleted or otherwise unlisted publications are outside this exact scope.

Original commits, mistakes, correction history, licenses and third-party notices
are preserved. The existing [repository license](../../LICENSE.md) continues to
apply to material within the owner's rights; referring to upstream work does not
change its license. No private signing key, passphrase, raw personal conversation
or newly disclosed research implementation is included.

For the distinction between GitHub commit badges and signatures on other files,
see [GitHub's commit-signature documentation](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification).
