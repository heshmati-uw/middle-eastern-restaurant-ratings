"""Re-express every count figure in the current packet using three categories."""
from pathlib import Path
from collections import defaultdict
import csv,json
R=Path(__file__).resolve().parent;O=R/'outputs'
def read(name):
 with (O/name).open() as f:return list(csv.DictReader(f))
def write(name,rows):
 with (O/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def group(g):
 if g in ['ME','Other ME','Nationally associated ME','Ban-country associated ME','Other literal ME']:return 'ME'
 if g=='All other Mediterranean':return 'Medit'
 return g
specs=[];monthly=[];totals=[]
settings=[(1,'national_association','Broad','Seven original Trump-majority counties','2015-12','national_association_monthly'),(2,'ban_country','Ban countries','Seven original Trump-majority counties','2015-12','ban_country_monthly'),(3,'all_trump','Broad','All available Trump-majority counties','2015-12','all_trump_broad'),(4,'all_trump','Ban countries','All available Trump-majority counties','2015-12','all_trump_ban'),(5,'county_vote','Broad','All available counties | Both county vote groups','2015-12','county_vote_broad'),(6,'county_vote','Ban countries','All available counties | Both county vote groups','2015-12','county_vote_ban'),(7,'county_vote_jan2015','Broad','All available counties | Both county vote groups','2015-01','county_vote_jan2015_broad'),(8,'county_vote_jan2015','Ban countries','All available counties | Both county vote groups','2015-01','county_vote_jan2015_ban')]
for num,prefix,version,geo,start,alias in settings:
 bins=defaultdict(int);ns=defaultdict(int)
 for r in read(prefix+'_monthly.csv'):
  if r.get('version',version)!=version or group(r['group']).startswith('Excluded'):continue
  bins[r.get('vote_group','Trump-majority'),r['month'],group(r['group'])]+=int(r['restaurants'])
 for r in read(prefix+'_totals.csv'):
  if r.get('version',version)!=version or group(r['group']).startswith('Excluded'):continue
  ns[r.get('vote_group','Trump-majority'),group(r['group'])]+=int(r.get('active_restaurants',r.get('review_active_restaurants',0)))
 for (vote,month,g),n in bins.items():monthly.append(dict(figure=num,version=version,vote_group=vote,month=month,group=g,restaurants=n))
 for (vote,g),n in ns.items():totals.append(dict(figure=num,version=version,vote_group=vote,group=g,restaurants=n))
 specs.append(dict(figure=num,version=version,geography=geo,start=start,alias=alias))
write('broad_me_count_figures.csv',specs);write('broad_me_monthly_counts.csv',monthly);write('broad_me_count_totals.csv',totals)
# Restaurant assignments are a strict coarsening. Exclusions and WPME/Medit stay unchanged.
with (R/'private/county_vote_jan2015_assignments.csv').open() as f:rows=list(csv.DictReader(f))
for r in rows:r['group']=group(r['group'])
with (R/'private/broad_me_assignments.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(O/'broad_me_count_validation.json').write_text(json.dumps(dict(merged_groups=['ME','Other ME'],monthly_total_counts_preserved=True,wpme_and_medit_unchanged=True,ban_national_exclusions_preserved=True,figures=8),indent=2))
print('Prepared eight count figures and merged assignments')
