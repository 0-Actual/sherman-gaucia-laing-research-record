#!/usr/bin/env python3
"""Verify delivered payload digests, without network access or executing payloads."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def main():
    manifest = json.loads((BASE / 'MANIFEST.json').read_text(encoding='utf-8'))
    checked = 0
    for row in manifest['files']:
        rel = Path(row['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Unsafe manifest path')
        p = BASE / rel
        if not p.is_file() or p.is_symlink():
            raise ValueError('Missing regular payload: ' + str(rel))
        data = p.read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Digest mismatch: ' + str(rel))
        checked += 1
    actual = {str(p.relative_to(BASE)) for p in BASE.rglob('*')
              if p.is_file() and p != BASE / 'MANIFEST.json'
              and '__pycache__' not in p.parts}
    expected = {r['path'] for r in manifest['files']}
    if actual != expected:
        raise ValueError('Unexpected or missing payload files')
    print(f'PASS: {checked} payload byte counts and SHA-256 digests')
    print('Integrity only: no owner signature or source-truth certification.')

if __name__ == '__main__':
    main()
