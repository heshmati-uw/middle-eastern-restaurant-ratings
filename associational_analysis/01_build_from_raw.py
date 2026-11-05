"""Build restaurant-level associations from original metadata/review gzip files.

Intermediate hashes stay local. No reviewer identifiers or review text are exported.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,csv,gzip,hashlib,json,sqlite3,time
from datetime import datetime,timezone

NATIONAL={x+' restaurant' for x in ['Afghani','Armenian','Egyptian','Lebanese','Moroccan','Persian','Syrian','Yemenite']}
LABELS={**{x:'National' for x in NATIONAL},'Middle Eastern restaurant':'Middle Eastern','Mediterranean restaurant':'Mediterranean','American restaurant':'American'}
def ms(s):return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()*1000)
CUT=ms('2016-11-08');START=ms('2016-11-14');END=ms('2017-04-10')
def init(ids):
    global IDS
    IDS=set(ids)
def scan_review(source,destination):
    total=kept=0
    with gzip.open(source,'rb') as f,gzip.open(destination,'wt',encoding='utf8',newline='') as out:
        w=csv.writer(out)
        for line in f:
            total+=1
            pos=line.rfind(b'"gmap_id"');key=line[pos:].split(b'"',4)
            if len(key)<4 or key[3] not in IDS:continue
            r=json.loads(line);t=r.get('time') or 0;rating=r.get('rating')
            if rating not in (1,2,3,4,5) or not (0<t<CUT or START<=t<END):continue
            h=hashlib.sha256(json.dumps([r.get(k) for k in ('gmap_id','user_id','time','rating','text')],ensure_ascii=False).encode()).hexdigest()
            w.writerow([h,r['gmap_id'],int(t),rating]);kept+=1
    return {'file':Path(source).name,'scanned':total,'selected_before_dedup':kept}
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--geography',type=Path,required=True);p.add_argument('--workers',type=int,default=12)
    args=p.parse_args();root=Path(__file__).resolve().parent
    private=root/'private';private.mkdir(exist_ok=True);out=root/'outputs';out.mkdir(exist_ok=True)
    manifest={'outcome_start':'2016-11-14','outcome_end_inclusive':'2017-04-09','history_end_exclusive':'2016-11-08','time_zone':'UTC','raw_directory':str(args.raw_dir),'metadata_files':[],'review_files':[],'geography_sha256':hashlib.sha256(args.geography.read_bytes()).hexdigest()}
    with args.geography.open(encoding='utf-8-sig',newline='') as f:geo={r['gmap_id']:r for r in csv.DictReader(f)}
    meta={};conflicts=set();eligible=set()
    for path in sorted(args.raw_dir.glob('meta-*.json.gz')):
        manifest['metadata_files'].append({'file':path.name,'bytes':path.stat().st_size,'mtime_ns':path.stat().st_mtime_ns})
        with gzip.open(path,'rt',encoding='utf8') as f:
            for line in f:
                r=json.loads(line);cats=r.get('category') or [];g=r.get('gmap_id')
                if not cats or cats[0] not in LABELS:continue
                eligible.add(g)
                if g not in geo or not geo[g].get('county_fips') or geo[g].get('gop_share') in ('','nan',None):continue
                rec={'gmap_id':g,'label':LABELS[cats[0]],'primary_category':cats[0],'county_fips':geo[g]['county_fips'],'gop_share':float(geo[g]['gop_share']),'price':r.get('price') or 'Missing'}
                if g in meta and meta[g]!=rec:conflicts.add(g)
                else:meta[g]=rec
        print('metadata',path.name,flush=True)
    for g in conflicts:meta.pop(g,None)
    manifest.update(raw_label_eligible=len(eligible),with_geography_nonconflicting=len(meta),metadata_conflicts_excluded=len(conflicts))
    with (private/'metadata.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(next(iter(meta.values()))));w.writeheader();w.writerows(meta.values())
    files=sorted(args.raw_dir.glob('review-*.json.gz'),key=lambda p:-p.stat().st_size)
    assert len(files)==52 and len(manifest['metadata_files'])==52
    with ProcessPoolExecutor(args.workers,initializer=init,initargs=([g.encode() for g in meta],)) as pool:
        jobs={pool.submit(scan_review,path,private/(path.stem+'.selected.csv.gz')):path for path in files}
        for f in as_completed(jobs):
            row=f.result();path=jobs[f];row.update(bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns);manifest['review_files'].append(row);print('reviews',row,flush=True)
    db=sqlite3.connect(private/'dedup.sqlite');db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
    db.execute('DROP TABLE IF EXISTS reviews');db.execute('CREATE TABLE reviews(hash TEXT PRIMARY KEY,gmap_id TEXT,time INTEGER,rating INTEGER) WITHOUT ROWID')
    for path in files:
        with gzip.open(private/(path.stem+'.selected.csv.gz'),'rt',encoding='utf8') as f:
            rows=[]
            for row in csv.reader(f):
                rows.append(row)
                if len(rows)==10000:db.executemany('INSERT OR IGNORE INTO reviews VALUES(?,?,?,?)',rows);rows=[]
            db.executemany('INSERT OR IGNORE INTO reviews VALUES(?,?,?,?)',rows)
        db.commit();print('deduplicated',path.name,flush=True)
    query='SELECT gmap_id,SUM(CASE WHEN time<? THEN 1 ELSE 0 END),SUM(CASE WHEN time>=? AND time<? THEN 1 ELSE 0 END),SUM(CASE WHEN time>=? AND time<? THEN rating ELSE 0 END) FROM reviews GROUP BY gmap_id'
    rows=[]
    for g,h,n,stars in db.execute(query,(CUT,START,END,START,END)):
        if n:rows.append({**meta[g],'prior_reviews':h,'outcome_reviews':n,'rating':stars/n})
    with (private/'restaurant_levels.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    manifest['deduplicated_selected_reviews']=db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0];manifest['outcome_restaurants']=len(rows)
    manifest['metadata_assumption']='Primary category and price are snapshot attributes, not historical measurements. Geography/vote are frozen linked inputs.'
    manifest['dedup_key']='SHA256 of JSON [gmap_id,user_id,time,rating,text]; repeated identical records count once across all state files.'
    (private/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    public={k:v for k,v in manifest.items() if k not in ('raw_directory','metadata_files','review_files')}
    public.update(raw_metadata_files=len(manifest['metadata_files']),raw_review_files=len(manifest['review_files']),raw_review_rows_scanned=sum(x['scanned'] for x in manifest['review_files']),selected_rows_before_dedup=sum(x['selected_before_dedup'] for x in manifest['review_files']))
    (out/'source_audit.json').write_text(json.dumps(public,indent=2),encoding='utf8')
    print('DONE',len(rows),'restaurants',flush=True)
if __name__=='__main__':main()
