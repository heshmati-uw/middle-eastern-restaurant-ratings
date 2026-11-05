"""Classify the unrestricted Trump-county universe and validate seven-county overlap."""
from pathlib import Path
from collections import defaultdict
import csv,json
ROOT=Path(__file__).resolve().parent;P=ROOT/'private';O=ROOT/'outputs'
def read(path):
 with path.open(newline='') as f:return list(csv.DictReader(f))
def save(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=read(P/'all_trump_food_activity.csv');byid={r['gmap_id']:r for r in rows}
registry=json.loads((ROOT/'dictionaries/country_food_registry_v1.json').read_text())
national={'Afghani restaurant':'Afghanistan','Armenian restaurant':'Armenia','Egyptian restaurant':'Egypt','Lebanese restaurant':'Lebanon','Moroccan restaurant':'Morocco','Persian restaurant':'Iran','Syrian restaurant':'Syria','Yemenite restaurant':'Yemen'}
ban={'Iran','Iraq','Syria','Yemen','Libya','Somalia','Sudan'}
months=[f'{year}-{m:02d}' for year in [2015,2016,2017] for m in range(1,13) if '2015-12'<=f'{year}-{m:02d}'<='2017-04']
groups=['ME','Other ME','WPME','Medit','Excluded other national tags']
assign=[];monthly=[];totals=[];county_counts=[]
for version,countries in [('Broad',set(registry['countries'])),('Ban countries',ban)]:
 eligible_foods={e['dish_id'] for e in registry['entries'] if countries.intersection(e['countries'])}
 bins=defaultdict(set);county_bins=defaultdict(set)
 for r in rows:
  g=r['gmap_id'];cat=r['primary_category'];country=national.get(cat,'');hits=eligible_foods.intersection(r['dish_ids'].split('|'))
  if cat=='Mediterranean restaurant':group='WPME' if hits else 'Medit'
  elif cat=='Middle Eastern restaurant':group='ME' if hits else 'Other ME'
  elif country in countries:group='ME'
  else:group='Excluded other national tags'
  assign.append(dict(version=version,gmap_id=g,county_fips=r['county_fips'],primary_category=cat,group=group,label_country=country,qualifying_dish_ids='|'.join(sorted(hits)),review_active=int(bool(r['months']))))
  for m in filter(None,r['months'].split('|')):
   bins[m,group].add(g);county_bins[m,group].add(r['county_fips'])
 for group in groups:
  a=[r for r in assign if r['version']==version and r['group']==group];active=[r for r in a if r['review_active']]
  totals.append(dict(version=version,group=group,metadata_restaurants=len(a),active_restaurants=len(active),active_counties=len({r['county_fips'] for r in active})))
  for m in months:monthly.append(dict(version=version,month=m,group=group,restaurants=len(bins[m,group]),counties=len(county_bins[m,group])))
 for m in months:
  assert sum(len(bins[m,g]) for g in groups)==sum(m in r['months'].split('|') for r in rows)
  plotted=set().union(*(bins[m,g] for g in groups[:-1]))
  county_counts.append(dict(version=version,month=m,plotted_restaurants=len(plotted),plotted_counties=len({byid[g]['county_fips'] for g in plotted}),excluded_restaurants=len(bins[m,groups[-1]])))
save(P/'all_trump_assignments.csv',assign)
save(O/'all_trump_monthly.csv',monthly);save(O/'all_trump_totals.csv',totals);save(O/'all_trump_county_counts.csv',county_counts)
save(O/'all_trump_county_coverage.csv',[dict(version=v,county_fips=c,active_restaurants=sum(r['version']==v and r['county_fips']==c and r['review_active'] and r['group']!=groups[-1] for r in assign)) for v in ['Broad','Ban countries'] for c in sorted({r['county_fips'] for r in assign if r['version']==v and r['review_active'] and r['group']!=groups[-1]})])
# Confirm geographic expansion reproduces every old restaurant-month and category.
old_activity=defaultdict(set)
for r in read(P/'seven_county_activity.csv'):
 if r['gmap_id'] in byid:old_activity[r['gmap_id']].add(r['date'][:7])
for r in read(P/'national_association_assignments.csv'):
 g=r['gmap_id'];assert g in byid
 assert set(filter(None,byid[g]['months'].split('|')))==old_activity[g]
 new=next(x for x in assign if x['gmap_id']==g and x['version']=='Broad')
 expected={'Nationally associated ME':'ME','Other literal ME':'Other ME','All other Mediterranean':'Medit','WPME':'WPME'}[r['group']]
 assert new['group']==expected,(g,new['group'],expected)
for r in read(P/'ban_country_assignments.csv'):
 new=next(x for x in assign if x['gmap_id']==r['gmap_id'] and x['version']=='Ban countries')
 expected={'Ban-country associated ME':'ME','Other literal ME':'Other ME'}.get(r['group'],r['group'])
 assert new['group']==expected
audit=dict(prior_seven_county_months_and_assignments_identical=True,monthly_partition_verified=True,no_fixed_cohort=True,metadata_counties=len({r['county_fips'] for r in rows}),metadata_restaurants=len(rows),dictionary_changes=False)
(O/'all_trump_validation.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(totals,indent=2))
