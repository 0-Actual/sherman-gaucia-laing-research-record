from pathlib import Path
import json,csv,io,hashlib
from decimal import Decimal
from collections import defaultdict
b=Path(__file__).resolve().parent
a=json.loads((b/'cjc-payment-analysis.json').read_text(encoding='utf-8'))
for s in a['snapshots']:
 m=s['summary'];raw=(b/m['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256']
 rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));values=[];groups=defaultdict(int)
 for r in rows:
  if not any(x.strip() for x in r):continue
  if 'year2' in m['file']:
   if len(r)<6 or not r[1].strip() or not r[2].strip() or '$' not in r[5]:continue
   name,money=r[2],r[5]
  else:name,money=r[1],r[4]
  cents=int(Decimal(money.strip().replace('$','').replace(',','').replace(' ',''))*100);values.append(cents);groups[name]+=cents
 assert len(values)==m['payment_rows'] and sum(values)==m['sum_cents']
 top=sum(sorted(groups.values(),reverse=True)[:10]);assert top==m['top_10_sum_cents']
 print(m['file'],len(values),'rows',str(Decimal(sum(values))/100),'CAD','top10 percent',top/sum(values)*100)
print('Original source bytes and arithmetic match; no files changed.')
