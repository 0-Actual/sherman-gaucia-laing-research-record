"""Copy and verify the selected upstream files into an isolated review folder."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path('reproduction'))
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    source=args.checkout.resolve()
    output=args.output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error('output must be absent or an empty directory')
    if output==source or source in output.parents:
        parser.error('output must be outside the source checkout')
    manifest=json.loads((here/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    verified=[]
    for entry in manifest['files']:
        relative=Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe source path')
        data=(source/relative).read_bytes()
        digest=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        if len(data)!=entry['bytes'] or digest!=entry['git_blob_sha1']:
            raise ValueError(f'source identity mismatch: {relative}')
        verified.append((relative,data))
    if len(verified)!=33:
        raise ValueError('unexpected source population')
    output.mkdir(parents=True,exist_ok=True)
    for edition in ('upstream','candidate'):
        for relative,data in verified:
            destination=output/edition/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(data)
    for name in ('setup-tests.cjs','prepare-candidate.cjs',
                 'output-lines.test.ts','output-lines-integration.test.ts'):
        shutil.copyfile(here/name,output/name)
    (output/'tools').mkdir()
    shutil.copyfile(here/'tooling-package.json',output/'tools/package.json')
    shutil.copyfile(here/'tooling-package-lock.json',output/'tools/package-lock.json')
    print(f'Verified {len(verified)} source files; prepared {output}')

if __name__=='__main__':
    main()
