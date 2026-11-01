#!/usr/bin/env python3
"""Refetch and verify 11 Google LD-2 filings using only Python's standard library.

Run: python verify_google_ld2.py --output-dir PATH
Writes CSV/JSON observations and SHA-256 hashes; does not retain raw HTML.
Hashes identify the bytes retrieved during this run. The official live renderer
may subsequently change formatting or displayed names, changing those hashes.
"""
import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path

INPUTS = [
    (2020, 1, 1800000, "c240fbf5-2122-417f-bffd-a23c3bcd6089"),
    (2020, 2, 1690000, "5756a20c-4639-49e2-9165-f0667b361579"),
    (2020, 3, 1930000, "40df1c3a-c0d4-42cd-898a-e4ff6dac3eab"),
    (2020, 4, 2110000, "65749c45-3697-492e-8430-520cfa2fd6ad"),
    (2025, 1, 3010000, "d1fc7251-32b4-4f44-b803-6888f5e8aa05"),
    (2025, 2, 3170000, "6e9426dd-f07f-4504-9c0c-369f90ab9f52"),
    (2025, 3, 3570000, "289972fc-977b-4357-a330-f3589a1cb786"),
    (2025, 4, 3350000, "25432e67-591b-4e9f-85ae-4437532f7e7e"),
    (2026, 1, 2860000, "534610dc-d423-47a6-819e-26409b01ea6c"),
    (2026, 2, 3570000, "0676fd59-1d30-4323-aad2-83e03d2ff407"),
    (2026, 3, 3230000, "08837d92-519d-4607-b01a-9186702f755c"),
]


def plain(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    value = value.replace("\u200b", "").replace("\ufeff", "")
    return re.sub(r"\s+", " ", value).strip()


def fetch_check(item):
    year, quarter, expected_amount, filing_uuid = item
    url = f"https://lda.gov/filings/public/filing/{filing_uuid}/print/"
    req = urllib.request.Request(url, headers={"User-Agent": "Public-record verification/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        body = response.read()
        final_url = response.geturl()
    raw = body.decode("utf-8")
    text = plain(raw)
    report_section = raw.split("TYPE OF REPORT", 1)[1].split("INCOME OR EXPENSES", 1)[0]
    report_text = plain(report_section)
    observed_year = int(re.search(r"8\. Year (\d{4})", report_text).group(1))
    quarters = {
        int(q): "checked" in attrs
        for q, attrs in re.findall(r"Q([1-4])\s*\([^)]*\)\s*<input([^>]*)>", report_section)
    }
    assert observed_year == year, (item, observed_year)
    assert quarters == {q: q == quarter for q in range(1, 5)}, (item, quarters)
    methods = {
        method: "checked" in attrs
        for attrs, method in re.findall(
            r"<input([^>]*)>\s*<span[^>]*>Method ([ABC])", raw
        )
    }
    assert methods == {"A": True, "B": False, "C": False}, (item, methods)
    money_section = raw.split("INCOME OR EXPENSES", 1)[1].split("14. REPORTING", 1)[0]
    amounts = re.findall(r"<div[^>]*>\s*[\u200b\ufeff]*([\d,]+\.\d{2})\s*</div>", money_section)
    assert len(amounts) == 1, (item, amounts)
    amount = int(float(amounts[0].replace(",", "")))
    assert amount == expected_amount, (item, amount)
    senate_id = re.search(r"5\. Senate ID#\s*([\d-]+)", text).group(1)
    house_id = re.search(r"6\. House ID#\s*(\d+)", text).group(1)
    assert senate_id == "320510-12" and house_id == "394790000"
    signature_text = text.split("Digitally Signed By:", 1)[1]
    signature_stamp = re.search(r"Date (\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M)", signature_text).group(1)
    signature_dt = dt.datetime.strptime(signature_stamp, "%m/%d/%Y %I:%M:%S %p")
    return {
        "year": year,
        "quarter": quarter,
        "amount_usd": amount,
        "method": "A",
        "method_b_checked": False,
        "method_c_checked": False,
        "filing_date": signature_dt.date().isoformat(),
        "filing_date_basis": "digital signature date shown on official filing",
        "signature_datetime_as_displayed": signature_stamp,
        "senate_id": senate_id,
        "house_id": house_id,
        "filing_uuid": filing_uuid,
        "source_url": url,
        "retrieved_url": final_url,
        "source_html_sha256": hashlib.sha256(body).hexdigest(),
        "source_html_bytes": len(body),
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch_check, INPUTS))
    totals = {str(year): sum(r["amount_usd"] for r in rows if r["year"] == year)
              for year in (2020, 2025, 2026)}
    assert totals == {"2020": 7530000, "2025": 13100000, "2026": 9660000}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "Self-registered Google federal LD-2 filings: full 2020, full 2025, 2026 Q1-Q3 only.",
        "cutoff": "2026-10-31",
        "amount_caution": "Good-faith LDA expense estimates rounded to nearest $10,000; do not add outside-firm receipts or lobbying portions of dues again.",
        "name_caution": "Current renderer can update historical headers; these observations do not establish a legal-name-change date.",
        "hash_caution": "SHA-256 hashes are of exact live source HTML bytes at retrieval; subsequent official rendering changes can change hashes.",
        "filing_date_caution": "Digital signature date from each filing, not an independently parsed official posting timestamp.",
        "totals_usd": totals,
        "rows": rows,
    }
    json_path = args.output_dir / "google_ld2_quarter_inputs.json"
    csv_path = args.output_dir / "google_ld2_quarter_inputs.csv"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"filings_verified": len(rows), "totals_usd": totals,
                      "files": [str(json_path), str(csv_path)]}))


if __name__ == "__main__":
    main()
