"""Identical category rules applied to all available counties in both vote groups."""
from pathlib import Path
from collections import defaultdict
import csv,json
ROOT=Path(__file__).resolve().parent;P=ROOT/'private';O=ROOT/'outputs'
def read(path):
 with path.open(newline='') as f:return list(csv.DictReader(f))
def save(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
registry=json.loads((ROOT/'dictionaries/country_food_registry_v1.json').read_text())
national={'Afghani restaurant':'Afghanistan','Armenian restaurant':'Armenia','Egyptian restaurant':'Egypt','Lebanese restaurant':'Lebanon','Moroccan restaurant':'Morocco','Persian restaurant':'Iran','Syrian restaurant':'Syria','Yemenite restaurant':'Yemen'}
ban={'Iran','Iraq','Syria','Yemen','Libya','Somalia','Sudan'}
groups=['ME','Other ME','WPME','Medit','Excluded other national tags']
months=[f'{y}-{m:02d}' for y in [2015,2016,2017] for m in range(1,13) if '2015-12'<=f'{y}-{m:02d}'<='2017-04']
assign=[];monthly=[];totals=[];coverage=[];ids_by_vote={};counties_by_vote={};source_audits=[]
for vote,prefix in [('Trump-majority','all_trump'),('Other counties','all_nontrump')]:
 rows=read(P/f'{prefix}_food_activity.csv');ids_by_vote[vote]={r['gmap_id'] for r in rows};counties_by_vote[vote]={r['county_fips'] for r in rows}
 audit=json.loads((O/f'{prefix}_raw_audit.json').read_text());source_audits.append(audit)
 for version,countries in [('Broad',set(registry['countries'])),('Ban countries',ban)]:
  eligible={e['dish_id'] for e in registry['entries'] if countries.intersection(e['countries'])}
  bins=defaultdict(set);byid={r['gmap_id']:r for r in rows};local=[]
  for r in rows:
   cat=r['primary_category'];country=national.get(cat,'');hits=eligible.intersection(r['dish_ids'].split('|'))
   if cat=='Mediterranean restaurant':group='WPME' if hits else 'Medit'
   elif cat=='Middle Eastern restaurant':group='ME' if hits else 'Other ME'
   elif country in countries:group='ME'
   else:group='Excluded other national tags'
   record=dict(version=version,vote_group=vote,gmap_id=r['gmap_id'],county_fips=r['county_fips'],group=group,review_active=int(bool(r['months'])),qualifying_dish_ids='|'.join(sorted(hits)))
   local.append(record);assign.append(record)
   for m in filter(None,r['months'].split('|')):bins[m,group].add(r['gmap_id'])
  for group in groups:
   rs=[r for r in local if r['group']==group];active=[r for r in rs if r['review_active']]
   totals.append(dict(version=version,vote_group=vote,group=group,metadata_restaurants=len(rs),active_restaurants=len(active),active_counties=len({r['county_fips'] for r in active})))
   for m in months:monthly.append(dict(version=version,vote_group=vote,month=m,group=group,restaurants=len(bins[m,group])))
  active=[r for r in local if r['review_active'] and r['group']!=groups[-1]]
  coverage.append(dict(version=version,vote_group=vote,active_restaurants=len(active),active_counties=len({r['county_fips'] for r in active}),metadata_restaurants=len(rows),metadata_counties=len({r['county_fips'] for r in rows})))
  for m in months:assert sum(len(bins[m,g]) for g in groups)==sum(m in r['months'].split('|') for r in rows)
assert not ids_by_vote['Trump-majority'].intersection(ids_by_vote['Other counties'])
assert not counties_by_vote['Trump-majority'].intersection(counties_by_vote['Other counties'])
for field in ['dictionary_sha256','metadata_sha256']:assert source_audits[0][field]==source_audits[1][field]
assert {r['file']:r['rows'] for r in source_audits[0]['raw_files']}=={r['file']:r['rows'] for r in source_audits[1]['raw_files']}
old={(r['version'],r['month'],r['group']):int(r['restaurants']) for r in read(O/'all_trump_monthly.csv')}
for r in monthly:
 if r['vote_group']=='Trump-majority':assert r['restaurants']==old[r['version'],r['month'],r['group']]
old_assign={(r['version'],r['gmap_id']):r['group'] for r in read(P/'all_trump_assignments.csv')}
for r in assign:
 if r['vote_group']=='Trump-majority':assert r['group']==old_assign[r['version'],r['gmap_id']]
save(P/'county_vote_assignments.csv',assign);save(O/'county_vote_monthly.csv',monthly);save(O/'county_vote_totals.csv',totals);save(O/'county_vote_coverage.csv',coverage)
(O/'county_vote_validation.json').write_text(json.dumps(dict(trump_counts_and_assignments_unchanged=True,vote_groups_disjoint=True,monthly_partition_verified=True,dictionary_identical=True,metadata_universe_identical=True,vote_definition='Trump-majority >0.5; other <=0.5; linked 2016 vote share',counts_not_rates=True),indent=2)+'\n')
print(json.dumps(coverage,indent=2));print(json.dumps(totals,indent=2))
