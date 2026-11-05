from pathlib import Path
from collections import defaultdict,Counter
import csv,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def save(name,rows,private=False):
    with (ROOT/('private' if private else 'outputs')/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
food={r['gmap_id']:r for r in read(ROOT/'private/positioning_variant_food.csv')}
activity=[r for r in read(ROOT/'private/seven_county_activity.csv') if r['gmap_id'] in food]
active={r['gmap_id'] for r in activity};months=sorted({r['date'][:7] for r in activity})
versions=[('V1','broad_ME','positive'),('V2','broad_ME','residual'),('V3','seven_ME','positive'),('V4','seven_ME','residual')]
monthly=[];totals=[];prepost=[];assignments=[];overlap=[];sensitivity=[]
for v,scope,rule in versions:
    groups={}
    for g,r in food.items():
        groups[g]='ME' if r['label']!='Mediterranean' else 'WPME' if r[scope]=='1' else 'Other Mediterranean' if rule=='residual' or r['other_med']=='1' else 'Unclassified'
        assignments.append(dict(version=v,gmap_id=g,group=groups[g]))
    bins=defaultdict(set);period=defaultdict(set)
    for r in activity:
        g,t=r['gmap_id'],r['date'];group=groups[g];bins[t[:7],group].add(g)
        if '2016-12-27'<=t<='2017-01-23':period[group,'pre'].add(g)
        if '2017-01-27'<=t<='2017-02-23':period[group,'post'].add(g)
    for group in ['ME','WPME','Other Mediterranean','Unclassified']:
        for m in months:monthly.append(dict(version=v,scope=scope,rule=rule,month=m,group=group,restaurants=len(bins[m,group])))
        ids={g for g in active if groups[g]==group}
        totals.append(dict(version=v,scope=scope,rule=rule,group=group,active_any_month=len(ids),metadata_restaurants=sum(x==group for x in groups.values()),counties=len({food[g]['county_fips'] for g in ids}),without_pre_election_text=sum(food[g]['pre_text']=='0' for g in ids)))
        a,b=period[group,'pre'],period[group,'post'];prepost.append(dict(version=v,group=group,before=len(a),after=len(b),both=len(a&b)))
    med={g for g in active if food[g]['label']=='Mediterranean'}
    overlap.append(dict(version=v,med_with_both_food_types=sum(food[g][scope]=='1' and food[g]['other_med']=='1' for g in med),ME_label_without_qualifying_food=sum(food[g]['label']!='Mediterranean' and food[g][scope]=='0' for g in active)))
    sensitivity.append(dict(version=v,positive_other_med_main=sum(food[g][scope]=='0' and food[g]['other_med']=='1' for g in med),positive_other_med_excluding_greek_salad_only=sum(food[g][scope]=='0' and food[g]['other_med_without_salad']=='1' for g in med)))
    for m in months:assert sum(len(bins[m,g]) for g in ['ME','WPME','Other Mediterranean','Unclassified'])==len({r['gmap_id'] for r in activity if r['date'][:7]==m})
save('positioning_variants_monthly.csv',monthly);save('positioning_variants_totals.csv',totals);save('positioning_variants_prepost.csv',prepost);save('positioning_variants_overlap.csv',overlap);save('positioning_variants_salad_sensitivity.csv',sensitivity);save('positioning_variant_assignments.csv',assignments,True)
save('positioning_variants_validation.csv',[dict(check='Disjoint groups plus unclassified exhaust active non-American restaurants in every version-month',active_restaurants=len(active),metadata_restaurants=len(food),months=len(months),versions=4)])
print(json.dumps(totals,indent=2));print('OVERLAP',overlap);print('SALAD SENSITIVITY',sensitivity)
