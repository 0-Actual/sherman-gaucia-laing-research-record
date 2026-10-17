import importlib.util,json,hashlib,tempfile,unittest,zipfile
from pathlib import Path
p=Path(__file__).with_name('verify_release.py')
s=importlib.util.spec_from_file_location('verifier',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class ReleaseVerification(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent);self.root=Path(self.tmp.name)
        (self.root/'data.txt').write_bytes(b'research\n');self.manifest()
    def tearDown(self):self.tmp.cleanup()
    def manifest(self):
        files=[]
        for f in self.root.iterdir():
            if f.name=='MANIFEST.json':continue
            b=f.read_bytes();files.append({'path':f.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        (self.root/'MANIFEST.json').write_text(json.dumps({'files':files}),encoding='utf-8')
    def test_valid_reference(self):
        h=v.digest((self.root/'MANIFEST.json').read_bytes());self.assertEqual(v.verify(self.root,h)['result'],'PASS')
    def test_changed_payload(self):
        (self.root/'data.txt').write_bytes(b'changed\n')
        with self.assertRaises(ValueError):v.verify(self.root)
    def test_changed_manifest_against_reference(self):
        h=v.digest((self.root/'MANIFEST.json').read_bytes());(self.root/'data.txt').write_bytes(b'changed');self.manifest()
        with self.assertRaises(ValueError):v.verify(self.root,h)
    def test_escape_path(self):
        obj=json.loads((self.root/'MANIFEST.json').read_text());obj['files'][0]['path']='../data.txt';(self.root/'MANIFEST.json').write_text(json.dumps(obj))
        with self.assertRaises(ValueError):v.verify(self.root)
    def test_extra_file(self):
        (self.root/'unexpected.txt').write_text('unexpected')
        with self.assertRaises(ValueError):v.verify(self.root)
    def test_duplicate_row(self):
        obj=json.loads((self.root/'MANIFEST.json').read_text());obj['files']*=2;(self.root/'MANIFEST.json').write_text(json.dumps(obj))
        with self.assertRaises(ValueError):v.verify(self.root)
    def test_archive_tamper(self):
        with zipfile.ZipFile(self.root/'data.zip','w') as z:
            z.writestr('x.txt','actual');z.writestr('RELEASE_CONTENT_MANIFEST.json',json.dumps({'files':[{'path':'x.txt','bytes':6,'sha256':'0'*64}]}))
        self.manifest()
        with self.assertRaises(ValueError):v.verify(self.root)
    def test_unlisted_archive_member(self):
        with zipfile.ZipFile(self.root/'data.zip','w') as z:
            z.writestr('secret.txt','unexpected');z.writestr('RELEASE_CONTENT_MANIFEST.json','{"files":[]}')
        self.manifest()
        with self.assertRaises(ValueError):v.verify(self.root)

    def test_manifest_shape(self):
        for value in ([],None,42,{'files':{}},{'files':[None]}):
            (self.root/'MANIFEST.json').write_text(json.dumps(value))
            with self.assertRaises(ValueError):v.verify(self.root)

    def test_manifest_size_limit(self):
        from unittest.mock import patch
        with patch.object(v,'MAX_MANIFEST_BYTES',16):
            with self.assertRaises(ValueError):v.verify(self.root)

    def test_oversized_payload_rejected_before_opening_it(self):
        from unittest.mock import patch
        original=Path.open;payload=self.root/'data.txt'
        payload.write_bytes(b'x'*100)
        def guarded(path,*args,**kwargs):
            if path==payload:self.fail('Oversized payload must not be opened')
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):
            with self.assertRaises(ValueError):v.verify(self.root)

    def test_nested_git_directory_is_not_hidden_from_inventory(self):
        p=self.root/'nested/.git/extra.txt';p.parent.mkdir(parents=True);p.write_text('unlisted')
        with self.assertRaises(ValueError):v.verify(self.root)

    def test_manifest_symlink_is_rejected(self):
        from unittest.mock import patch
        original=Path.is_symlink
        with patch.object(Path,'is_symlink',lambda p:True if p.name=='MANIFEST.json' else original(p)):
            with self.assertRaises(ValueError):v.verify(self.root)

    def test_stream_growth_is_rejected(self):
        import io
        with self.assertRaises(ValueError):v.hash_stream(io.BytesIO(b'abc'),2)

    def test_archive_link_member_is_rejected(self):
        body=b'target';row={'path':'alias','bytes':len(body),'sha256':v.digest(body)}
        with zipfile.ZipFile(self.root/'data.zip','w') as z:
            info=zipfile.ZipInfo('alias');info.create_system=3;info.external_attr=0o120777<<16
            z.writestr(info,body);z.writestr('RELEASE_CONTENT_MANIFEST.json',json.dumps({'files':[row]}))
        self.manifest()
        with self.assertRaises(ValueError):v.verify(self.root)

if __name__=='__main__':unittest.main(verbosity=2)

