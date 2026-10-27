# ME versus WPME: price, dine-in and alcohol, no geographic matching

Extract ME_WPME_price_format.zip into the workspace root. Open analysis_clean/full_pre_election_core/attribute_matching/ME_WPME_price_dine_alcohol/matching_report.html.

Current specification: exact dollar-sign price tier, recorded dine-in flag and recorded alcohol flag. ME and WPME only. Trump/non-Trump county samples separate; no county, state, region or distance used to select matches. Equal restaurant weights. Select min(group counts) per stratum, with reproducible random subsampling without replacement of the larger group and a fixed seed (20261026 with event/county-type offsets). No post-event rating or trend tuning of selection.

Matched N per group (price-only reference -> price+dine-in+alcohol): election Trump 84->80, non-Trump 750->719; ban Trump 87->85, non-Trump 811->794. Sample losses are 2.1%-4.8%. New ME-WPME change estimates: election Trump -.098 (p=.529), non-Trump +.054 (p=.299); ban Trump -.116 (p=.432), non-Trump +.050 (p=.369). No significant mean-change effects.

Main mean model is restaurant-level rating change ~ ME + matching-stratum FE. County-clustered CR1 standard errors. No geographic fixed effects. This differs from earlier county-FE/triplet-FE models; changes cannot be attributed only to matching. Election windows Oct10-Nov6 vs Nov14-Dec11, 2016; ban Dec26-Jan22 vs Jan30-Feb26, 2017. Holidays retained, mixed event weeks excluded.

Weekly model uses restaurant and matching-stratum-by-week FE, total restaurant weight one, county clustering. Diagnostic eligibility needs 2+ pre weeks and 1+ post week, followed by rebalancing within matching strata. Joint pretrend p for new Trump election=.0494, ban=.00634; non-Trump election=.721, ban=.767. Non-rejection is not proof of parallel trends. Eight mean models and eight weekly models (including price-only reference) independently verified.

Metadata are undated snapshots. Dine-in means listed under service options; alcohol flag means alcohol, beer, wine or cocktails listed under offerings. Zero is not recorded, not confirmed absence. Frozen ME/WPME groups use full raw pre-election core tags, same primary-category rule. No reviewer text or reviewer IDs distributed.

Reproduce:
python analysis_clean/ME_WPME_price_only.py
Rscript analysis_clean/ME_WPME_price_only.R
python analysis_clean/ME_WPME_price_only.py --dine-alcohol
Rscript analysis_clean/ME_WPME_price_only.R --dine-alcohol
python analysis_clean/report_ME_WPME_price_format.py

Requires Python numpy/pandas and R data.table/fixest. Frozen inputs included; R regenerates the two omitted large verification CSVs for each specification. Raw metadata reconstruction remains in the earlier attribute_matching archive. Use balance/overlap and historical validity to choose further covariates, not effect significance.
