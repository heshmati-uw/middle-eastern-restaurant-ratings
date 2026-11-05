"""Descriptive counts of restaurants with reviews; no culinary or paired restriction."""
from pathlib import Path
from collections import defaultdict
import csv,json,calendar
from datetime import date
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
LABELS=['Middle Eastern','National','Mediterranean','American']
COUNTIES={'08041':'El Paso, CO','12009':'Brevard, FL','12071':'Lee, FL','20173':'Sedgwick, KS','26099':'Macomb, MI','34025':'Monmouth, NJ','48085':'Collin, TX'}
MONTHS=[f'{y}-{m:02}' for y in [2015,2016,2017] for m in range(1,13) if '2015-12'<=f'{y}-{m:02}'<='2017-04']
monthly=defaultdict(set);county_month=defaultdict(set);period=defaultdict(set);allperiod=defaultdict(set)
with (ROOT/'private/seven_county_activity.csv').open() as f:
    for r in csv.DictReader(f):
        g,l,c,t=r['gmap_id'],r['label'],r['county_fips'],r['date'];month=t[:7]
        monthly[month,l].add(g);county_month[month,c,l].add(g)
        if '2016-12-27'<=t<='2017-01-23':period[c,l,'pre'].add(g)
        if '2017-01-27'<=t<='2017-02-23':period[c,l,'post'].add(g)
        if t<'2017-01-24':allperiod[l,'pre'].add(g)
        if t>='2017-01-27':allperiod[l,'post'].add(g)
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('seven_county_monthly_counts.csv',[dict(month=m,label=l,restaurants=len(monthly[m,l])) for m in MONTHS for l in LABELS])
save('seven_county_monthly_by_county.csv',[dict(month=m,county_fips=c,county=COUNTIES[c],label=l,restaurants=len(county_month[m,c,l])) for m in MONTHS for c in COUNTIES for l in LABELS])
rows=[]
for c in list(COUNTIES)+['ALL']:
    for l in LABELS:
        pre=set().union(*(period[k,l,'pre'] for k in COUNTIES)) if c=='ALL' else period[c,l,'pre']
        post=set().union(*(period[k,l,'post'] for k in COUNTIES)) if c=='ALL' else period[c,l,'post']
        rows.append(dict(county_fips=c,county=COUNTIES.get(c,'All seven counties'),label=l,before=len(pre),after=len(post),both=len(pre&post),either=len(pre|post),before_only=len(pre-post),after_only=len(post-pre)))
save('seven_county_prepost_counts.csv',rows)
save('seven_county_full_window_counts.csv',[dict(label=l,before=len(allperiod[l,'pre']),after=len(allperiod[l,'post']),both=len(allperiod[l,'pre']&allperiod[l,'post']),pre_start='2015-12-01',pre_end='2017-01-23',post_start='2017-01-27',post_end='2017-04-30') for l in LABELS])
print(json.dumps([r for r in rows if r['county_fips']=='ALL'],indent=2))

