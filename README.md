# Middle Eastern restaurant ratings

## Latest analysis: continuous voting shares, with county fixed effects

The latest dictionary-sensitivity figures are in [CONTINUOUS_DICTIONARY_SENSITIVITY.md](CONTINUOUS_DICTIONARY_SENSITIVITY.md) and [continuous_dictionary_county_fe.zip](continuous_dictionary_county_fe.zip): all three contrasts, both events, county/precinct shares, six definitions including full-raw core, and independent verification. No American group or proposed expanded positioning classification has been added. None of the 72 slope comparisons has raw p<.05.


The main political measure is **actual Trump vote share**, separately at county and precinct levels, with no majority split. ME, WPME and review-screened Mediterranean use full eligible samples, equal restaurant weights, four-week windows and holidays included. County-FE models and unadjusted continuous associations are both reported as conditional/descriptive associations, not causal effects.

See [CONTINUOUS_VOTING_COUNTY_FE.md](CONTINUOUS_VOTING_COUNTY_FE.md) and download [continuous_voting_county_fe.zip](continuous_voting_county_fe.zip) for current reports, fitted curves, data, scripts and independent verification. None of the 12 county-FE cuisine slope differences is significant at .10. County samples have 3,300 election and 3,687 ban restaurants; precinct samples have 3,292 and 3,678. County vote-share main effects are absorbed by county FE; cuisine-by-share differences remain estimable. Precinct share varies within counties.

The archive also restores the screenshot's original county-FE dictionary forest plots, preserving their older split-county specifications and labels in a historical gallery. [FULL_CORRELATIONAL_ANALYSIS.md](FULL_CORRELATIONAL_ANALYSIS.md) and [full_correlational_sample.zip](full_correlational_sample.zip) preserve the preceding full-sample descriptive report; earlier matching and causal-style explorations are separate snapshots.

## Archived initial ME/WPME/American snapshot

Archived initial research snapshot: four-week restaurant rating comparisons around the 2016 election and the January 2017 travel ban, in Trump-majority and other counties. ME, WPME, and American groups are mutually exclusive. Each restaurant receives equal weight in group comparisons.

## Main findings

| Shock | ME minus American change: Trump counties | Other counties | Trump minus other | Two-sided p |
|---|---:|---:|---:|---:|
| Election | -0.249 stars | -0.033 stars | -0.217 stars | 0.0314 |
| Ban | -0.110 stars | +0.013 stars | -0.122 stars | 0.1284 |

The election contrast suggests ME lost more ground relative to American restaurants in Trump counties. Its Holm-adjusted p across the two ME-American shocks is 0.0629 (0.1887 across all six direct comparisons). WPME county-type differences are not statistically clear. These are exploratory descriptive comparisons: the four-week window was selected after inspecting longer windows. They do not establish causal effects or discrimination.

## Rerun the current analysis

Requires Python 3.11+ and R with fixest, data.table, and jsonlite. Tested with R 4.5.0; package versions are in county_difference_R_session.txt.

```sh
python -m pip install -r requirements.txt
Rscript install_dependencies.R
python run_analysis.py
```

If Rscript is not on PATH, pass its full executable path as the first argument to run_analysis.py. Run dependency installation from this repository directory. The runner works from any working directory. It regenerates the result tables, R model archive, verification JSON, and county_difference_report.html. Open that HTML file locally after downloading/cloning the repository. Independent NumPy checks verify all 18 estimates and county-clustered standard errors, reconstruct restaurant means, and check that the earlier Trump estimates are unchanged.

## Data and methods

both_county_shock_weekly.csv is the exact analysis-ready input: 139,864 observed business-weeks from 13,861 candidate businesses. both_county_candidates.csv records the full eligible pool, including businesses without reviews in every comparison period. The weekly input contains business ID, Monday week, average rating, review count, group, county FIPS, 2016 Republican vote share, and Trump-majority indicator. Missing review weeks are absent, not zero-valued ratings. County FIPS must be read as text to retain leading zeroes.

Election: October 10-November 6 vs November 14-December 11, 2016. Ban: December 26, 2016-January 22, 2017 vs January 30-February 26, 2017. Mixed event weeks are excluded. The election comparison ends before the ban; the ban baseline is after the election.

Within each restaurant and period, weekly rating averages are weighted by review counts. Restaurants must have observations both before and after. The cross-restaurant analysis gives each restaurant's rating change equal weight. Trump-majority means Republican vote share greater than 50%; other counties have share at or below 50%. Missing geography/share is excluded. Pairwise OLS models compare restaurant changes; pooled models use change ~ treated * trump. Standard errors cluster by county, use G/(G-1) * (N-1)/(N-K) correction, and use G-1 degrees of freedom for t tests and intervals.

ME uses a primary category from the Middle Eastern category list in the archived config.json (including Persian, Lebanese, Halal, North African, and other listed cuisines). WPME is primary-Mediterranean with the saved business-level baba-ghanoush review flag equal to one; MED is primary-Mediterranean with that flag zero. These flags are inherited from the modern saved classification, so they can use information beyond the event window. American uses the historical primary-American category and common geocoding rules. The full definitions, selection history, extraction scripts, earlier baselines and window sensitivities are preserved in historical_code_and_reports.zip. Current comparisons include ME-American, WPME-American, and WPME-ME. Mediterranean was examined earlier and is documented in that archive; it is not a separate group in these current tests.

county_four_week_restaurant_changes.csv contains each eligible restaurant's pre/post rating, review counts, observed week counts, and change for each shock. county_four_week_descriptives.csv contains equally weighted group averages. county_stratum_four_week_results.csv contains the 12 within-stratum contrasts; county_difference_four_week_tests.csv contains the six direct county-type differences, intervals, raw p-values, directional p-values, and multiplicity adjustments. county_four_week_models.rds preserves fitted R models. election_ban_results.csv is the earlier result table used as a regression check.

## Provenance and scope

Outcomes were extracted from the original Google Reviews/Reviews_Data_Combined.csv business-level weekly arrays. Source coverage and selection checks are recorded in both_county_data_audit.json. No candidate IDs were missing from that source. This repository contains the current aggregate analysis data, not the multi-gigabyte original raw review/metadata files or review text. It can reproduce the current estimates without those original files. Rebuilding selection/extraction from raw sources requires the original project files and the local paths/dependencies documented in the historical archive; prepare_county_comparison.py is retained as provenance rather than as the portable entry point.

SHA256SUMS.json records the packaged file hashes before upload. Existing source files were not modified. This private research snapshot grants no additional license or redistribution rights to underlying data.
