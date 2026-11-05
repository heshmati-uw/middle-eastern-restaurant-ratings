"""Recover earlier months from complete, raw-derived pre-election review cache."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import csv,json,sqlite3,hashlib
ROOT=Path(__file__).resolve().parent;P=ROOT/'private';O=ROOT/'outputs'
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def save(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
manifest=json.loads((P/'source_manifest.json').read_text());raw=Path(manifest['raw_directory'])
assert all((raw/r['file']).stat().st_size==r['bytes'] and (raw/r['file']).stat().st_mtime_ns==r['mtime_ns'] for r in manifest['review_files'])
profiles={prefix:read(P/f'{prefix}_food_activity.csv') for prefix in ['all_trump','all_nontrump']}
ids={r['gmap_id'] for rows in profiles.values() for r in rows}
c=sqlite3.connect('file:'+str((P/'dedup.sqlite').resolve()).replace('\\','/')+'?mode=ro',uri=True)
assert c.execute('SELECT count(*) FROM reviews').fetchone()[0]==manifest['deduplicated_selected_reviews']
c.execute('CREATE TEMP TABLE ids(gmap_id TEXT PRIMARY KEY)');c.executemany('INSERT INTO ids VALUES(?)',[(g,) for g in ids])
history=defaultdict(set)
for g,m in c.execute("SELECT DISTINCT r.gmap_id,strftime('%Y-%m',time/1000,'unixepoch') FROM reviews r JOIN ids USING(gmap_id) WHERE time>=1420070400000 AND time<1477958400000"):
 history[g].add(m)
overlap={f'2016-{m:02d}' for m in range(1,11)}|{'2015-12'}
for prefix,rows in profiles.items():
 for r in rows:
  old=set(filter(None,r['months'].split('|')))
  assert old&overlap==history[r['gmap_id']]&overlap,'Raw cache and newer scan disagree'
  r['months']='|'.join(sorted(old|history[r['gmap_id']]))
 save(P/f'{prefix}_food_activity_jan2015.csv',rows)
yearly=[]
for y,n,k,t in c.execute("SELECT strftime('%Y',time/1000,'unixepoch'),count(*),count(distinct r.gmap_id),min(time) FROM reviews r JOIN ids USING(gmap_id) WHERE time<1478563200000 GROUP BY 1 ORDER BY 1"):
 yearly.append(dict(year=y,reviews=n,restaurants=k,first_recorded_utc=datetime.fromtimestamp(t/1000,timezone.utc).isoformat(),coverage='Through Nov 7 only' if y=='2016' else 'Full calendar year'))
save(O/'county_vote_historical_coverage.csv',yearly)
audit=dict(start='2015-01-01',end_inclusive='2017-04-30',raw_files_verified_unchanged=52,cache='dedup.sqlite built from all 52 raw sources; full pre-Nov8 history, not outcome-only',cache_rows=manifest['deduplicated_selected_reviews'],source_manifest_sha256=hashlib.sha256((P/'source_manifest.json').read_bytes()).hexdigest(),overlap_months_verified=sorted(overlap),original_months_preserved=True,food_and_label_assignments_unchanged=True,earliest_recorded_utc=yearly[0]['first_recorded_utc'],earliest_year_reviews=yearly[0]['reviews'],earliest_year_restaurants=yearly[0]['restaurants'],early_timestamp_caution='The 1990-12-31 cluster is suspicious; no claim that review collection began then. Counts are recorded dates, not verified dates of collection.')
(O/'county_vote_jan2015_source_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(yearly,indent=2))
