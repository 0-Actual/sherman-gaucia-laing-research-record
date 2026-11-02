#!/usr/bin/env node
// New publication preparation. No network, archive jobs or source edits.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const SELF=fileURLToPath(import.meta.url), EDITION=path.resolve(path.dirname(SELF),'..');
const RETAINED='prior-work/corrected-comparisons.json', REPORT='PROJECT-COMPARISONS.md', COVERAGE='comparison-coverage.json';
const LIMIT=32*1024*1024;
const need=(ok,message)=>{if(!ok)throw Error(message);};
const digest=b=>createHash('sha256').update(b).digest('hex');
const pointerPart=s=>String(s).replace(/~/g,'~0').replace(/\//g,'~1');
const inside=(base,p)=>p===base||(!path.relative(base,p).startsWith('..'+path.sep)&&path.relative(base,p)!=='..'&&!path.isAbsolute(path.relative(base,p)));
function noLinks(p){
 let current=path.parse(path.resolve(p)).root;
 for(const bit of path.resolve(p).slice(current.length).split(path.sep).filter(Boolean)){
  current=path.join(current,bit);need(!fs.lstatSync(current).isSymbolicLink(),'Linked path rejected');
 }
}
function readRegular(p){
 noLinks(p);const before=fs.lstatSync(p,{bigint:true});need(before.isFile()&&before.size<=BigInt(LIMIT),'Bounded regular source required');
 const bytes=fs.readFileSync(p),after=fs.lstatSync(p,{bigint:true});
 need(['dev','ino','size','mtimeNs','ctimeNs'].every(k=>before[k]===after[k])&&BigInt(bytes.length)===before.size,'Source changed during read');
 return bytes;
}
function writeNew(p,bytes){
 noLinks(path.dirname(p));const fd=fs.openSync(p,'wx');
 try{let n=0;while(n<bytes.length){const wrote=fs.writeSync(fd,bytes,n,bytes.length-n);need(wrote>0,'Write stalled');n+=wrote;}fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
 need(readRegular(p).equals(bytes),'Destination readback mismatch');
}
function safeText(value){
 return String(value).replace(/[&<>"\\\x60*_\[\]#!|~+]/g,c=>'&#'+c.charCodeAt(0)+';').replace(/\r/g,'&#13;').replace(/\n/g,'  \n');
}
function label(key){
 return String(key).replace(/_/g,' ').replace(/([a-z])([A-Z])/g,'$1 $2').replace(/^./,c=>c.toUpperCase());
}
export function renderComparisons({sourcePath,outputDir}){
 need(typeof sourcePath==='string'&&typeof outputDir==='string','sourcePath and outputDir are required');
 const source=path.resolve(sourcePath),out=path.resolve(outputDir);
 need(!inside(path.dirname(SELF),out),'Output must be outside the helper source directory');
 const sourceBytes=readRegular(source),data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(sourceBytes));
 need(data&&typeof data==='object'&&!Array.isArray(data)&&Array.isArray(data.comparisons)&&data.comparisons.length===28,'Exactly 28 comparison rows required');
 const ids=new Set();
 for(const row of data.comparisons){
  need(row&&typeof row==='object'&&!Array.isArray(row)&&/^I(?:0[1-9]|1[0-9]|2[0-8])$/.test(row.id)&&!ids.has(row.id),'Missing, repeated or unexpected comparison ID');
  ids.add(row.id);need(typeof row.title==='string'&&row.title.length>0,'Comparison title required');
  need(row.latest_corrected_conclusions&&typeof row.latest_corrected_conclusions==='object'&&!Array.isArray(row.latest_corrected_conclusions),'Latest conclusions object required');
  need(row.owner_stages&&typeof row.owner_stages==='object'&&!Array.isArray(row.owner_stages),'Owner stages object required');
 }
 for(let i=1;i<=28;i++)need(ids.has('I'+String(i).padStart(2,'0')),'Comparison ID population differs');
 if(!fs.existsSync(out))fs.mkdirSync(out,{recursive:true});noLinks(out);need(fs.statSync(out).isDirectory(),'Output directory required');
 for(const name of [REPORT,COVERAGE])need(!fs.existsSync(path.join(out,name)),'Create-only output already exists: '+name);
 const retainedPath=path.join(out,...RETAINED.split('/'));
 if(fs.existsSync(retainedPath))need(readRegular(retainedPath).equals(sourceBytes),'Existing retained comparison JSON differs');
 else{const parent=path.dirname(retainedPath);if(!fs.existsSync(parent))fs.mkdirSync(parent);writeNew(retainedPath,sourceBytes);}
 const lines=[],coverage=[],sectionRows=[],push=s=>{lines.push(...String(s).split('\n'));};
 const heading=(name,depth)=>{push((depth<=6?'#'.repeat(depth)+' ':'**')+safeText(name)+(depth<=6?'':'**'));push('');};
 function valueText(value){
  if(typeof value==='string'){push(value.length?safeText(value):'*Empty string in the source.*');push('');}
  else{push('Source value: '+JSON.stringify(value));push('');}
 }
 function exactLeaf(value,pointer,context){
  const json=JSON.stringify(value),runs=json.match(/\x60+/g)||[],fence='\x60'.repeat(Math.max(3,...runs.map(s=>s.length+1)));
  push('<details>');push('<summary>Exact source value</summary>');push('');push(fence+'json');
  const startLine=lines.length+1;push(json);const endLine=lines.length;
  push(fence);push('');push('</details>');push('');
  coverage.push({comparisonId:context.id,pointer,value,reportSection:context.section,reportAnchor:context.anchor,encoding:'json',startLine,endLine});
 }
 function render(value,pointer,name,depth,context=null){
  need(depth<=48,'Source nesting exceeds supported bound');heading(name,Math.min(depth,7));
  if(Array.isArray(value)){
   if(!value.length){valueText(value);if(context)exactLeaf(value,pointer,context);return;}
   push('Ordered list: '+value.length+' source items.');push('');
   value.forEach((item,i)=>render(item,pointer+'/'+i,'Item '+(i+1),depth+1,context));return;
  }
  if(value!==null&&typeof value==='object'){
   const entries=Object.entries(value);
   if(!entries.length){valueText(value);if(context)exactLeaf(value,pointer,context);return;}
   for(const [key,child] of entries)render(child,pointer+'/'+pointerPart(key),label(key),depth+1,context);return;
  }
  valueText(value);if(context)exactLeaf(value,pointer,context);
 }
 push('# Project comparisons — complete source rendering');push('');
 push('Sherman Gaucia Laing · Word.Quantum.Earth · Research evidence edition, November 2, 2026.');push('');
 push('Research assistance: ChatGPT/Codex and the existing project reviewers. This is a completely new publication. The earlier edition remains unchanged as a historical record.');push('');
 push('## Accountability for the earlier build and review');push('');
 push('ChatGPT’s report-building code in this project omitted available conclusion prose for I03, I05, I06, I13, I14, I21, I24, I25, I26, I27 and I28. ChatGPT’s review did not catch that omission before the earlier publication. The renderer recognized three field names but omitted the alternative finding, limit and excluded-from-current-findings fields already present in the retained source.');push('');
 push('The same build also omitted stored differences and comparison-gap fields in I04, I07, I08, I10, I12, I15, I19 and I20. This edition renders every latest-conclusion field, every owner stage and every other retained comparison field. The earlier source and report remain historical records; this correction does not invent replacement evidence.');push('');
 push('## How to read the evidence');push('');
 push('Recorded owner requirements, produced artifacts, executed work, public disclosure and external announcements are separate stages. Original dates, offsets, null values and qualifiers are retained. A later review date does not establish an implementation’s origin. Similarity and temporal order alone do not establish exposure, copying, authorship, purchase, novelty or legal priority.');push('');
 push('Latest corrected conclusions appear before the historical comparison and correction records. The historical material is retained for lineage and must not silently override later corrections. Exact source-value blocks accompany every conclusion leaf, including empty containers; the coverage file maps each block to its original JSON pointer.');push('');
 push('All original strings and structured values remain in the [unchanged comparison JSON]('+RETAINED+'). The final appendices reproduce the source’s provenance, source catalogue, owner anchors, review lineage and unresolved gaps. Other research and transaction evidence belongs to the accompanying edition; this renderer does not claim a complete account or universal body of work.');push('');
 push('## All 28 retained comparisons');push('');
 data.comparisons.forEach((row,index)=>{
  const anchor='comparison-'+row.id.toLowerCase(),section='### '+row.id+' '+safeText(row.title),base='/comparisons/'+index;
  push('<a id="'+anchor+'"></a>');push('');const startLine=lines.length+1;push(section);push('');
  const context={id:row.id,section,anchor};
  render(row.latest_corrected_conclusions,base+'/latest_corrected_conclusions','Latest corrected conclusions',4,context);
  render(row.owner_stages,base+'/owner_stages','Owner stages — original dates and qualifications',4);
  if(Object.hasOwn(row,'industry_dates'))render(row.industry_dates,base+'/industry_dates','Industry dates and source references',4);
  if(Object.hasOwn(row,'industry_references'))render(row.industry_references,base+'/industry_references','Industry source keys',4);
  if(Object.hasOwn(row,'prior_2026_09_17_comparison'))render(row.prior_2026_09_17_comparison,base+'/prior_2026_09_17_comparison','Historical September 17 comparison — retained, not the latest conclusion',4);
  if(Object.hasOwn(row,'applicable_stage_date_corrections'))render(row.applicable_stage_date_corrections,base+'/applicable_stage_date_corrections','Applicable dated corrections',4);
  const shown=new Set(['latest_corrected_conclusions','owner_stages','industry_dates','industry_references','prior_2026_09_17_comparison','applicable_stage_date_corrections']);
  for(const [key,value] of Object.entries(row))if(!shown.has(key))render(value,base+'/'+pointerPart(key),label(key),4);
  sectionRows.push({comparisonId:row.id,sourcePointer:base,reportSection:section,reportAnchor:anchor,startLine,endLine:lines.length});
 });
 push('## Source appendices — retained provenance and evidence limits');push('');
 for(const [key,value] of Object.entries(data))if(key!=='comparisons')render(value,'/'+pointerPart(key),label(key),3);
 const reportBytes=Buffer.from(lines.join('\n')+'\n','utf8');need(reportBytes.length<=LIMIT,'Rendered report exceeds supported bound');
 const reportIdentity={path:REPORT,bytes:reportBytes.length,sha256:digest(reportBytes)};
 const result={schema:'qel.comparisons.markdown-coverage.v1',createdUtc:new Date().toISOString(),source:{retainedPath:RETAINED,bytes:sourceBytes.length,sha256:digest(sourceBytes)},report:reportIdentity,comparisonCount:28,conclusionLeafCount:coverage.length,sections:sectionRows,conclusions:coverage,leafDefinition:'Primitive values and empty objects/arrays; nonempty containers are recursively enumerated in source order.',lineDefinition:'One-based LF-separated report lines; startLine/endLine cover only the JSON payload, excluding fences.',originalSourcePreserved:true,sourceSemanticValuesNormalized:false,publicationPerformed:false,ownerSignatureStatus:'NOT_PERFORMED',limits:['Source strings are preserved exactly in retained JSON and conclusion-value JSON blocks. Readable display escapes Markdown control characters.','Coverage records permit independent checking; renderer completion alone is not an independent verifier pass.','Prior evidence and historical status labels remain attributed and dated; no fresh external-source verification or execution claim is made.']};
 need(readRegular(source).equals(sourceBytes)&&readRegular(retainedPath).equals(sourceBytes),'Source changed before report save');
 writeNew(path.join(out,REPORT),reportBytes);writeNew(path.join(out,COVERAGE),Buffer.from(JSON.stringify(result,null,2)+'\n'));
 return {status:'REPORT_AND_COVERAGE_SAVED_READBACK_VERIFIED',outputDir:out,comparisonCount:28,conclusionLeafCount:coverage.length,report:reportIdentity,coveragePath:path.join(out,COVERAGE),sourceSha256:digest(sourceBytes),publicationPerformed:false};
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF){
 try{const args=process.argv.slice(2);need(args.length===4&&args[0]==='--source'&&args[2]==='--output','Usage: --source COMPARISON_JSON --output USB_EDITION_OUTPUT');console.log(JSON.stringify(renderComparisons({sourcePath:args[1],outputDir:args[3]})));}
 catch(e){console.error(JSON.stringify({status:'COMPARISON_RENDER_INCOMPLETE_RETAINED',message:e.message}));process.exitCode=1;}
}
