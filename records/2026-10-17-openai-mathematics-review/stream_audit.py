"""Read every pinned repository file once; preserve source and review states.

Static/lexical evidence only. Never executes downloaded source or declares proofs valid.
All downloaded material retains its upstream license.
"""
from __future__ import annotations
import collections, datetime, hashlib, json, re, sqlite3, tarfile, time, urllib.request, zlib, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'audit'
PIN='1581d4cbdd69a0faf34b2089614fe2a814316a6a'
ARCHIVE=ROOT/f'openai-math-{PIN}.tar.gz'
URL=f'https://codeload.github.com/openai/math/tar.gz/{PIN}'
DB=OUT/'REVIEW.sqlite3'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def download():
    if ARCHIVE.exists():
        print('Using retained pinned archive.',flush=True)
        return
    partial=ARCHIVE.with_suffix('.tar.gz.part')
    if partial.exists():
        raise RuntimeError('An interrupted download exists; preserve/reconcile it before retrying.')
    print(f'Downloading pinned public archive: {URL}',flush=True)
    start=now(); h=hashlib.sha256(); n=0; report=0
    request=urllib.request.Request(URL,headers={'User-Agent':'Repository-review/1.0'})
    with urllib.request.urlopen(request,timeout=120) as response,partial.open('wb') as dest:
        for block in iter(lambda:response.read(1024*1024),b''):
            dest.write(block);h.update(block);n+=len(block)
            if n-report>=32*1024*1024:
                print(f'Archive received: {n//(1024*1024)} MiB',flush=True);report=n
    partial.replace(ARCHIVE)
    dump('ARCHIVE_RECEIPT.json',dict(url=URL,commit=PIN,start_utc=start,downloaded_utc=now(),bytes=n,sha256=h.hexdigest()))
    print(f'Archive saved: {n} bytes',flush=True)

def main():
    OUT.mkdir(exist_ok=True)
    expected=json.loads((OUT/'FILE_INVENTORY.json').read_text(encoding='utf-8'))
    expected={row['path']:row for row in expected}
    download()
    con=sqlite3.connect(DB)
    con.executescript('''
    CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY,git_blob TEXT,sha256 TEXT,bytes INTEGER,physical_lines INTEGER,content_state TEXT,semantic_state TEXT);
    CREATE TABLE IF NOT EXISTS sources(git_blob TEXT PRIMARY KEY,compressed_utf8 BLOB);
    CREATE TABLE IF NOT EXISTS imports(source TEXT,line INTEGER,module TEXT,target TEXT,internal INTEGER);
    CREATE TABLE IF NOT EXISTS markers(path TEXT,line INTEGER,kind TEXT,context TEXT,classification TEXT);
    CREATE TABLE IF NOT EXISTS exceptions(path TEXT,kind TEXT,detail TEXT);
    CREATE TABLE IF NOT EXISTS run_metadata(key TEXT PRIMARY KEY,value TEXT);
    ''')
    con.execute('INSERT OR REPLACE INTO run_metadata VALUES (?,?)',('commit',PIN));con.commit()
    completed=dict(con.execute('SELECT path,git_blob FROM files'))
    checked=set(); seen=0; started=time.monotonic(); reused=0
    with tarfile.open(ARCHIVE,'r|gz') as archive:
        for member in archive:
            archive.members.clear()
            if not member.isfile(): continue
            path=member.name.split('/',1)[1]
            row=expected.get(path)
            if row is None:
                con.execute('INSERT INTO exceptions VALUES (?,?,?)',(path,'not_in_pinned_tree',member.type.decode(errors='replace')));continue
            checked.add(path)
            if completed.get(path)==row['git_blob']:
                reused+=1;continue
            if seen % 1000 == 0 and shutil.disk_usage(ROOT).free < 256*1024*1024:
                con.commit()
                raise RuntimeError('Stopped at the local disk reserve; completed file evidence remains resumable.')
            reader=archive.extractfile(member)
            data=reader.read()
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            sha256=hashlib.sha256(data).hexdigest()
            if blob!=row['git_blob']:
                raise RuntimeError(f'Pinned Git identity mismatch: {path}')
            ext=Path(path).suffix.lower(); state='binary_identity_verified';lines=None
            if ext not in {'.pdf','.png'}:
                try:
                    text=data.decode('utf-8')
                except UnicodeDecodeError as error:
                    state='non_utf8_identity_verified'
                    con.execute('INSERT INTO exceptions VALUES (?,?,?)',(path,'non_utf8',str(error)))
                else:
                    state='lexically_scanned_not_semantically_reviewed';lines=len(text.splitlines())
                    # Keep commonly reviewed text readily queryable; the complete archive
                    # remains the source for unselected large proof modules.
                    cache_source = (ext in {'.md','.json','.yaml','.yml','.bib','.py'} or
                                    '/ComparatorChallenges/' in path or
                                    any(term in path for term in ['Heisenberg','Bloch','bloch','magnetization','DirichletL/Nonvanishing','DirichletL/Detector/FinalAssembly']))
                    if cache_source:
                        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?)',(blob,zlib.compress(data,level=1)))
                    if ext=='.lean':
                        edge_rows=[];marker_rows=[]
                        for n,line in enumerate(text.splitlines(),1):
                            match=re.match(r'\s*(?:public\s+|meta\s+)?import\s+(.+)',line)
                            if match:
                                for module in match[1].split('--')[0].split():
                                    target='lean/'+module.replace('.','/')+'.lean'
                                    edge_rows.append((path,n,module,target,int(target in expected)))
                            for kind in set(re.findall(r'\b(sorry|admit|axiom|unsafe)\b',line)):
                                classification='comparison_target_candidate' if '/ComparatorChallenges/' in path else 'lexical_candidate_not_confirmed_defect'
                                marker_rows.append((path,n,kind,line[:500],classification))
                        con.executemany('INSERT INTO imports VALUES (?,?,?,?,?)',edge_rows)
                        con.executemany('INSERT INTO markers VALUES (?,?,?,?,?)',marker_rows)
                    elif ext=='.json':
                        try: json.loads(text)
                        except Exception as error: con.execute('INSERT INTO exceptions VALUES (?,?,?)',(path,'json_parse',str(error)))
            con.execute('INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)',(path,blob,sha256,len(data),lines,state,'not_reviewed'))
            seen+=1
            if seen%1000==0:
                con.commit();print(f'Files checked: {seen}; prior matched rows reused: {reused}',flush=True)
    for path in expected.keys()-checked:
        con.execute('INSERT INTO exceptions VALUES (?,?,?)',(path,'absent_from_archive',expected[path]['type']))
    con.executescript('CREATE INDEX IF NOT EXISTS imports_source ON imports(source); CREATE INDEX IF NOT EXISTS imports_target ON imports(target); CREATE INDEX IF NOT EXISTS markers_path ON markers(path);')
    con.commit()
    summary=dict(commit=PIN,completed_utc=now(),new_files_checked=seen,reused_files=reused,
       expected_tree_files=len(expected),archive_files_seen=len(checked),file_records=con.execute('SELECT count(*) FROM files').fetchone()[0],
       bytes=con.execute('SELECT sum(bytes) FROM files').fetchone()[0],
       physical_text_lines=con.execute('SELECT sum(physical_lines) FROM files').fetchone()[0],
       content_states=dict(con.execute('SELECT content_state,count(*) FROM files GROUP BY content_state')),
       distinct_text_blobs=con.execute('SELECT count(*) FROM sources').fetchone()[0],
       import_edges=con.execute('SELECT count(*) FROM imports').fetchone()[0],
       lexical_markers=con.execute('SELECT count(*) FROM markers').fetchone()[0],
       exceptions=con.execute('SELECT count(*) FROM exceptions').fetchone()[0],
       processing_seconds=round(time.monotonic()-started,2),
       semantic_proof_review_complete=False,lean_build_run=False,comparator_run=False,
       limits=['Lexical markers can be comments, permitted axioms or intended comparison targets; none is automatically a defect.',
               'Archived versions, duplicate bytes and current manuscripts are different populations.',
               'Full file-byte coverage is not full semantic review or a correctness certificate.'])
    dump('FULL_SCAN_SUMMARY.json',summary)
    con.execute('INSERT OR REPLACE INTO run_metadata VALUES (?,?)',('complete_summary',json.dumps(summary)))
    con.commit();con.close();print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
