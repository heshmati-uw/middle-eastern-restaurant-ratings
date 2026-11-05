"""Raw pre-election food evidence for all non-American category restaurants in seven counties."""
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv,gzip,json,re,unicodedata,argparse,hashlib
ROOT=Path(__file__).resolve().parent;CUT=1478563200000
def norm(s):return ' '.join(re.findall(r'[^\W_]+',''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))))
def definitions(expanded=False):
    base=json.loads((ROOT/'dictionaries/food_dictionary_no_shawarma.json').read_text())
    country=json.loads((ROOT/'dictionaries/country_food_dictionary.json').read_text())['entries']
    other=json.loads((ROOT/'dictionaries/non_me_mediterranean_pilot.json').read_text())['entries']
    specs=[]
    for k,p in base['core'].items():
        if k!='baba_ghanoush':specs.append(('core_'+k,p))
    for e in country:
        k=norm(e['dish']).replace(' ','_')
        if k not in {'dolma','dolmeh','shakshouka'}:specs.append(('seven_'+k,r'\b(?:'+'|'.join(re.escape(norm(a)) for a in e['aliases'])+r')\b'))
    for e in other:specs.append(('other_'+e['dish'],r'\b(?:'+'|'.join(re.escape(norm(a)) for a in e['aliases'])+r')\b'))
    if expanded:
        additions=json.loads((ROOT/'dictionaries/me_food_additions_2026_11_05.json').read_text())['qualifying_additions']
        specs.extend(('core_'+k,p) for k,p in additions.items())
    return specs
def init(ids,specs,any_date=False):
    global IDS,PATS,ANY_DATE
    IDS=set(ids);PATS=[(k,re.compile(p)) for k,p in specs];ANY_DATE=any_date
def scan(path):
    found=defaultdict(set);texts=set();total=0;min_time=None;max_time=None
    with gzip.open(path,'rb') as f:
        for line in f:
            total+=1;p=line.rfind(b'"gmap_id"');key=line[p:].split(b'"',4)
            if len(key)<4 or key[3] not in IDS:continue
            r=json.loads(line)
            t=r.get('time') or 0
            if not t>0 or (not ANY_DATE and t>=CUT) or r.get('rating') not in [1,2,3,4,5] or not r.get('text'):continue
            min_time=t if min_time is None else min(min_time,t);max_time=t if max_time is None else max(max_time,t)
            g=r['gmap_id'];texts.add(g);s=norm(r['text'])
            for k,p in PATS:
                if p.search(s):found[g].add(k)
    return dict(file=path.name,rows=total,selected_text_min_time=min_time,selected_text_max_time=max_time),dict(found),texts
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--workers',type=int,default=12);p.add_argument('--any-date',action='store_true');p.add_argument('--expanded',action='store_true');a=p.parse_args()
    if a.expanded:assert a.any_date,'Expanded extension currently uses the requested any-date window.'
    counties=set(json.loads((ROOT/'outputs/seven_county_activity_audit.json').read_text())['county_fips'])
    with (ROOT/'private/metadata.csv').open() as f:meta={r['gmap_id']:r for r in csv.DictReader(f) if r['county_fips'] in counties and r['label']!='American'}
    specs=definitions(a.expanded);files=sorted(a.raw_dir.glob('review-*.json.gz'),key=lambda p:-p.stat().st_size);assert len(files)==52
    cached_empty=[]
    if a.expanded:
        # Previous complete any-date scan proves the other files have no eligible text
        # for these exact IDs. Reuse that negative result only for unchanged sources.
        with (ROOT/'private/positioning_variant_food_anydate.csv').open() as f:prior_ids={r['gmap_id'] for r in csv.DictReader(f)}
        manifest=json.loads((ROOT/'private/source_manifest.json').read_text());stats={r['file']:r for r in manifest['review_files']}
        previous=json.loads((ROOT/'outputs/positioning_anydate_raw_audit.json').read_text())
        unchanged=all(p.stat().st_size==stats[p.name]['bytes'] and p.stat().st_mtime_ns==stats[p.name]['mtime_ns'] for p in files)
        if set(meta)==prior_ids and unchanged and len(previous['raw_files'])==52:
            cached_empty=[{**r,'reused_zero_eligible_text':True} for r in previous['raw_files'] if r['selected_text_min_time'] is None]
            skip={r['file'] for r in cached_empty};files=[p for p in files if p.name not in skip]
            print('Reusing verified empty-text results for',len(skip),'unchanged files; rescanning',len(files),flush=True)
    found=defaultdict(set);texts=set();audit=[]
    with ProcessPoolExecutor(a.workers,initializer=init,initargs=([g.encode() for g in meta],specs,a.any_date)) as pool:
        for job in as_completed([pool.submit(scan,p) for p in files]):
            row,fs,ts=job.result();texts.update(ts);audit.append(row)
            for g,ks in fs.items():found[g].update(ks)
            print(row,flush=True)
    filename='positioning_variant_food_expanded_anydate.csv' if a.expanded else 'positioning_variant_food_anydate.csv' if a.any_date else 'positioning_variant_food.csv'
    with (ROOT/'private'/filename).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['gmap_id','label','county_fips','any_text' if a.any_date else 'pre_text','broad_ME','seven_ME','other_med','other_med_without_salad','features'])
        for g,r in sorted(meta.items()):
            fs=found[g];seven=any(k.startswith('seven_') for k in fs);broad=seven or any(k.startswith('core_') for k in fs);other=any(k.startswith('other_') for k in fs)
            w.writerow([g,r['label'],r['county_fips'],int(g in texts),int(broad),int(seven),int(other),int(any(k.startswith('other_') and k!='other_horiatiki' for k in fs)),'|'.join(sorted(fs))])
    auditname='positioning_expanded_anydate_raw_audit.json' if a.expanded else 'positioning_anydate_raw_audit.json' if a.any_date else 'positioning_variants_raw_audit.json'
    (ROOT/'outputs'/auditname).write_text(json.dumps(dict(metadata_restaurants=len(meta),raw_files=audit+cached_empty,files_rescanned=len(audit),files_with_reused_empty_text=len(cached_empty),cutoff_exclusive=None if a.any_date else '2016-11-08 UTC',evidence_window='All valid positive-timestamp reviews in supplied raw corpus' if a.any_date else 'Pre-election reviews',dictionary_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'dictionaries').glob('*.json')}),indent=2))
if __name__=='__main__':main()
