#!/usr/bin/env python3
"""Read public FEC records and write a slim committee-level summary.

Requires Python 3.10+; no third-party packages. Raw responses are retained in
an internal cache outside the public output directory. Public output includes
only committee aggregates, response hashes and public URLs, never addresses.
The FEC API may rate-limit DEMO_KEY; optionally set FEC_API_KEY in the environment.

Usage: python reproduce_msvp_pac.py
Replay retained bytes: add --offline --raw-dir /path/to/internal/cache
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "https://api.open.fec.gov/v1/schedules/schedule_b/"
FILTERS = {
    "committee_id": "C00227546",
    "two_year_transaction_period": "2026",
    "per_page": "100",
    "sort": "-disbursement_date",
    "line_number": "F3X-23",
    "min_date": "2025-01-01",
    "max_date": "2026-08-31",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "msvp_pac_reproduced.json")
    parser.add_argument("--raw-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent / "sources_raw" / "msvp_pac")
    parser.add_argument("--offline", action="store_true",
                        help="Recompute only from retained response bytes and capture manifest")
    args = parser.parse_args()
    if args.raw_dir.resolve().is_relative_to(args.output.resolve().parent):
        raise ValueError("The internal raw cache must be outside the public output directory")
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    capture_manifest = args.raw_dir / "capture_manifest.json"
    cached_pages = json.loads(capture_manifest.read_text()) if args.offline else []
    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    params = dict(FILTERS, api_key=api_key)
    totals = defaultdict(lambda: Decimal("0"))
    names = defaultdict(set)
    counts = defaultdict(int)
    manifests = []
    seen = set()
    dates = []
    row_count = nonmemo_count = missing_id_count = 0
    expected_count = None
    total = Decimal("0")
    for page in range(1, 1001):
        url = BASE + "?" + urlencode(params)
        raw_filename = f"page_{page:03d}.json"
        if args.offline:
            if page > len(cached_pages):
                raise RuntimeError("Missing retained response page")
            captured = cached_pages[page - 1]
            raw = (args.raw_dir / raw_filename).read_bytes()
            if hashlib.sha256(raw).hexdigest() != captured["raw_response_sha256"]:
                raise RuntimeError("Retained response hash mismatch")
        else:
            with urlopen(url, timeout=40) as response:
                raw = response.read()
            (args.raw_dir / raw_filename).write_bytes(raw)
        result = json.loads(raw)
        rows = result["results"]
        expected_count = result["pagination"]["count"]
        # Public replay URL never contains a private key supplied by the user.
        public_params = dict(params, api_key="DEMO_KEY")
        provenance = {
            "page": page,
            "public_url": BASE + "?" + urlencode(public_params),
            "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw),
            "row_count": len(rows),
            "pagination": result["pagination"],
        }
        if args.offline and provenance["public_url"] != captured["public_url"]:
            raise RuntimeError("Retained response query differs from current frozen filters")
        manifests.append(provenance)
        if not args.offline:
            capture_manifest.write_text(json.dumps(manifests, indent=2) + "\n")
        row_count += len(rows)
        for row in rows:
            sub_id = row.get("sub_id")
            if sub_id is not None:
                if sub_id in seen:
                    raise RuntimeError("Repeated sub_id across API pages; aborting aggregation")
                seen.add(sub_id)
            if row.get("memoed_subtotal"):
                continue
            nonmemo_count += 1
            amount = Decimal(str(row["disbursement_amount"]))
            total += amount
            dates.append(row["disbursement_date"])
            recipient_id = row.get("recipient_committee_id")
            if not recipient_id:
                missing_id_count += 1
                continue
            totals[recipient_id] += amount
            names[recipient_id].add(row["recipient_name"])
            counts[recipient_id] += 1
        if row_count >= expected_count:
            break
        indexes = result["pagination"].get("last_indexes")
        if not rows or not indexes:
            raise RuntimeError("FEC pagination stopped before its reported count")
        params.update(indexes)
    else:
        raise RuntimeError("Unexpectedly many pages")
    if row_count != expected_count:
        raise RuntimeError("Fetched row count differs from FEC reported count")
    summary = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "U.S. Federal Election Commission processed Schedule B API",
        "filters": FILTERS,
        "method": "All pages via returned last_indexes; exclude memoed_subtotal; aggregate by recipient_committee_id and combine name aliases/accounts. No additional amendment normalization beyond FEC processed data.",
        "rows": row_count,
        "nonmemo_rows": nonmemo_count,
        "missing_recipient_committee_id_rows": missing_id_count,
        "earliest_transaction_date": min(dates) if dates else None,
        "latest_transaction_date": max(dates) if dates else None,
        "nonmemo_line_23_total_usd": str(total.quantize(Decimal("0.01"))),
        "ranking": [{
            "recipient_committee_id": recipient_id,
            "recipient_names_as_filed": sorted(names[recipient_id]),
            "total_usd": str(amount.quantize(Decimal("0.01"))),
            "transaction_count": counts[recipient_id],
        } for recipient_id, amount in sorted(totals.items(), key=lambda x: (-x[1], x[0]))[:10]],
        "page_provenance": manifests,
        "caveat": "This is itemized line-23 contributions for the specified date window, not all PAC spending. Joint fundraising committee receipts do not identify final beneficiary allocations. Later amendments can change historical results. Raw JSON is retained only in the internal cache and must not be distributed with this summary.",
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}: {row_count} rows; ${total:,.2f} non-memo line-23 contributions")


if __name__ == "__main__":
    main()
