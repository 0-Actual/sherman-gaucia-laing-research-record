"""Prepare the pinned Git inventory without checking out or executing upstream code."""
from pathlib import Path
import argparse
import json
import subprocess

PIN = '1581d4cbdd69a0faf34b2089614fe2a814316a6a'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--git', default='git')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent/'audit')
    args = parser.parse_args()
    prefix = [args.git, '-C', str(args.repository)]
    actual = subprocess.check_output(prefix+['rev-parse', '--verify', PIN+'^{commit}']).decode().strip()
    if actual != PIN:
        raise RuntimeError('Pinned commit did not resolve exactly.')
    raw = subprocess.check_output(prefix+['ls-tree', '-r', '-z', PIN])
    rows = []
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, typ, blob = meta.decode('ascii').split()
        if typ != 'blob' or mode not in {'100644', '100755'}:
            raise RuntimeError('Unsupported tree entry: '+path.decode('utf-8'))
        rows.append(dict(path=path.decode('utf-8'), mode=mode, type=typ, git_blob=blob))
    if len(rows) != 133956 or len({r['path'] for r in rows}) != len(rows):
        raise RuntimeError('Pinned inventory count or path uniqueness mismatch.')
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output/'FILE_INVENTORY.json'
    if destination.exists():
        raise FileExistsError('Use a fresh output directory; do not overwrite evidence.')
    destination.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(commit=PIN, files=len(rows), destination=str(destination))))


if __name__ == '__main__':
    main()
