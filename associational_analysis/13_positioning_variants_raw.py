"""Raw pre-election food evidence for all non-American category restaurants in seven counties."""
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv,gzip,json,re,unicodedata,argparse,hashlib
ROOT=Path(__file__).resolve().parent;CUT=1478563200000
def norm(s):return ' '.join(re.findall(r'[^\W_]+',''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))))
def definitions():
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
    return specs
def init(ids,specs):
    global IDS,PATS
    IDS=set(ids);PATS=[(k,re.compile(p)) for k,p in specs]
def scan(path):
    found=defaultdict(set);texts=set();total=0
    with gzip.open(path,'rb') as f:
        for line in f:
            total+=1;p=line.rfind(b'"gmap_id"');key=line[p:].split(b'"',4)
            if len(key)<4 or key[3] not in IDS:continue
            r=json.loads(line)
            if not 0<(r.get('time') or 0)<CUT or r.get('rating') not in [1,2,3,4,5] or not r.get('text'):continue
            g=r['gmap_id'];texts.add(g);s=norm(r['text'])
            for k,p in PATS:
                if p.search(s):found[g].add(k)
    return dict(file=path.name,rows=total),dict(found),texts
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
    counties=set(json.loads((ROOT/'outputs/seven_county_activity_audit.json').read_text())['county_fips'])
    with (ROOT/'private/metadata.csv').open() as f:meta={r['gmap_id']:r for r in csv.DictReader(f) if r['county_fips'] in counties and r['label']!='American'}
    specs=definitions();files=sorted(a.raw_dir.glob('review-*.json.gz'),key=lambda p:-p.stat().st_size);assert len(files)==52
    found=defaultdict(set);texts=set();audit=[]
    with ProcessPoolExecutor(a.workers,initializer=init,initargs=([g.encode() for g in meta],specs)) as pool:
        for job in as_completed([pool.submit(scan,p) for p in files]):
            row,fs,ts=job.result();texts.update(ts);audit.append(row)
            for g,ks in fs.items():found[g].update(ks)
            print(row,flush=True)
    with (ROOT/'private/positioning_variant_food.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['gmap_id','label','county_fips','pre_text','broad_ME','seven_ME','other_med','other_med_without_salad','features'])
        for g,r in sorted(meta.items()):
            fs=found[g];seven=any(k.startswith('seven_') for k in fs);broad=seven or any(k.startswith('core_') for k in fs);other=any(k.startswith('other_') for k in fs)
            w.writerow([g,r['label'],r['county_fips'],int(g in texts),int(broad),int(seven),int(other),int(any(k.startswith('other_') and k!='other_horiatiki' for k in fs)),'|'.join(sorted(fs))])
    (ROOT/'outputs/positioning_variants_raw_audit.json').write_text(json.dumps(dict(metadata_restaurants=len(meta),raw_files=audit,cutoff_exclusive='2016-11-08 UTC',dictionary_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'dictionaries').glob('*.json')}),indent=2))
if __name__=='__main__':main()
