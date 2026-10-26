"""Expand the common-source shock data to both county-vote strata."""
from pathlib import Path
import json,ast,sys
import pandas as pd
import numpy as np
from prepare_data import sha256
HERE=Path(__file__).resolve().parent;OUT=HERE/'outputs'
CFG=json.loads((HERE/'config.json').read_text());ROOT=Path(CFG['source_root'])
SOURCE=ROOT/'data/Google Reviews/Reviews_Data_Combined.csv'

def main():
    groups=pd.read_csv(OUT/'restaurant_groups.csv')
    geo=pd.read_csv(OUT/'reviews_clean.csv',usecols=['gmap_id','county_fips','gop_share'],
                    dtype={'county_fips':'string'}).drop_duplicates('gmap_id')
    focal=groups[groups.group.isin(['ME','WPME'])][['gmap_id','group']].merge(geo,on='gmap_id',validate='one_to_one')
    cache=pd.read_pickle(OUT/'baseline_selected_cache.pkl')
    cg=cache[cache.group.eq('American')][['gmap_id','group']].drop_duplicates('gmap_id')
    bg=pd.read_csv(OUT/'baseline_business_geography.csv',dtype={'county_fips':'string'})
    controls=cg.merge(bg[['gmap_id','county_fips','gop_share']],on='gmap_id',validate='one_to_one')
    disagree=pd.read_csv(OUT/'baseline_geography_disagreements.csv')
    controls=controls[~controls.gmap_id.isin(disagree.gmap_id)]
    candidates=pd.concat([focal,controls],ignore_index=True)
    candidates=candidates[candidates.county_fips.notna()&candidates.gop_share.notna()].copy()
    candidates['trump']=(candidates.gop_share>.5).astype(int)
    assert candidates.gmap_id.is_unique
    assert candidates.groupby('county_fips').trump.nunique().eq(1).all()
    candidates.to_csv(OUT/'both_county_candidates.csv',index=False)
    prior=pd.read_pickle(OUT/'expanded_american_source_records.pkl')
    prior=prior[prior.gmap_id.isin(candidates.gmap_id)].copy()
    missing=set(candidates.gmap_id)-set(prior.gmap_id)
    extracted=OUT/'both_county_source_records.pkl'
    fingerprint={'source_bytes':SOURCE.stat().st_size,'source_mtime_ns':SOURCE.stat().st_mtime_ns,
                 'candidate_sha256':sha256(OUT/'both_county_candidates.csv')}
    if '--use-cache' in sys.argv:
        metadata=json.loads((OUT/'both_county_cache_metadata.json').read_text())
        assert metadata['fingerprint']==fingerprint
        assert metadata['record_sha256']==sha256(extracted)
        records=pd.read_pickle(extracted);scanned=metadata['scanned_business_rows']
    else:
        parts=[prior];scanned=0
        print('Candidate businesses:',len(candidates),'already extracted:',len(prior),
              'additional IDs to retrieve:',len(missing),flush=True)
        for chunk in pd.read_csv(SOURCE,usecols=['gmap_id','Date','Average Rating','Count of Reviews'],chunksize=20000):
            scanned+=len(chunk)
            z=chunk[chunk.gmap_id.isin(missing)]
            if len(z):parts.append(z.copy())
            if scanned%500000==0:print(f'Scanned {scanned:,} business rows',flush=True)
        records=pd.concat(parts,ignore_index=True)
        records.to_pickle(extracted)
        (OUT/'both_county_cache_metadata.json').write_text(json.dumps({'fingerprint':fingerprint,
           'record_sha256':sha256(extracted),'scanned_business_rows':scanned},indent=2))
    found=set(records.gmap_id)
    missing_ids=sorted(set(candidates.gmap_id)-found)
    pd.DataFrame({'gmap_id':missing_ids}).to_csv(OUT/'both_county_missing_source_ids.csv',index=False)
    rows=[]
    for ident,dates,ratings,counts in records.itertuples(index=False,name=None):
        ds,rs,ns=map(ast.literal_eval,[dates,ratings,counts])
        assert len(ds)==len(rs)==len(ns)
        for day,rating,count in zip(ds,rs,ns):
            if '2016-10-10'<=day<='2017-02-20':
                rows.append((ident,day,float(rating),float(count)))
    w=pd.DataFrame(rows,columns=['gmap_id','week','rating','reviews'])
    before=len(w);w=w.drop_duplicates()
    conflict=w[w.duplicated(['gmap_id','week'],keep=False)]
    assert conflict.empty,'Conflicting business-week outcomes must be resolved'
    w=w[w.rating.between(1,5)&w.reviews.gt(0)].merge(candidates,on='gmap_id',validate='many_to_one')
    assert pd.to_datetime(w.week).dt.dayofweek.eq(0).all()
    w.to_csv(OUT/'both_county_shock_weekly.csv',index=False)
    audit={'source_business_rows_scanned':scanned,'candidate_businesses':len(candidates),
           'candidate_counts':candidates.groupby(['trump','group']).size().reset_index(name='n').to_dict('records'),
           'source_ids_found':len(found),'source_ids_missing':len(missing_ids),
           'weekly_rows':len(w),'exact_duplicates_removed':before-len(w),
           'outcome_source':str(SOURCE),'vote_rule':'Trump >0.50; non-Trump <=0.50; missing excluded',
           'candidate_sha256':fingerprint['candidate_sha256'],'source_records_sha256':sha256(extracted)}
    (OUT/'both_county_data_audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2),flush=True)

if __name__=='__main__':main()
