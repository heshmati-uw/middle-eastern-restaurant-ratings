"""Fixed culinary-supported Trump-county cohort: descriptive monthly activity.
Uses the complete raw-derived restaurant-day scan from step 08, without rescanning.
"""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
cohort={r['gmap_id']:r for r in read(ROOT/'private/culinary_supported.csv') if float(r['gop_share'])>.5}
assert len(cohort)==36
labels=['Middle Eastern','National','Mediterranean'];months=[f'{y}-{m:02}' for y in [2015,2016,2017] for m in range(1,13) if '2015-12'<=f'{y}-{m:02}'<='2017-04']
monthly=defaultdict(set);period=defaultdict(set);seen=set()
for r in read(ROOT/'private/seven_county_activity.csv'):
    if r['gmap_id'] not in cohort:continue
    g,l,t=r['gmap_id'],r['label'],r['date'];assert r['culinary_cohort']=='1';seen.add(g)
    monthly[t[:7],l].add(g)
    if '2016-12-27'<=t<='2017-01-23':period[l,'pre'].add(g)
    if '2017-01-27'<=t<='2017-02-23':period[l,'post'].add(g)
assert seen==set(cohort)
totals=Counter(r['label'] for r in cohort.values())
save('culinary_activity_monthly.csv',[dict(month=m,label=l,restaurants=len(monthly[m,l]),cohort_restaurants=totals[l]) for m in months for l in labels])
counts=[]
for l in labels:
    a,b=period[l,'pre'],period[l,'post']
    counts.append(dict(label=l,cohort_restaurants=totals[l],before=len(a),after=len(b),both=len(a&b),either=len(a|b)))
save('culinary_activity_prepost.csv',counts)
composition=Counter((r['county_fips'],r['label'],r['primary_category']) for r in cohort.values())
save('culinary_activity_composition.csv',[dict(county_fips=c,label=l,primary_category=p,restaurants=n) for (c,l,p),n in sorted(composition.items())])
# Counts must be subsets of the unrestricted seven-county counts in every month.
unrestricted={(r['month'],r['label']):int(r['restaurants']) for r in read(OUT/'seven_county_monthly_counts.csv')}
assert all(len(monthly[m,l])<=unrestricted[m,l] for m in months for l in labels)
save('culinary_activity_validation.csv',[dict(check='Fixed cohort IDs all observed in raw-derived activity; monthly counts never exceed unrestricted counts',restaurants=len(cohort),counties=len({r['county_fips'] for r in cohort.values()}))])
print(json.dumps(counts,indent=2));print(json.dumps(dict(Counter(r['primary_category'] for r in cohort.values())),indent=2))
