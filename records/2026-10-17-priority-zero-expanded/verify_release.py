"""Check a downloaded release against its manifest. Does not execute research code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Invalid relative name')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value:
        raise ValueError('Unsafe relative name')
    return value

def check_rows(rows):
    seen=set()
    for row in rows:
        name=safe_path(row['path'])
        if name.casefold() in seen:
            raise ValueError('Duplicate/colliding file name')
        seen.add(name.casefold())
        if type(row['bytes']) is not int or not 0 <= row['bytes'] <= 268435456:
            raise ValueError('Invalid file size')
        if not isinstance(row['sha256'],str) or len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256']):
            raise ValueError('Invalid SHA-256')
    if sum(row['bytes'] for row in rows)>1073741824:
        raise ValueError('Declared contents exceed verifier limit')

def verify(root, expected_manifest=None):
    root=Path(root).resolve()
    data=(root/'MANIFEST.json').read_bytes()
    if expected_manifest and digest(data)!=expected_manifest:
        raise ValueError('Manifest does not match the independent reference')
    manifest=json.loads(data)
    rows=manifest['files'];check_rows(rows)
    checked=0;archive_files=0
    for row in rows:
        name=safe_path(row['path']);path=root/name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('File points outside the release')
        body=path.read_bytes()
        if len(body)!=row['bytes'] or digest(body)!=row['sha256']:
            raise ValueError('File mismatch: '+name)
        checked+=1
        if path.suffix.lower()=='.zip':
            with zipfile.ZipFile(path) as archive:
                infos=archive.infolist();names=[x.filename for x in infos]
                if len(set(names))!=len(names):raise ValueError('Duplicate archive member')
                if 'RELEASE_CONTENT_MANIFEST.json' not in names:raise ValueError('Missing collection manifest')
                meta=archive.getinfo('RELEASE_CONTENT_MANIFEST.json')
                if meta.file_size>16777216:raise ValueError('Oversized collection manifest')
                members=json.loads(archive.read(meta))['files'];check_rows(members)
                if set(names)!={x['path'] for x in members}|{'RELEASE_CONTENT_MANIFEST.json'}:
                    raise ValueError('Unexpected/missing archive members')
                for member in members:
                    info=archive.getinfo(member['path'])
                    if info.file_size!=member['bytes']:raise ValueError('Archive size mismatch')
                    raw=archive.read(info)
                    if digest(raw)!=member['sha256']:raise ValueError('Archive content mismatch')
                    archive_files+=1
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
    if actual!={x['path'] for x in rows}|{'MANIFEST.json'}:
        raise ValueError('Unexpected/missing release files; use a clean download directory')
    return {'result':'PASS','manifest_sha256':digest(data),'top_level_payload_files':checked,'archive_payload_members':archive_files,
            'meaning':'Integrity relative to the supplied manifest; not authorship, historical time or scientific validity.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--manifest-sha256',help='Reference obtained independently, such as from the verified publication receipt')
    args=parser.parse_args()
    try:print(json.dumps(verify(args.directory,args.manifest_sha256),indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile) as error:parser.exit(1,'Verification failed: '+str(error)+'\n')
