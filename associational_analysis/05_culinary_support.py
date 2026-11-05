"""Keep all restaurants having an opposite-label culinary peer in their county."""
from pathlib import Path
import csv,json
from collections import defaultdict,Counter
root=Path(__file__).resolve().parent
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
d=[r for r in read(root/'private/restaurant_levels.csv') if r['label']!='American']
profiles={r.pop('gmap_id'):r for r in read(root/'private/culinary_profiles.csv')}
features=json.loads((root/'outputs/culinary_features.json').read_text())
qual=set(features['qualifying_features'])
# The seven-country registry is supplemented by the established core dictionary
# so that Levantine, Afghan and Egyptian offerings are not omitted by design.
regional={
 'Levant':['kibbeh','fattoush','muhammara','manakish','mujaddara','maqluba','mansaf','musakhan'],
 'Afghanistan':['bolani','qabili_pulao','mantu'],
 'Egypt':['koshari','molokhia','ful_medames'],
 'Iran':['ghormeh_sabzi','fesenjan','gheymeh','tahdig','koobideh','joojeh','abgoosht','ash_reshteh','zereshk_polo']}
for p in profiles.values():
    for region,dishes in regional.items():
        key='tradition_'+region
        p[key]=str(int(p.get(key,'0')=='1' or any(p.get('dish_'+dish)=='1' for dish in dishes)))
        qual.add(key)
(root/'outputs/culinary_regional_mapping.json').write_text(json.dumps(regional,indent=2))
counties=defaultdict(list)
for r in d:
    r['med']=int(r['label']=='Mediterranean');r.update(profiles[r['gmap_id']]);counties[r['county_fips']].append(r)
retained=[];audit=[]
for county,rows in counties.items():
    for r in rows:
        own={k for k in qual if r[k]=='1'}
        peers=[x for x in rows if x['med']!=r['med'] and any(x[k]=='1' for k in own)]
        if peers:retained.append(r)
for group,rows in [('All outcome restaurants',d),('Shared county and culinary support',retained)]:
    for label in ['Mediterranean','National','Middle Eastern']:
        a=[r for r in rows if r['label']==label]
        audit.append(dict(sample=group,label=label,restaurants=len(a),reviews=sum(int(r['outcome_reviews']) for r in a),counties=len({r['county_fips'] for r in a})))
for path,rows in [(root/'private/culinary_supported.csv',retained),(root/'outputs/culinary_sample_flow.csv',audit)]:
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(audit,indent=2))
