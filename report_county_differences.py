"""Validate and report the four-week county-stratum and interaction tests."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;OUT=HERE

def main():
    s=pd.read_csv(OUT/'county_stratum_four_week_results.csv')
    i=pd.read_csv(OUT/'county_difference_four_week_tests.csv')
    q=pd.read_csv(OUT/'county_four_week_restaurant_changes.csv',dtype={'county_fips':'string'})
    d=pd.read_csv(OUT/'county_four_week_descriptives.csv')
    w=pd.read_csv(OUT/'both_county_shock_weekly.csv',dtype={'county_fips':'string'})
    audit=json.loads((OUT/'both_county_data_audit.json').read_text())
    cfg=json.loads((HERE/'shock_specifications.json').read_text())
    specs=[x for x in cfg['main_windows']+cfg['sensitivity_windows'] if x['weeks']==4]
    # Independently reconstruct before/after business means and equal-weight changes.
    for spec in specs:
        x=w[((w.week>=spec['pre_start'])&(w.week<=spec['pre_end']))|
            ((w.week>=spec['post_start'])&(w.week<=spec['post_end']))].copy()
        x['period']=np.where(x.week<=spec['pre_end'],'pre','post')
        x['score_sum']=x.rating*x.reviews
        b=x.groupby(['gmap_id','period'])[['score_sum','reviews']].sum()
        b['rating']=b.score_sum/b.reviews
        b=b.rating.unstack('period').dropna().reset_index()
        saved=q[q.shock==spec['shock']]
        check=saved.merge(b,on='gmap_id',validate='one_to_one')
        assert len(check)==len(b)==len(saved)
        assert (check.rating_pre-check.pre).abs().max()<1e-12
        assert (check.rating_post-check.post).abs().max()<1e-12
    checks=[]
    def verify(data,columns,coefficient,estimate,se):
        X=np.column_stack(columns)
        y=data.change.to_numpy();inv=np.linalg.inv(X.T@X)
        beta=inv@X.T@y;residual=y-X@beta
        code=pd.factorize(data.county_fips)[0];G=int(code.max()+1);N=len(y);K=X.shape[1]
        score=np.zeros((G,K));np.add.at(score,code,X*residual[:,None])
        cov=inv@score.T@score@inv*(G/(G-1))*((N-1)/(N-K))
        manualse=np.sqrt(cov[coefficient,coefficient])
        assert abs(beta[coefficient]-estimate)<1e-10
        assert abs(manualse-se)<1e-10
        checks.append((abs(beta[coefficient]-estimate),abs(manualse-se)))
    for row in s.itertuples():
        treated,control=row.comparison.split(' vs ')
        x=q[q.shock.eq(row.shock)&q.trump.eq(row.trump)&q.group.isin([treated,control])]
        t=x.group.eq(treated).astype(float).to_numpy()
        verify(x,[np.ones(len(x)),t],1,row.estimate,row.se)
        assert len(x)==row.restaurants
    for row in i.itertuples():
        treated,control=row.comparison.split(' vs ')
        x=q[q.shock.eq(row.shock)&q.group.isin([treated,control])]
        t=x.group.eq(treated).astype(float).to_numpy();tr=x.trump.to_numpy()
        verify(x,[np.ones(len(x)),t,tr,t*tr],3,row.difference,row.se)
        assert abs(row.difference-(row.trump_contrast-row.nontrump_contrast))<1e-12
    # Reproduce the previous six Trump-county models exactly.
    old=pd.read_csv(OUT/'election_ban_results.csv')
    old=old[old.weeks.eq(4)]
    merged=s[s.trump.eq(1)].merge(old,on=['shock','comparison'],suffixes=('_new','_old'),validate='one_to_one')
    assert len(merged)==6
    for col in ['estimate','se','p']:
        assert (merged[col+'_new']-merged[col+'_old']).abs().max()<1e-12
    def p(x):return '<0.001' if x<.001 else f'{x:.3f}'
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+escape(h)+'</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    primary=i[i.comparison.eq('ME vs American')]
    body='''<h1>Is ME’s decline larger in Trump-majority counties?</h1>
    <p><strong>In the four-week election window, yes in the unadjusted direct test:</strong> ME’s change relative to American restaurants is 0.217 stars more negative in Trump-majority counties (two-sided p = 0.031). The corresponding ban-period difference is not statistically clear (−0.122 stars; p = 0.128).</p>
    <p>The election p-value becomes 0.063 after Holm adjustment across the two requested ME–American shock tests. The four-week window was chosen after inspecting the earlier window results, so these remain exploratory findings.</p>
    <h2>Same windows and equal restaurant weights</h2>
    <ul><li><strong>Election:</strong> October 10–November 6, 2016 versus November 14–December 11, 2016.</li>
    <li><strong>Ban:</strong> December 26, 2016–January 22, 2017 versus January 30–February 26, 2017.</li></ul>
    <p>The complete shock week is excluded. Every restaurant must have reviews in both periods. Reviews are averaged within each restaurant-period first, then each restaurant’s change receives equal weight. All groups use outcomes from the same rebuilt combined weekly source.</p>
    <p>Trump-majority counties have Republican vote share greater than 50%; other counties have share at or below 50%. “Non-Trump” is this operational threshold, not necessarily a Democratic-majority or Democratic-winner definition. Missing county/vote shares are excluded.</p>
    <h2>Direct test: ME versus American</h2><p>The estimate below is (ME–American change in Trump counties) minus (ME–American change in other counties). Negative means ME lost more ground in Trump counties. This directly tests the difference; it does not infer a difference merely because one subgroup has a significant p-value and the other does not.</p>'''
    body+=table(['Shock','Trump-county contrast','Other-county contrast','Difference between contrasts','95% CI','Two-sided p','Holm p across two shock tests'],[
        [a.shock,f'{a.trump_contrast:+.3f}',f'{a.nontrump_contrast:+.3f}',f'{a.difference:+.3f}',
         f'[{a.low:+.3f}, {a.high:+.3f}]',p(a.p),p(a.p_holm_primary_two)] for a in primary.itertuples()])
    body+='<h2>Four-week comparisons in non-Trump counties</h2><p>Positive WPME–ME means WPME improved relative to ME. All changes are in star-rating points.</p>'
    body+=table(['Shock','Comparison','Relative change','95% CI','p','Restaurants: first / second group'],[
        [a.shock,a.comparison,f'{a.estimate:+.3f}',f'[{a.low:+.3f}, {a.high:+.3f}]',p(a.p),
         f'{a.treated_restaurants:,} / {a.control_restaurants:,}'] for a in s[s.trump.eq(0)].itertuples()])
    body+='<h2>All direct between-county tests</h2>'
    body+=table(['Shock','Comparison','Trump minus other contrast','95% CI','p','Holm p across six direct tests'],[
        [a.shock,a.comparison,f'{a.difference:+.3f}',f'[{a.low:+.3f}, {a.high:+.3f}]',p(a.p),p(a.p_holm_all_six)] for a in i.itertuples()])
    body+='<p>No WPME between-county differential is statistically clear. Adjusting across all six direct comparisons gives election ME–American p = 0.189. These adjustment families do not account for every earlier baseline/window choice.</p>'
    body+='<h2>Restaurant-level average ratings</h2>'
    body+=table(['Shock','County group','Restaurant group','Restaurants','Before','After','Change'],[
        [a.shock,'Trump-majority' if a.trump else 'Other',a.group,f'{a.restaurants:,}',f'{a.pre:.3f}',f'{a.post:.3f}',f'{a.change:+.3f}'] for a in d.itertuples()])
    body+='<h2>Estimation and verification</h2><p>Within each county-vote group, OLS regresses each restaurant’s after-minus-before mean rating on a cuisine-group indicator. The direct test pools the two county-vote groups and adds the county-vote indicator and its interaction with the cuisine indicator. The interaction coefficient equals the difference between subgroup contrasts. In period-level notation, it is the post × cuisine × Trump-county interaction.</p>'
    body+='<p>Standard errors cluster by county, using G/(G−1) × (N−1)/(N−K) small-sample correction; two-sided t tests and intervals use G−1 degrees of freedom. A directional, negative-tail p-value is also exported for the direct test, but the headline results use two-sided inference.</p>'
    body+=f"<p>All {audit['candidate_businesses']:,} candidate IDs were found in the source file. The control pool is constructed using the same historical primary-American eligibility and geocoding rules in both county groups, rather than using keyword-selected American restaurants in one group. Focal ME/WPME classifications use the same modern mapping in both groups. Adding the non-Trump data reproduces all six prior Trump-county coefficients, standard errors and p-values exactly.</p>"
    body+='<p>Independent NumPy regressions and county sandwich calculations reproduce all 18 model estimates/standard errors. Restaurant-period means were independently reconstructed as well. These are descriptive group-change contrasts, not causal effects of the election/ban or proof of discrimination. County types can differ in restaurant/reviewer composition, seasonality and local conditions; no county-fixed-effect or demographic adjustment is imposed in these raw-mean contrasts.</p>'
    body+='''<h2>Files</h2><ul>
    <li><a href="county_stratum_four_week_results.csv">Within-county-group estimates and p-values</a></li>
    <li><a href="county_difference_four_week_tests.csv">Direct differences, intervals, and p-values</a></li>
    <li><a href="county_four_week_descriptives.csv">Group means and sample counts</a></li>
    <li><a href="county_four_week_restaurant_changes.csv">Restaurant-period averages and changes</a></li>
    <li><a href="both_county_data_audit.json">Source coverage and selection audit</a></li>
    <li><a href="county_difference_verification.json">Independent numerical checks</a></li>
    <li><a href="prepare_county_comparison.py">Data preparation</a> and <a href="county_difference_models.R">model code</a></li></ul>'''
    style='body{font:16px/1.6 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#24323b}h1,h2{color:#173f46}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid #d8e2e5;vertical-align:top}th{background:#edf4f5}.scroll{overflow-x:auto}a{color:#14637d}'
    path=OUT/'county_difference_report.html'
    path.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>County comparison of four-week shocks</title><style>'+style+'</style><body>'+body+'</body></html>',encoding='utf-8')
    verification={'models_checked':len(checks),'independent_point_and_covariance_checks_passed':True,
                  'independent_restaurant_period_means_verified':True,'previous_Trump_results_unchanged':True,
                  'max_coefficient_error':max(x[0] for x in checks),'max_se_error':max(x[1] for x in checks)}
    (OUT/'county_difference_verification.json').write_text(json.dumps(verification,indent=2))
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            if tag=='a':
                href=dict(attrs).get('href','')
                if href and not href.startswith(('http','#')):assert (OUT/href).exists(),href
    Links().feed(path.read_text(encoding='utf-8'))
    assert len(s)==12 and len(i)==6 and len(checks)==18
    print(json.dumps(verification,indent=2))

if __name__=='__main__':main()
