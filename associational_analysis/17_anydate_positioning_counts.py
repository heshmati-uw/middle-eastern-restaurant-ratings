"""Any-date food evidence sensitivity; same monthly population and dictionaries."""
from pathlib import Path
from collections import defaultdict
import csv,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def save(name,rows,private=False):
    with (ROOT/('private' if private else 'outputs')/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
food={r['gmap_id']:r for r in read(ROOT/'private/positioning_variant_food_anydate.csv')}
pre={r['gmap_id']:r for r in read(ROOT/'private/positioning_variant_food.csv')}
assert set(food)==set(pre)
for g in food:
    for key in ['broad_ME','seven_ME']:assert int(food[g][key])>=int(pre[g][key])
    assert set(pre[g]['features'].split('|'))-{''}<=set(food[g]['features'].split('|'))
activity=[r for r in read(ROOT/'private/seven_county_activity.csv') if r['gmap_id'] in food]
active={r['gmap_id'] for r in activity};months=sorted({r['date'][:7] for r in activity})
groups=['ME','WPME','All other Mediterranean restaurants']
monthly=[];totals=[];prepost=[];assignments=[];transitions=[]
for version,key in [('Broader','broad_ME'),('Seven-country','seven_ME')]:
    def classify(r):return 'ME' if r['label']!='Mediterranean' else 'WPME' if r[key]=='1' else groups[2]
    group={g:classify(r) for g,r in food.items()};bins=defaultdict(set);period=defaultdict(set)
    for g in food:assignments.append(dict(version=version,gmap_id=g,group=group[g],pre_cutoff_group=classify(pre[g])))
    for r in activity:
        g,t=r['gmap_id'],r['date'];label=group[g];bins[t[:7],label].add(g)
        if '2016-12-27'<=t<='2017-01-23':period[label,'pre'].add(g)
        if '2017-01-27'<=t<='2017-02-23':period[label,'post'].add(g)
    for label in groups:
        for m in months:monthly.append(dict(version=version,month=m,group=label,restaurants=len(bins[m,label])))
        ids={g for g in active if group[g]==label}
        totals.append(dict(version=version,group=label,pre_cutoff_unique=sum(classify(pre[g])==label for g in active),any_date_unique=len(ids),counties=len({food[g]['county_fips'] for g in ids})))
        a,b=period[label,'pre'],period[label,'post'];prepost.append(dict(version=version,group=label,before=len(a),after=len(b),both=len(a&b)))
    for old in groups:
        for new in groups:transitions.append(dict(version=version,pre_cutoff_group=old,any_date_group=new,restaurants=sum(classify(pre[g])==old and group[g]==new for g in active)))
    for m in months:assert sum(len(bins[m,l]) for l in groups)==len({r['gmap_id'] for r in activity if r['date'][:7]==m})
save('positioning_anydate_monthly.csv',monthly);save('positioning_anydate_totals.csv',totals);save('positioning_anydate_prepost.csv',prepost);save('positioning_anydate_transitions.csv',transitions);save('positioning_anydate_assignments.csv',assignments,True)
save('positioning_anydate_validation.csv',[dict(check='Same restaurant universe; earlier qualifying evidence is a subset of any-date evidence; groups exhaust every monthly non-American activity count',metadata_restaurants=len(food),active_restaurants=len(active),months=len(months))])
print(json.dumps(totals,indent=2));print(json.dumps(prepost,indent=2))
