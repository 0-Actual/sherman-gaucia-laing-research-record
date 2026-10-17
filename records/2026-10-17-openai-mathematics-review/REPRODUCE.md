# Reproduce the completed finite checks

Use Python 3.12 or later; no third-party package is needed.

```text
python check_capacity.py
```

The script writes `audit/CAPACITY_CHECK_RESULTS.json`. Expected: 72 passing
identity cases, 60 checked stability certificates, four orientation-negative-control
scenarios, and rational coefficient 3/128. A fresh run has a fresh timestamp.
The result contains the script's SHA-256 identity. No API calls, quantum hardware,
Lean installation or source repository code execution are involved.

For the repository-wide procedure, use a separate copy of this packet so the
published result files remain unchanged. Allow several gigabytes of free storage.
With Git installed, acquire metadata without checking out long Windows paths:

```text
git clone --filter=blob:none --no-checkout https://github.com/openai/math.git source-repository
python prepare_inventory.py source-repository
python stream_audit.py
python analyze_map.py
```

The inventory helper verifies the pinned commit exists and reads its complete
Git tree. The scanner obtains the pinned public archive (about 748 MiB), matches
every file body against the tree, then records lexical evidence in SQLite.
It never executes upstream source. The mapper consumes that retained state.
The archive must match SOURCE_RECEIPT.json; download compression metadata can
change over time, so an archive-hash difference requires investigation even if
the individually checked Git blob identities later agree.

The scripts intentionally use simple lexical patterns for this snapshot, including
literal IDs within its YAML sources section; they are not generic Lean, Markdown
or YAML parsers. A marker is not automatically a defect. Fresh timestamps, elapsed
times and reused-file counts differ across runs. Use a fresh directory for an
independent scan. The original exact archive, tree and SQLite state are retained
privately. Repeating this larger scan is unnecessary for the finite check above.

Reproducing a Lean theorem would require the repository's pinned Lean dependencies
and its Comparator instructions, plus adequate resources. It has not been done
by this review. The configuration's permitted-axiom list is not itself a successful
execution receipt.
