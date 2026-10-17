"""Verify a downloaded release without executing or extracting its research code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

MAX_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_ENTRIES = 100000

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Invalid relative name')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or value == '.':
        raise ValueError('Unsafe relative name')
    return value

def check_rows(rows):
    if not isinstance(rows, list) or len(rows) > MAX_ENTRIES:
        raise ValueError('Expected a bounded file list')
    seen = set()
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Expected a file record')
        name = safe_path(row.get('path'))
        if name.casefold() in seen:
            raise ValueError('Duplicate/colliding file name')
        seen.add(name.casefold())
        size = row.get('bytes')
        if type(size) is not int or not 0 <= size <= MAX_FILE_BYTES:
            raise ValueError('Invalid file size')
        value = row.get('sha256')
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Invalid SHA-256')
        total += size
    if total > MAX_TOTAL_BYTES:
        raise ValueError('Declared contents exceed verifier limit')
    return total

def parse_manifest(data):
    obj = json.loads(data)
    if not isinstance(obj, dict) or 'files' not in obj:
        raise ValueError('Expected a manifest object with a file list')
    check_rows(obj['files'])
    return obj

def checked_path(root, name, limit):
    path = root / safe_path(name)
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('File points outside the release')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
        raise ValueError('File is not regular or exceeds verifier limit: ' + name)
    return path

def bounded_read(stream, limit):
    data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Input exceeds verifier limit')
    return data

def hash_stream(stream, expected_size):
    h = hashlib.sha256()
    total = 0
    while True:
        chunk = stream.read(min(1024 * 1024, expected_size - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > expected_size:
            raise ValueError('Input exceeds declared size')
        h.update(chunk)
    if total != expected_size:
        raise ValueError('Input size does not match manifest')
    return h.hexdigest()

def verify(root, expected_manifest=None):
    root = Path(root).resolve()
    manifest_path = checked_path(root, 'MANIFEST.json', MAX_MANIFEST_BYTES)
    with manifest_path.open('rb') as stream:
        data = bounded_read(stream, MAX_MANIFEST_BYTES)
    if expected_manifest and digest(data) != expected_manifest:
        raise ValueError('Manifest does not match the independent reference')
    rows = parse_manifest(data)['files']
    checked = archive_files = archive_bytes = 0
    for row in rows:
        name = row['path']
        path = checked_path(root, name, row['bytes'])
        with path.open('rb') as stream:
            if hash_stream(stream, row['bytes']) != row['sha256']:
                raise ValueError('File mismatch: ' + name)
        checked += 1
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                names = [x.filename for x in infos]
                if len(names) > MAX_ENTRIES or len(set(names)) != len(names):
                    raise ValueError('Duplicate or excessive archive members')
                if 'RELEASE_CONTENT_MANIFEST.json' not in names:
                    raise ValueError('Missing collection manifest')
                for info in infos:
                    safe_path(info.filename)
                    if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                        raise ValueError('Archive member is not a regular payload file')
                meta = archive.getinfo('RELEASE_CONTENT_MANIFEST.json')
                if meta.file_size > MAX_MANIFEST_BYTES:
                    raise ValueError('Oversized collection manifest')
                with archive.open(meta) as stream:
                    members = parse_manifest(bounded_read(stream, MAX_MANIFEST_BYTES))['files']
                archive_bytes += check_rows(members)
                if archive_bytes > MAX_TOTAL_BYTES or archive_files + len(members) > MAX_ENTRIES:
                    raise ValueError('Combined archive contents exceed verifier limit')
                if set(names) != {x['path'] for x in members} | {'RELEASE_CONTENT_MANIFEST.json'}:
                    raise ValueError('Unexpected/missing archive members')
                for member in members:
                    info = archive.getinfo(member['path'])
                    if info.file_size != member['bytes']:
                        raise ValueError('Archive size mismatch')
                    with archive.open(info) as stream:
                        if hash_stream(stream, member['bytes']) != member['sha256']:
                            raise ValueError('Archive content mismatch')
                    archive_files += 1
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
              if p.is_file() and p.relative_to(root).parts[0] != '.git'}
    if actual != {x['path'] for x in rows} | {'MANIFEST.json'}:
        raise ValueError('Unexpected/missing release files; use a clean download directory')
    return {'result': 'PASS', 'manifest_sha256': digest(data),
            'top_level_payload_files': checked, 'archive_payload_members': archive_files,
            'meaning': 'Integrity relative to the supplied manifest; not authorship, historical time or scientific validity.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--manifest-sha256', help='Reference from a separately verified publication receipt')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.directory, args.manifest_sha256), indent=2))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, zipfile.BadZipFile) as error:
        parser.exit(1, 'Verification failed: ' + str(error) + '\n')
