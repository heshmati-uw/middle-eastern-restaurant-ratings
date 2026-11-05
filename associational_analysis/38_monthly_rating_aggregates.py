"""Restaurant- and review-weighted monthly means in identical count samples."""
from pathlib import Path
from collections import defaultdict
import csv,json,statistics
R=Path(__file__).resolve().parent;P=R/'private';O=R/'outputs'
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
def save(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ratings=read(P/'restaurant_month_ratings.csv');byid=defaultdict(list)
for r in ratings:byid[r['gmap_id']].append(r)
assign=read(P/'broad_me_assignments.csv');bins=defaultdict(list);period=defaultdict(list)
for a in assign:
 if a['group'].startswith('Excluded'):continue
 for r in byid[a['gmap_id']]:
  key=(a['version'],a['vote_group'],a['group']);bins[key+(r['month'],)].append(r);period[key].append(r)
rows=[];totals=[]
for (version,vote,g,month),rs in sorted(bins.items()):
 n=sum(int(r['reviews']) for r in rs);s=sum(float(r['rating_sum']) for r in rs)
 rows.append(dict(version=version,vote_group=vote,group=g,month=month,restaurants=len(rs),reviews=n,restaurant_weighted_mean=statistics.mean(float(r['mean_rating']) for r in rs),review_weighted_mean=s/n))
for (version,vote,g),rs in sorted(period.items()):
 totals.append(dict(version=version,vote_group=vote,group=g,restaurants=len({r['gmap_id'] for r in rs}),reviews=sum(int(r['reviews']) for r in rs)))
expected={(r['version'],r['vote_group'],r['group'],r['month']):int(r['restaurants']) for r in read(O/'broad_me_monthly_counts.csv') if r['figure'] in ['7','8']}
actual={(r['version'],r['vote_group'],r['group'],r['month']):r['restaurants'] for r in rows}
assert expected==actual,'Rating and count restaurant-month samples differ'
save(O/'broad_me_monthly_ratings.csv',rows);save(O/'broad_me_rating_totals.csv',totals)
(O/'broad_me_ratings_validation.json').write_text(json.dumps(dict(count_rating_samples_identical=True,monthly_cells=len(rows),restaurant_weighting='mean of restaurant-month mean ratings',review_weighting='sum of all stars divided by review count',fixed_cohort=False,matched=False,complete_calendar_months=True),indent=2))
print(json.dumps(totals,indent=2))
