"""Versioned nonexclusive country registry and national-association classification.

Reuses unchanged regex features from the complete expanded any-date raw scan.
Country links change; no new review search patterns or reviews are introduced.
"""
from pathlib import Path
import csv, json, re, importlib.util, hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
D=ROOT/'dictionaries'; O=ROOT/'outputs'; P=ROOT/'private'
spec=importlib.util.spec_from_file_location('raw',ROOT/'13_positioning_variants_raw.py')
raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
old=json.loads((D/'country_food_dictionary.json').read_text())
base=json.loads((D/'food_dictionary_no_shawarma.json').read_text())
extra=json.loads((D/'me_food_additions_2026_11_05.json').read_text())
entries={}
def get(k):
    return entries.setdefault(k,dict(dish_id=k,feature_keys=[],patterns=[],country_sources={},source_status={}))
def link(k,c,url,status='source_checked_2026_11_05'):
    e=get(k);e['country_sources'].setdefault(c,[])
    for u in ([url] if isinstance(url,str) else url):
        if u not in e['country_sources'][c]:e['country_sources'][c].append(u)
    e['source_status'][c]=status
# Preserve original feature spellings, but join dish variants with identical aliases.
aliases={}
for e in old['entries']:
    k=raw.norm(e['dish']).replace(' ','_')
    if k in {'dolma','dolmeh','shakshouka'}:continue
    get(k)
    aliases[k]=set(raw.norm(a) for a in e['aliases'])|aliases.get(k,set())
    link(k,e['country'],e['sources'],'inherited_seven_country_registry')
for k in base['core']:get(k)
for k in extra['qualifying_additions']:get(k)
for feature,pattern in raw.definitions(True):
    if feature.startswith('other_'):continue
    k=feature.split('_',1)[1];e=get(k)
    if feature not in e['feature_keys']:e['feature_keys'].append(feature)
    if pattern not in e['patterns']:e['patterns'].append(pattern)
# Existing core names matching a seven-country alias inherit that association.
for k in list(entries):
    for j,aa in aliases.items():
        if raw.norm(k.replace('_',' ')) in aa:
            for c,urls in list(entries[j]['country_sources'].items()):link(k,c,urls,'inherited_seven_country_registry')
leb='https://maureenabood.com/'
for k in ['baba_ghanoush','kibbeh','fattoush','muhammara','mujaddara','kebab','kofta']:link(k,'Lebanon',leb)
for k in ['tabbouleh','shawarma']:link(k,'Lebanon','https://maureenabood.com/summer-menus/')
for k in ['labneh','zaatar']:link(k,'Lebanon','https://edelweiss-assets.abovethetreeline.com/PS/supplemental/RWOB_E_Galley.pdf')
for k in ['baba_ghanoush','tabbouleh','shawarma','labneh','fattoush']:link(k,'Syria','https://www.omayahcooks.com/full-index')
link('zaatar','Syria','https://waratah-h.schools.nsw.gov.au/content/dam/doe/sws/schools/w/waratah-h/news/Taste_of_Harmony_Cookbook_FINAL_2020.pdf')
af='https://www.ecieco.org/fa/article/234/Traditional-Afghan-Cuisine-A-Symbol-of-Hospitality-and-Collective-Identity'
for k in ['bolani','mantu','qabili_pulao','kebab']:link(k,'Afghanistan',af)
link('lahmacun','Armenia','https://www.armenianmuseum.org/armenian-recipes/lahmajoun-meat-recipe')
for k in ['koshari','ful_medames','molokhia','kofta']:link(k,'Egypt','https://amiraspantry.com/category/egyptian-recipes/')
link('kebab','Egypt','https://cdn.who.int/media/docs/default-source/eios/2022-eios-gtm-agenda.pdf?sfvrsn=c630b60c_1')
for k in ['kofta','kebab']:link(k,'Morocco','https://tasteofmaroc.com/moroccan-kefta-recipe/')
link('kebab','Iran','https://www.iranicaonline.org/articles/kabab-popular-dish/')
# Union identical aliases (e.g., kubba/kibbeh, asida/aseeda); keep named preparations.
parent={k:k for k in entries}
def find(k):
    while parent[k]!=k:k=parent[k]
    return k
for k in entries:
    for j in aliases:
        ak=aliases.get(k,{raw.norm(k.replace('_',' '))})
        if ak & aliases[j]:parent[find(j)]=find(k)
merged={}
for k,e in entries.items():
    root=find(k);z=merged.setdefault(root,dict(dish_id=root,feature_keys=[],patterns=[],country_sources={},source_status={}))
    for field in ['feature_keys','patterns']:z[field]=sorted(set(z[field]+e[field]))
    for c,urls in e['country_sources'].items():
        z['country_sources'][c]=sorted(set(z['country_sources'].get(c,[])+urls))
        z['source_status'][c]=e['source_status'][c]
for e in merged.values():
    e['countries']=sorted(e['country_sources'])
    e['membership']='shared' if len(e['countries'])>1 else 'single_listed' if e['countries'] else 'broader_only_unmapped'
    e['broader_ME_qualifier']=True
    e['country_list_qualifier']=bool(e['countries'])
countries=old['countries']+['Afghanistan','Armenia','Egypt','Lebanon','Morocco']
registry=dict(version='twelve-country-associations-v1-2026-11-05',countries=countries,
    evidence_window='Any available valid-star positive-timestamp review; retrospective, not rolling',
    interpretation='Nonexhaustive documented cuisine associations, not exclusive origins, restaurant nationality or verified authenticity. Single-listed is relative to this registry only.',
    context_validation='Regex mentions only. Negation, comparisons, and mentions of other restaurants have not been adjudicated.',
    excluded_standalone=['shakshuka','generic dolma/dolmeh','baklava','hummus','falafel'],
    entries=sorted(merged.values(),key=lambda e:e['dish_id']))
(D/'country_food_registry_v1.json').write_text(json.dumps(registry,indent=2)+'\n',encoding='utf8')
def read(p):
    with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def save(p,rows):
    with p.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save(O/'national_association_dictionary.csv',[dict(dish_id=e['dish_id'],membership=e['membership'],countries='|'.join(e['countries']),feature_keys='|'.join(e['feature_keys']),sources='|'.join(sorted({u for us in e['country_sources'].values() for u in us}))) for e in registry['entries']])
food=read(P/'positioning_variant_food_expanded_anydate.csv');meta={r['gmap_id']:r for r in read(P/'metadata.csv')}
activity=read(P/'seven_county_activity.csv');ids={r['gmap_id'] for r in food};activity=[r for r in activity if r['gmap_id'] in ids]
active={r['gmap_id'] for r in activity};months=sorted({r['date'][:7] for r in activity})
national_tags={'Afghani restaurant':'Afghanistan','Armenian restaurant':'Armenia','Egyptian restaurant':'Egypt','Lebanese restaurant':'Lebanon','Moroccan restaurant':'Morocco','Persian restaurant':'Iran','Syrian restaurant':'Syria','Yemenite restaurant':'Yemen'}
assign=[]
for r in food:
    g=r['gmap_id'];category=meta[g]['primary_category'];fs=set(r['features'].split('|'))
    hits=[e for e in registry['entries'] if fs.intersection(e['feature_keys']) and e['country_list_qualifier']]
    cc=sorted({c for e in hits for c in e['countries']});tag=national_tags.get(category,'')
    eligible=bool(tag) or (category=='Middle Eastern restaurant' and bool(hits))
    group='Nationally associated ME' if eligible else 'Other literal ME' if category=='Middle Eastern restaurant' else 'WPME' if r['broad_ME']=='1' else 'All other Mediterranean'
    assert category in national_tags or category in ['Middle Eastern restaurant','Mediterranean restaurant']
    route='national tag + food evidence' if tag and hits else 'national tag only' if tag else 'literal ME + food evidence' if eligible else 'outside nationally associated group'
    assign.append(dict(gmap_id=g,primary_category=category,group=group,route=route,label_country=tag,food_countries='|'.join(cc),country_dish_ids='|'.join(e['dish_id'] for e in hits),active_in_plot=int(g in active)))
save(P/'national_association_assignments.csv',assign)
byid={r['gmap_id']:r for r in assign};groups=['Nationally associated ME','Other literal ME','WPME','All other Mediterranean']
bins=defaultdict(set)
for r in activity:bins[r['date'][:7],byid[r['gmap_id']]['group']].add(r['gmap_id'])
monthly=[dict(month=m,group=l,restaurants=len(bins[m,l])) for m in months for l in groups]
save(O/'national_association_monthly.csv',monthly)
totals=[dict(group=l,metadata_restaurants=sum(r['group']==l for r in assign),review_active_restaurants=sum(r['group']==l and r['gmap_id'] in active for r in assign)) for l in groups]
save(O/'national_association_totals.csv',totals)
save(O/'national_association_routes.csv',[dict(route=route,review_active_restaurants=sum(r['route']==route and r['gmap_id'] in active for r in assign)) for route in sorted({r['route'] for r in assign})])
assert len(assign)==176 and len(active)==124
for m in months:assert sum(len(bins[m,l]) for l in groups)==len({r['gmap_id'] for r in activity if r['date'][:7]==m})
for e in registry['entries']:assert (e['membership']=='shared')==(len(e['countries'])>1)
for k in ['koobideh','adas_polo']:assert next(e for e in registry['entries'] if e['dish_id']==k)['membership']=='single_listed'
assert len({c for e in registry['entries'] for c in e['countries']})==12
assert {f for e in registry['entries'] for f in e['feature_keys']}=={f for f,p in raw.definitions(True) if not f.startswith('other_')}
audit=dict(dictionary_sha256=hashlib.sha256((D/'country_food_registry_v1.json').read_bytes()).hexdigest(),food_profile_sha256=hashlib.sha256((P/'positioning_variant_food_expanded_anydate.csv').read_bytes()).hexdigest(),countries=12,dish_entries=len(registry['entries']),raw_rescan=False,reason='Unchanged extraction patterns; relink existing complete any-date raw-scan features to documented countries.',monthly_partition_verified=True,metadata_restaurants=len(assign),review_active_restaurants=len(active),single_listed_not_exclusive=True)
(O/'national_association_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(totals,indent=2));print(json.dumps(read(O/'national_association_routes.csv'),indent=2))
