#!/usr/bin/env python3
"""Reproduce selected aggregate source totals using Poppler pdftotext."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 extract_source_totals.py source.pdf')
    pdf = Path(sys.argv[1])
    source_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'],
                          capture_output=True, check=True, text=True).stdout
    pattern = re.compile(r'\$([0-9,]+)\s+Q([1-4])[-\s]*(20[0-9]{2})')
    totals = defaultdict(int)
    quarters = defaultdict(lambda: defaultdict(int))
    counts = defaultdict(int)
    for amount, quarter, year in pattern.findall(text):
        if year not in ('2020', '2025'):
            continue
        value = int(amount.replace(',', ''))
        totals[year] += value
        quarters[year][quarter] += value
        counts[year] += 1
    out = {'source_sha256': source_hash, 'year_totals_usd': dict(totals),
           'quarter_totals_usd': {y: dict(v) for y,v in quarters.items()},
           'row_counts': dict(counts), 'method': 'Poppler pdftotext -layout; optional quarter/year separator',
           'scope': 'selected 2020/2025 rows, no recipient text redistributed'}
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
