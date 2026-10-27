# Full-sample descriptive and correlational restaurant analysis

This is the current full-sample analysis, replacing causal-event interpretations with observed associations. ME, WPME and review-screened Mediterranean groups; both the election and ban; separate Trump/non-Trump county and precinct classifications. No matching, price/format availability or local-common-group restrictions. Equal restaurant weights.

Download full_correlational_sample.zip, extract into the workspace root, and open analysis_clean/full_pre_election_core/correlational_full_sample/correlational_report.html. The report contains all pre/post averages, 24 cuisine contrasts, sample sizes, raw p symbols (+ included), pointwise confidence intervals, weekly rating/count plots, state coverage and classification overlap. Political difference-of-contrast tests and continuous vote-share regressions are supplements. Adjusted Holm p-values are companion columns/downloads, not the primary display.

## Sample sizes

| Event | Voting geography | Trump: ME / WPME / MED | Non-Trump: ME / WPME / MED |
|---|---|---:|---:|
| Election | County | 101 / 96 / 218 | 1069 / 825 / 991 |
| Election | Precinct | 110 / 122 / 244 | 1058 / 797 / 961 |
| Ban | County | 126 / 102 / 260 | 1195 / 908 / 1096 |
| Ban | Precinct | 128 / 131 / 285 | 1191 / 877 / 1066 |

County-linked totals are 3300 for election and 3687 for ban. Precinct-linked totals are 3292 and 3678. These are event-specific cohorts, not a common-business panel across both shocks. The same restaurants are used for all three contrasts within each event/geography/political stratum. County and precinct records must not be stacked as independent observations.

## Findings and interpretation

None of the 24 primary within-political-group cuisine comparisons has raw p<.05. ME-WPME changes in Trump counties are -.133 stars after the election (p=.283) and -.108 after the ban (p=.379); in non-Trump counties +.023 (p=.627) and +.064 (p=.197). Precinct-based signs differ. ME-MED after the ban in Trump precincts is +.168 (p=.066). The corresponding Trump-minus-non-Trump precinct contrast is +.197 (raw p=.0476), but not significant after its 12-test-family Holm correction. None of the continuous cuisine-slope contrasts has p<.05. Non-significance is not equivalence or proof of no relationship.

Primary regressions estimate unadjusted cuisine differences in restaurant rating changes, not causal effects and not the earlier within-county FE estimand. Pretrend problems, changing reviewers and selective observation remain. Earlier matching/FE analyses are preserved as separate exploratory specifications, not pooled into this report.

Trump-majority means >50% of all-candidate votes; non-Trump means <=50%, not necessarily Clinton-majority. County and precinct statuses are based on their respective voting. About 14% of precinct-linked restaurants have differing county/precinct classifications. Precinct linkage uses the existing SAGE 2016 spatial/vote quality screen. Neighborhood voting is not reviewer ideology.

## Windows, groups and weighting

Election Oct10-Nov6 vs Nov14-Dec11, 2016. Ban Dec26-Jan22 vs Jan30-Feb26, 2017. Four complete weeks each side; mixed event weeks omitted. Holidays included. Dec19 Christmas week is outside the four-week ban baseline but is included in the longer trend plot.

ME uses the unchanged primary-category definition. WPME is primary Mediterranean with pre-election core dish evidence from the full raw review scan. MED has primary Mediterranean, eligible pre-election review text and no core mention; shared dishes allowed. Unknown text histories remain excluded. No mention is not proof of menu absence. Detailed raw classification provenance is preserved in the earlier full_pre_election_core archive.

Within restaurant-period, review ratings aggregate using review counts. Across restaurants, each restaurant gets one unit of weight. Each primary model has all three cuisine indicators, estimated separately by event/geography/political category. County-clustered CR1 inference uses G/(G-1)*(N-1)/(N-K) and t df G-1, including precinct analyses. Political-heterogeneity models retain cross-stratum within-county covariance. Continuous regressions use cuisine-specific linear slopes per 10pp Trump share. No matching or covariate/FE adjustment is applied. Weekly raw curves weight each observed restaurant equally within that week; counts show composition changes.

## Reproduction

Requires Python numpy/pandas/scipy and R data.table/fixest/jsonlite.

python analysis_clean/prepare_full_correlational.py
Rscript analysis_clean/full_correlational_models.R
python analysis_clean/report_full_correlational.py

The archive includes frozen source aggregates and final restaurant-level analysis data, so original multi-gigabyte review files are not required. Preparation regenerates weekly_observations.csv; R regenerates model_verification_inputs.csv. Those redundant large CSVs are omitted from the archive. Independent Python checks reproduce all 32 OLS models and county-clustered covariance matrices plus all 132 reported linear contrasts, p-values and intervals. No reviewer text or reviewer IDs are redistributed. Input and archive hashes are recorded.
