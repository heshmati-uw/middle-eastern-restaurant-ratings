"""Rebuild binary pre-election food profiles directly from original review text.

Mentions proxy offerings; no sentiment or outcome ratings determine profiles.
Duplicates cannot affect binary presence. No review text is exported.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
import argparse, csv, gzip, json, re, unicodedata, hashlib

ROOT=Path(__file__).resolve().parent
CUT=1478563200000
def norm(s):
    return ' '.join(re.findall(r'[^\W_]+',''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))))

def definitions():
    base=json.loads((ROOT/'dictionaries/food_dictionary_no_shawarma.json').read_text())
    countries=json.loads((ROOT/'dictionaries/country_food_dictionary.json').read_text())['entries']
    specs=[]
    for family in ['core','shared_sensitivity']:
        for dish,pattern in base[family].items():
            specs.append((f'dish_{dish}',pattern, family=='core' and dish!='baba_ghanoush',[]))
    for e in countries:
        dish=norm(e['dish']).replace(' ','_')
        pattern=r'\b(?:'+'|'.join(re.escape(norm(a)) for a in e['aliases'])+r')\b'
        # Shared dishes can establish the same-dish link but never infer a country.
        specific=dish not in {'dolma','dolmeh','shakshouka'}
        specs.append((f'countrydish_{dish}',pattern,specific,[e['country']] if e['tier']=='country_associated' else []))
    return specs

def init(ids,specs):
    global IDS,PATTERNS
    IDS=set(ids);PATTERNS=[(k,re.compile(p),q,cs) for k,p,q,cs in specs]

def scan(path):
    found=defaultdict(set);total=eligible=0
    with gzip.open(path,'rb') as f:
        for line in f:
            total+=1
            pos=line.rfind(b'"gmap_id"');key=line[pos:].split(b'"',4)
            if len(key)<4 or key[3] not in IDS:continue
            r=json.loads(line)
            if not 0<(r.get('time') or 0)<CUT or r.get('rating') not in (1,2,3,4,5) or not r.get('text'):continue
            eligible+=1;s=norm(r['text']);g=r['gmap_id']
            for k,p,q,cs in PATTERNS:
                if p.search(s):
                    found[g].add(k)
                    for c in cs:found[g].add('tradition_'+c)
    return dict(file=path.name,rows=total,eligible_text_rows=eligible),{g:sorted(v) for g,v in found.items()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',required=True,type=Path);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
    with (ROOT/'private/restaurant_levels.csv').open() as f:ids=[r['gmap_id'].encode() for r in csv.DictReader(f) if r['label']!='American']
    specs=definitions();found=defaultdict(set);audit=[];files=list(a.raw_dir.glob('review-*.json.gz'));assert len(files)==52
    with ProcessPoolExecutor(a.workers,initializer=init,initargs=(ids,specs)) as pool:
        jobs=[pool.submit(scan,p) for p in sorted(files,key=lambda p:-p.stat().st_size)]
        for job in as_completed(jobs):
            row,features=job.result();audit.append(row)
            for g,fs in features.items():found[g].update(fs)
            print(row,flush=True)
    keys=sorted({k for k,p,q,cs in specs}|{'tradition_'+c for k,p,q,cs in specs for c in cs})
    qualifying={k for k,p,q,cs in specs if q}|{k for k in keys if k.startswith('tradition_')}
    with (ROOT/'private/culinary_profiles.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['gmap_id']+keys)
        for b in ids:
            g=b.decode();w.writerow([g]+[int(k in found[g]) for k in keys])
    (ROOT/'outputs/culinary_features.json').write_text(json.dumps({'features':keys,'qualifying_features':sorted(qualifying),'tradition_rule':'Only country_associated entries infer tradition; shared entries can establish a dish link.','excluded_from_qualification':['baba_ghanoush','all shared_sensitivity dishes','dolma','dolmeh','shakshouka'],'dictionary_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'dictionaries').glob('*.json')}},indent=2))
    (ROOT/'outputs/culinary_raw_audit.json').write_text(json.dumps({'files':audit,'restaurants_scanned':len(ids),'restaurants_with_any_food_evidence':sum(bool(found[b.decode()]) for b in ids),'cutoff_exclusive':'2016-11-08 UTC','binary_profiles_duplicate_invariant':True},indent=2))
if __name__=='__main__':main()
