"""Seven-ban-country sensitivity, with explicit handling of other national tags."""
from pathlib import Path
from collections import defaultdict
import argparse,csv,json
ROOT=Path(__file__).resolve().parent;P=ROOT/'private';O=ROOT/'outputs'
parser=argparse.ArgumentParser()
parser.add_argument('--other-national-tags',required=True,choices=['exclude','food-evidence'])
a=parser.parse_args()
countries={'Iran','Iraq','Syria','Yemen','Libya','Somalia','Sudan'}
registry=json.loads((ROOT/'dictionaries/country_food_registry_v1.json').read_text())
entries=[e for e in registry['entries'] if countries.intersection(e['countries'])]
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def save(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
prior={r['gmap_id']:r for r in read(P/'national_association_assignments.csv')}
food=read(P/'positioning_variant_food_expanded_anydate.csv')
assign=[]
for r in food:
 g=r['gmap_id'];p=prior[g];cat=p['primary_category'];country=p['label_country'];fs=set(r['features'].split('|'))
 hits=[e for e in entries if fs.intersection(e['feature_keys'])]
 if cat=='Mediterranean restaurant':group='WPME' if hits else 'Medit'
 elif cat=='Middle Eastern restaurant':group='Ban-country associated ME' if hits else 'Other literal ME'
 elif country in countries:group='Ban-country associated ME'
 elif a.other_national_tags=='food-evidence' and hits:group='Ban-country associated ME'
 else:group='Excluded other national tags'
 assign.append(dict(gmap_id=g,group=group,primary_category=cat,label_country=country,ban_food_evidence=int(bool(hits)),dish_ids='|'.join(e['dish_id'] for e in hits)))
byid={r['gmap_id']:r for r in assign}
activity=[r for r in read(P/'seven_county_activity.csv') if r['gmap_id'] in byid]
active={r['gmap_id'] for r in activity};months=sorted({r['date'][:7] for r in activity})
groups=['Ban-country associated ME','Other literal ME','WPME','Medit','Excluded other national tags']
bins=defaultdict(set)
for r in activity:bins[r['date'][:7],byid[r['gmap_id']]['group']].add(r['gmap_id'])
save(P/'ban_country_assignments.csv',assign)
save(O/'ban_country_monthly.csv',[dict(month=m,group=l,restaurants=len(bins[m,l])) for m in months for l in groups[:-1]])
totals=[dict(group=l,metadata_restaurants=sum(r['group']==l for r in assign),review_active_restaurants=sum(r['group']==l and r['gmap_id'] in active for r in assign)) for l in groups]
save(O/'ban_country_totals.csv',totals)
save(O/'ban_country_exclusions_monthly.csv',[dict(month=m,excluded_restaurants=len(bins[m,groups[-1]])) for m in months])
save(O/'ban_country_food_list.csv',[dict(dish_id=e['dish_id'],countries='|'.join(sorted(countries.intersection(e['countries'])))) for e in entries])
for m in months:assert sum(len(bins[m,l]) for l in groups)==len({r['gmap_id'] for r in activity if r['date'][:7]==m})
for r in assign:
 if r['group']=='WPME':assert prior[r['gmap_id']]['group']=='WPME'
audit=dict(countries=sorted(countries),qualifying_entries=len(entries),other_national_tags=a.other_national_tags,monthly_partition_including_exclusions_verified=True,review_active_restaurants=len(active),evidence_window=registry['evidence_window'])
(O/'ban_country_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(totals,indent=2))
