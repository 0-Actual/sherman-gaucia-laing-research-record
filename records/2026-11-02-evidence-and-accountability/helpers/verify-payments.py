"""Read-only payment verifier. Ordinary exceptions remain effective with Python -O."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys

sys.dont_write_bytecode = True


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def load_json(path):
    def invalid(value):
        raise VerificationError("Nonfinite JSON number: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object, parse_constant=invalid)


def cents(value):
    text = value.strip().replace("$", "").replace(",", "").replace(" ", "").replace("\u00a0", "")
    require(re.fullmatch(r"-?\d+(?:\.\d{1,2})?", text) is not None,
            "Malformed or fractional-cent payment")
    try:
        number = Decimal(text) * 100
    except InvalidOperation as error:
        raise VerificationError("Invalid payment number") from error
    require(number == number.to_integral_value(), "Fractional cent would be truncated")
    return int(number)


def verify_payments(root, contract=None):
    root = Path(root).resolve()
    contract = contract or load_json(Path(__file__).with_name("expected-records.json"))
    base = root / "financial" / "international-followthrough"
    analysis = load_json(base / "cjc-payment-analysis.json")
    snapshots = analysis.get("snapshots")
    expected = {row["file"]: row for row in contract["paymentSnapshots"]}
    require(isinstance(snapshots, list) and len(snapshots) == len(expected),
            "payments.snapshot_count: expected both original CSV snapshots")
    seen, results = set(), []
    for snapshot in snapshots:
        require(isinstance(snapshot, dict) and isinstance(snapshot.get("summary"), dict),
                "Malformed payment snapshot")
        summary = snapshot["summary"]
        name = summary.get("file")
        require(name in expected and name not in seen, "Unknown or duplicate payment snapshot")
        seen.add(name)
        pin = expected[name]
        file_path = base / name
        require(not file_path.is_symlink() and file_path.is_file(), "Original payment CSV missing")
        raw = file_path.read_bytes()
        actual_hash = hashlib.sha256(raw).hexdigest()
        require(actual_hash == pin["sha256"] == summary.get("sha256"),
                "Original payment source SHA-256 differs")
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
        groups, payments, total_rows = defaultdict(int), [], []
        year_two = name == "cjc-year2-2026-08-19.csv"
        for line_number, row in enumerate(rows, 1):
            if not any(cell.strip() for cell in row):
                continue
            if year_two:
                require(len(row) >= 6, "Malformed year-two CSV row")
                if line_number == 1:
                    require(row[0].strip() == "SY2 Application ID", "Unexpected year-two header")
                    continue
                legal_name, amount_text = row[2], row[5]
                if not legal_name.strip():
                    require(not any(cell.strip() for cell in row[:5]) and "$" in amount_text,
                            "Unexpected unnamed year-two row")
                    total_rows.append(cents(amount_text))
                    continue
            else:
                require(len(row) >= 5 and row[1].strip(), "Malformed year-one CSV row")
                legal_name, amount_text = row[1], row[4]
            require(legal_name.strip() and amount_text.strip(), "Malformed named payment row")
            amount = cents(amount_text)
            payments.append({"source_row": line_number, "legal_name": legal_name, "amount_cents": amount})
            groups[legal_name] += amount
        total = sum(row["amount_cents"] for row in payments)
        top = sum(sorted(groups.values(), reverse=True)[:10])
        require(len(rows) == summary.get("source_rows"), "Payment source row count differs")
        require(len(payments) == pin["payment_rows"] == summary.get("payment_rows"),
                "payments.payment_rows: original named rows omitted or added")
        require(total == pin["sum_cents"] == summary.get("sum_cents"),
                "payments.sum_cents: payment sum differs")
        require(top == pin["top_10_sum_cents"] == summary.get("top_10_sum_cents"),
                "Payment top-ten sum differs")
        require(summary.get("currency") == pin["currency"] == "CAD", "Payment currency changed")
        require(Decimal(summary["sum_CAD"]) == Decimal(total) / 100, "CAD/cents display differs")
        require(total > 0 and math.isclose(summary["top_10_share_percent"], top / total * 100,
                                          rel_tol=1e-12, abs_tol=1e-9),
                "Payment top-ten percentage differs")
        require(all(value == total for value in total_rows), "CSV declared total differs")
        recorded = snapshot.get("payments")
        require(isinstance(recorded, list) and len(recorded) == len(payments),
                "payments.detail_rows: recorded recipient rows omitted")
        for actual, record in zip(payments, recorded):
            require(all(record.get(key) == value for key, value in actual.items()),
                    "Recorded recipient row differs from its original CSV")
        results.append({"file": name, "sha256": actual_hash, "payment_rows": len(payments),
                        "sum_cents": total, "top_10_sum_cents": top, "currency": "CAD"})
    require(seen == set(expected), "Missing payment snapshot")
    return {"csv_files": len(results), "payment_rows": sum(r["payment_rows"] for r in results),
            "snapshots": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        result = verify_payments(arguments.root)
        print(json.dumps({"schema": "qel.payment-verification.v2", "status": "PASS", **result},
                         ensure_ascii=False, sort_keys=True))
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
