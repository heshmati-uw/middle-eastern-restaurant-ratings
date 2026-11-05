"""Complete Jan2015-Apr2017 raw ratings for the existing non-American universe."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv,gzip,hashlib,json,sqlite3
ROOT=Path(__file__).resolve().parent;P=ROOT/'private';O=ROOT/'outputs'
START=1420070400000;END=1493596800000
def init(ids):
 global IDS
 IDS={g.encode() for g in ids}
def scan(path,dest,sig):
 n=selected=0
 with gzip.open(path,'rb') as source,gzip.open(dest,'wt',newline='',encoding='utf8') as output:
  w=csv.writer(output)
  for line in source:
   n+=1;pos=line.rfind(b'"gmap_id"');key=line[pos:].split(b'"',4)
   if len(key)<4 or key[3] not in IDS:continue
   r=json.loads(line);t=r.get('time') or 0
   if not START<=t<END or r.get('rating') not in [1,2,3,4,5]:continue
   h=hashlib.sha256(json.dumps([r.get(k) for k in ('gmap_id','user_id','time','rating','text')],ensure_ascii=False).encode()).hexdigest()
   w.writerow([h,r['gmap_id'],t,r['rating']]);selected+=1
 result=dict(signature=sig,file=path.name,rows=n,selected_records=selected)
 dest.with_suffix('.json').write_text(json.dumps(result));return result
def main():
 manifest=json.loads((P/'source_manifest.json').read_text());raw=Path(manifest['raw_directory'])
 ids=set()
 for prefix in ['all_trump','all_nontrump']:
  with (P/f'{prefix}_food_activity_jan2015.csv').open() as f:ids.update(r['gmap_id'] for r in csv.DictReader(f))
 cache=P/'monthly_ratings_checkpoints';cache.mkdir(exist_ok=True)
 base=hashlib.sha256(json.dumps(sorted(ids)).encode()+b'Jan2015-Apr2017-v1').hexdigest()
 jobs=[];results=[]
 for r in manifest['review_files']:
  path=raw/r['file'];assert path.stat().st_size==r['bytes'] and path.stat().st_mtime_ns==r['mtime_ns']
  dest=cache/(path.name+'.csv.gz');sig=base+str(r['bytes'])+str(r['mtime_ns']);audit=dest.with_suffix('.json')
  if dest.exists() and audit.exists() and json.loads(audit.read_text())['signature']==sig:results.append(json.loads(audit.read_text()))
  else:jobs.append((path,dest,sig))
 print(json.dumps(dict(files_to_scan=len(jobs),restaurants=len(ids))),flush=True)
 with ProcessPoolExecutor(12,initializer=init,initargs=(ids,)) as pool:
  for future in as_completed([pool.submit(scan,*j) for j in jobs]):
   result=future.result();results.append(result);print(json.dumps(result),flush=True)
 db=sqlite3.connect(P/'monthly_ratings.sqlite')
 db.execute('CREATE TABLE IF NOT EXISTS reviews(hash TEXT PRIMARY KEY,gmap_id TEXT,time INTEGER,rating INTEGER) WITHOUT ROWID')
 for r in results:
  with gzip.open(cache/(r['file']+'.csv.gz'),'rt',encoding='utf8') as f:db.executemany('INSERT OR IGNORE INTO reviews VALUES(?,?,?,?)',csv.reader(f))
 db.commit()
 with (P/'restaurant_month_ratings.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['gmap_id','month','reviews','rating_sum','mean_rating'])
  w.writerows(db.execute("SELECT gmap_id,strftime('%Y-%m',time/1000,'unixepoch'),count(*),sum(rating),avg(rating) FROM reviews GROUP BY 1,2 ORDER BY 1,2"))
 audit=dict(start='2015-01-01',end_inclusive='2017-04-30',metadata_restaurants=len(ids),raw_files=sorted(results,key=lambda r:r['file']),deduplicated_reviews=db.execute('SELECT count(*) FROM reviews').fetchone()[0],dedup_key=['gmap_id','user_id','time','rating','text'],time_zone='UTC')
 (O/'monthly_ratings_raw_audit.json').write_text(json.dumps(audit,indent=2));print('DONE',audit['deduplicated_reviews'],flush=True)
if __name__=='__main__':main()
