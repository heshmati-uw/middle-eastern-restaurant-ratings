# Restaurant price and format matching

This is an exploratory sensitivity analysis using undated Google metadata. It does not establish a causal election or ban effect.

Open `analysis_clean/full_pre_election_core/attribute_matching/matching_report.html` after extracting the archive. All three cuisine comparisons, both events, both county strata, sample flow, balance and weekly plots are included.

Matching: symmetric optimal 1:1 without replacement, exact county and dollar-sign price tier. PriceFormat also requires the same recorded dine-in/takeout/delivery and service-recording status. Remaining attributes and geography enter the matching cost. Ratings and trends are not matching inputs. Each retained restaurant has unit weight; inference clusters by county. Some within-county matches are geographically distant.

Election: Oct 10–Nov 6 versus Nov 14–Dec 11, 2016. Ban: Jan 2–22 versus Jan 30–Feb 26, 2017; Christmas/New Year weeks excluded. Cuisine labels use the full raw pre-election core scan. MED excludes core mentions, but may have shared dish mentions.

ME minus WPME in Trump counties after the ban: price matching -0.528 stars (p=.0821; 27/27 restaurants); price plus format -0.301 (p=.4210; 20/20). Joint pretrend p=.0318 and .000248 respectively, with only 11 and 9 counties. Matching does not resolve the pretrend problem.

Reproduction from the repository/extracted workspace root:
1. Install R data.table and fixest, and Python numpy/pandas/scipy.
2. Run `Rscript analysis_clean/model_attribute_matches.R`.
3. Run `python analysis_clean/report_attribute_matching.py`.

The R script regenerates the two large numerical-verification input CSVs omitted from this archive. The independent Python verifier checks all 48 mean models and 48 weekly models, including county-clustered standard errors and estimable joint pretrend tests. verification.json records the checks.

Frozen original and matched restaurant data plus the weekly input are included, allowing model reproduction without raw files. To reconstruct matching, run match_restaurant_attributes.py with the earlier full_pre_election_core and holiday-sensitivity snapshots. prepare_matching_attributes.py reconstructs attributes from the local raw metadata paths recorded in the script; raw metadata files and reviewer text are not redistributed.

Google price/format attributes are undated and include pandemic-era listings; missing flags mean not recorded rather than verified absence. These variables cannot be assumed to describe restaurants in 2016. Raw p symbols: + <.10, * <.05, ** <.01, *** <.001.
