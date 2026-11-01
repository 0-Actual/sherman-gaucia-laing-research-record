from pathlib import Path
import hashlib,json,math,subprocess,sys
from datetime import date
b=Path(__file__).resolve().parent
r=lambda p:json.loads((b/p).read_text(encoding='utf-8'))
m=r('publication-manifest.json')
for f in m['files']:
 p=b/f['path'];raw=p.read_bytes();assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],f['path']
t=r('purchases.json')['transactions'];assert len(t)==13 and len({x['id'] for x in t})==13
p=r('prior-work/corrected-comparisons.json')['comparisons'];assert len(p)==28
ids={x['id'] for x in p}
for row in r('correlation-matrix.json')['rows']:
 assert set(row['comparison_ids'])<=ids
 for a in row['owner_stages']:
  if a['calendar_day_gap'] is not None:assert (date.fromisoformat(a['announcement_date'][:10])-date.fromisoformat(a['recorded_date'][:10])).days==a['calendar_day_gap']
for c in r('calculation-index.json')['financial']:
 a=c['inputs'];op=c['operation']
 v=sum(a) if op=='sum' else a[0]-a[1] if op=='subtract' else a[0]/a[1]*100 if op in ('ratio_percent','percent') else (a[0]-a[1])/100*a[2] if op=='spread' else a[0]*a[1] if op=='multiply' else a[0]/a[1] if op=='divide' else None
 assert v is not None and math.isclose(v,c['result'],rel_tol=1e-12,abs_tol=1e-6),c['id']
for c in r('calculation-index.json')['slavery']:
 a,z=c['inputs'];op=c['operation'];v=a/z*100 if op=='percent' else a-z if op=='subtract' else (a-z)/z*100 if op=='growth_percent' else a/z
 assert math.isclose(v,c['result'],rel_tol=1e-12),c['id']
assert 25000*20==r('calculation-index.json')['procurement_face_value']['result']
subprocess.run([sys.executable,'-B',str(b/'financial/international-followthrough/verify-payments.py')],check=True)
print('PASS: '+str(len(m['files']))+' payload identities; 13 purchase rows; 28 prior comparison rows; 26 arithmetic results; recorded-day gaps; 2 original payment CSVs.')
