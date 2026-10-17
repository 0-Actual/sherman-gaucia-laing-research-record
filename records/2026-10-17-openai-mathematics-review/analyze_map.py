"""Reconcile the complete byte inventory with claims and formal-check interfaces."""
import collections, json, re, sqlite3, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'audit'
con=sqlite3.connect(OUT/'REVIEW.sqlite3')
con.row_factory=sqlite3.Row
def source(path):
    row=con.execute('SELECT compressed_utf8 FROM sources JOIN files USING(git_blob) WHERE path=?',(path,)).fetchone()
    if row is None: raise KeyError(path)
    return zlib.decompress(row[0]).decode('utf-8')
def dump(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

full=json.loads((OUT/'FULL_SCAN_SUMMARY.json').read_text(encoding='utf-8'))
assert full['file_records']==full['expected_tree_files']==full['archive_files_seen']
paths={r[0] for r in con.execute('SELECT path FROM files')}
contents=source('CONTENTS.md')
formal=source('lean/formalization.yaml')
source_section=formal.split('\nsources:\n',1)[1].split('\nrelated_formalizations:',1)[0]
formal_sources={m.strip().strip('"\'').removeprefix('../') for m in re.findall(r'^\s+id:\s+(.+)$',source_section,re.M)}
families=[]
starts=list(re.finditer(r'^\*\*(\d{3})\. (.+?)\*\*',contents,re.M))
for n,match in enumerate(starts):
    body=contents[match.end():starts[n+1].start() if n+1<len(starts) else len(contents)]
    papers=re.findall(r'\]\((preprints/[^\n]+?\.pdf)\)',body)
    scope=f'lean/docs/{match[1]}.md'
    scope_papers=[]
    if scope in paths:
        preamble=source(scope).split('\n## Scope',1)[0]
        scope_papers=[p.removeprefix('../../') for p in re.findall(r'\]\((../../preprints/[^\n]+?\.pdf)\)',preamble)]
    row=dict(family=match[1],title=match[2],papers=papers,
        mapped_papers_in_formal_source_list=[p for p in papers if p in formal_sources],
        formal_scope_path=scope if scope in paths else None,
        scope_note_papers=scope_papers,
        status='catalogued_not_whole_family_proof_reviewed')
    families.append(row)
mapped={p for f in families for p in f['papers']}
pdfs={p for p in paths if p.startswith('preprints/') and p.endswith('.pdf')}
scope_sources={p for f in families for p in f['scope_note_papers']}
dump('FAMILY_COVERAGE.json',families)
dump('CATALOGUE_RECONCILIATION.json',dict(families=len(families),paper_links=sum(len(f['papers']) for f in families),unique_papers=len(mapped),
    missing_paper_paths=sorted(mapped-paths),other_preprint_pdfs=sorted(pdfs-mapped),formal_source_paths=len(formal_sources),
    formal_sources_not_in_current_map=sorted(formal_sources-mapped),families_with_some_formal_source=sum(bool(f['mapped_papers_in_formal_source_list']) for f in families),
    scope_note_paper_paths=len(scope_sources),scope_note_paths_not_in_current_map=sorted(scope_sources-mapped),
    scope_note_paths_not_in_yaml_sources=sorted(scope_sources-formal_sources),
    families_with_partial_formal_source_coverage=sum(0<len(f['mapped_papers_in_formal_source_list'])<len(f['papers']) for f in families),
    note='Formal source-list membership is declared coverage, not a locally executed successful proof check. Other PDFs may be withdrawn or prior editions.'))

configs=[];missing=[];axioms=collections.Counter()
for path in sorted(paths):
    if not(path.startswith('lean/ComparatorChallenges/') and path.endswith('.json')):continue
    try:data=json.loads(source(path))
    except Exception as e:
        missing.append(dict(path=path,reason='parse_or_cache',detail=str(e)));continue
    if not isinstance(data,dict) or 'solution_module' not in data:continue
    modules={key:'lean/'+data[key].replace('.','/')+'.lean' for key in ['challenge_module','solution_module']}
    for key,target in modules.items():
        if target not in paths:missing.append(dict(path=path,reason='module_not_in_tree',field=key,target=target))
    for ax in data.get('permitted_axioms',[]):axioms[ax]+=1
    configs.append(dict(path=path,**modules,theorem_names=data.get('theorem_names',[]),permitted_axioms=data.get('permitted_axioms',[]),enable_nanoda=data.get('enable_nanoda')))
dump('COMPARATOR_MAP.json',configs)
dump('COMPARATOR_STRUCTURAL_EXCEPTIONS.json',missing)
unresolved=[dict(r) for r in con.execute("SELECT module,target,count(*) as import_rows FROM imports WHERE internal=0 AND module LIKE 'OAI.%' GROUP BY module,target")]
dump('UNRESOLVED_INTERNAL_IMPORT_CANDIDATES.json',unresolved)
markers=[dict(r) for r in con.execute('SELECT kind,classification,count(*) as occurrences,count(DISTINCT path) as files FROM markers GROUP BY kind,classification')]
exceptions=[dict(r) for r in con.execute('SELECT * FROM exceptions')]
dump('LEXICAL_MARKER_COUNTS.json',markers);dump('SCAN_EXCEPTIONS.json',exceptions)

chosen={
 '003':'lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean',
 '271':'lean/OAI/MathematicalPhysics/Heisenberg/Main.lean',
}
dependencies=[]
for family,path in chosen.items():
    closure=[r[0] for r in con.execute('''WITH RECURSIVE reachable(path) AS (
      SELECT ? UNION SELECT target FROM imports JOIN reachable ON source=reachable.path WHERE internal=1
    ) SELECT path FROM reachable''',(path,))]
    line_sum=0
    for node in closure:
        record=con.execute('SELECT physical_lines FROM files WHERE path=?',(node,)).fetchone()
        line_sum+=(record[0] or 0) if record else 0
    dependencies.append(dict(family=family,root=path,internal_modules=len(closure),physical_lines=line_sum,paths=sorted(closure),
       note='Import closure, not a minimal theorem dependency slice or semantic verification. External library dependencies are excluded.'))
dump('SELECTED_IMPORT_CLOSURES.json',dependencies)
summary=dict(families=len(families),current_manuscript_paths=len(mapped),formal_source_paths=len(formal_sources),
   scope_note_paper_paths=len(scope_sources),scope_paths_missing_from_tree=sorted(scope_sources-paths),
   comparator_configs=len(configs),comparator_interface_exceptions=len(missing),permitted_axiom_counts=dict(axioms),
   unresolved_OAI_import_candidates=len(unresolved),scan_exceptions=len(exceptions),lexical_marker_groups=markers,
   selected_closures=[{k:v for k,v in r.items() if k!='paths'} for r in dependencies])
dump('STRUCTURAL_REVIEW_SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
con.close()
