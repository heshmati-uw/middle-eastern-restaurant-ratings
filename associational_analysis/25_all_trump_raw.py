"""All eligible Trump-majority restaurants: raw any-date food + monthly activity.

No county peer, matching, historical food cutoff, or balanced review requirement.
Uses the complete raw-derived metadata/geography universe, verified against source
size/mtime. Scans every raw review file, including cross-state duplicates. Binary
food and month indicators are duplicate invariant. Per-source checkpoints allow
safe resumption only with identical sources, IDs, and dictionary.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from collections import defaultdict
from datetime import datetime,timezone
import argparse,csv,gzip,hashlib,json,re,unicodedata
ROOT=Path(__file__).resolve().parent
START=1448928000000;END=1493596800000
def norm(s):return ' '.join(re.findall(r'[^\W_]+',''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))))
def init(ids,entries):
 global IDS,PATS
 IDS=set(ids);PATS=[(e['dish_id'],[re.compile(p) for p in e['patterns']]) for e in entries]
def scan(path,cache,signature):
 found=defaultdict(set);months=defaultdict(set);n=selected=0;lo=hi=None
 with gzip.open(path,'rb') as f:
  for line in f:
   n+=1;pos=line.rfind(b'"gmap_id"');key=line[pos:].split(b'"',4)
   if len(key)<4 or key[3] not in IDS:continue
   r=json.loads(line);t=r.get('time') or 0
   if t<=0 or r.get('rating') not in [1,2,3,4,5]:continue
   g=r['gmap_id'];selected+=1
   if START<=t<END:months[g].add(datetime.fromtimestamp(t/1000,timezone.utc).strftime('%Y-%m'))
   if r.get('text'):
    lo=t if lo is None else min(lo,t);hi=t if hi is None else max(hi,t);s=norm(r['text'])
    for k,patterns in PATS:
     if k not in found[g] and any(p.search(s) for p in patterns):found[g].add(k)
 row=dict(file=path.name,rows=n,selected_valid_records=selected,text_min_time=lo,text_max_time=hi)
 result=dict(signature=signature,audit=row,foods={g:sorted(v) for g,v in found.items()},months={g:sorted(v) for g,v in months.items()})
 cache.write_text(json.dumps(result));return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
 with (ROOT/'private/metadata.csv').open() as f:meta={r['gmap_id']:r for r in csv.DictReader(f) if r['label']!='American' and float(r['gop_share'])>.5}
 manifest=json.loads((ROOT/'private/source_manifest.json').read_text())
 for r in manifest['metadata_files']:
  source=a.raw_dir/r['file'];assert source.stat().st_size==r['bytes'] and source.stat().st_mtime_ns==r['mtime_ns'],'Rebuild metadata: source changed'
 registry_path=ROOT/'dictionaries/country_food_registry_v1.json';registry=json.loads(registry_path.read_text())
 files=sorted(a.raw_dir.glob('review-*.json.gz'),key=lambda p:-p.stat().st_size);assert len(files)==52
 signature=hashlib.sha256(registry_path.read_bytes()+json.dumps(sorted(meta)).encode()+b'all-trump-raw-v1').hexdigest()
 cache=ROOT/'private/all_trump_raw_checkpoints';cache.mkdir(exist_ok=True)
 jobs=[];results=[]
 for source in files:
  sig=signature+str(source.stat().st_size)+str(source.stat().st_mtime_ns);dest=cache/(source.name+'.json')
  old=json.loads(dest.read_text()) if dest.exists() else None
  if old and old['signature']==sig:results.append(old)
  else:jobs.append((source,dest,sig))
 print(json.dumps(dict(metadata_restaurants=len(meta),metadata_counties=len({r['county_fips'] for r in meta.values()}),files_to_scan=len(jobs),reused_checkpoints=len(results))),flush=True)
 with ProcessPoolExecutor(a.workers,initializer=init,initargs=([g.encode() for g in meta],registry['entries'])) as pool:
  for future in as_completed([pool.submit(scan,*job) for job in jobs]):
   result=future.result();results.append(result);print(json.dumps(result['audit']),flush=True)
 foods=defaultdict(set);months=defaultdict(set)
 for result in results:
  for g,ks in result['foods'].items():foods[g].update(ks)
  for g,ms in result['months'].items():months[g].update(ms)
 dest=ROOT/'private/all_trump_food_activity.csv'
 with dest.open('w',newline='') as f:
  fields=list(next(iter(meta.values())))+['dish_ids','months'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for g,r in sorted(meta.items()):w.writerow({**r,'dish_ids':'|'.join(sorted(foods[g])),'months':'|'.join(sorted(months[g]))})
 audit=dict(metadata_restaurants=len(meta),metadata_counties=len({r['county_fips'] for r in meta.values()}),active_restaurants=sum(bool(months[g]) for g in meta),active_counties=len({r['county_fips'] for g,r in meta.items() if months[g]}),dictionary_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),metadata_sha256=hashlib.sha256((ROOT/'private/metadata.csv').read_bytes()).hexdigest(),raw_files=[r['audit'] for r in results],definition='Trump vote share >0.5; primary ME/national/Mediterranean tags; all months Dec2015-Apr2017; any-date food; no matching or fixed review cohort')
 (ROOT/'outputs/all_trump_raw_audit.json').write_text(json.dumps(audit,indent=2))
 print('DONE',json.dumps({k:v for k,v in audit.items() if k!='raw_files'}),flush=True)
if __name__=='__main__':main()
