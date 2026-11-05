"""Rebuild restaurant-day review activity for the seven culinary-sample Trump counties.
Binary activity is duplicate invariant; counts describe observed review activity,
not all operating restaurants. Reads all original state files to retain cross-file records.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from collections import defaultdict
from datetime import datetime,timezone
import csv,json,gzip,argparse
ROOT=Path(__file__).resolve().parent
START=1448928000000 # 2015-12-01 UTC
END=1493596800000 # 2017-05-01 UTC, exclusive
def init(ids):
    global IDS
    IDS=set(ids)
def scan(path):
    found=defaultdict(set);n=0
    with gzip.open(path,'rb') as f:
        for line in f:
            n+=1;p=line.rfind(b'"gmap_id"');key=line[p:].split(b'"',4)
            if len(key)<4 or key[3] not in IDS:continue
            r=json.loads(line);t=r.get('time') or 0
            if START<=t<END and r.get('rating') in [1,2,3,4,5]:found[r['gmap_id']].add(int(t)//86400000)
    return {'file':path.name,'raw_rows':n},dict(found)
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
    with (ROOT/'private/culinary_supported.csv').open() as f:cohort={r['gmap_id']:r for r in csv.DictReader(f) if float(r['gop_share'])>.5}
    counties={r['county_fips'] for r in cohort.values()};assert len(counties)==7 and len(cohort)==36
    with (ROOT/'private/metadata.csv').open() as f:meta={r['gmap_id']:r for r in csv.DictReader(f) if r['county_fips'] in counties}
    found=defaultdict(set);audit=[];files=sorted(a.raw_dir.glob('review-*.json.gz'),key=lambda p:-p.stat().st_size);assert len(files)==52
    with ProcessPoolExecutor(a.workers,initializer=init,initargs=([g.encode() for g in meta],)) as pool:
        jobs=[pool.submit(scan,p) for p in files]
        for j in as_completed(jobs):
            row,days=j.result();audit.append(row)
            for g,ds in days.items():found[g].update(ds)
            print(row,flush=True)
    with (ROOT/'private/seven_county_activity.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['gmap_id','label','county_fips','culinary_cohort','date'])
        for g,ds in sorted(found.items()):
            for day in sorted(ds):w.writerow([g,meta[g]['label'],meta[g]['county_fips'],int(g in cohort),datetime.fromtimestamp(day*86400,timezone.utc).date().isoformat()])
    (ROOT/'outputs/seven_county_activity_audit.json').write_text(json.dumps({'start':'2015-12-01','end_inclusive':'2017-04-30','timezone':'UTC','county_fips':sorted(counties),'metadata_restaurants':len(meta),'restaurants_with_activity':len(found),'raw_files':audit,'definition':'At least one valid-star review per restaurant-day; duplicates do not affect activity.'},indent=2))
if __name__=='__main__':main()
