# Continuous-share dictionary sensitivity with county fixed effects

All three comparisons (ME-WPME, ME-MED, WPME-MED), election and ban, county and precinct vote shares. Equal restaurant weights, full eligible samples, no matching or price restrictions. Political support is continuous; no majority split. Interpret coefficients as conditional associations, not causal effects.

Extract continuous_dictionary_county_fe.zip into the workspace root. Open analysis_clean/full_pre_election_core/correlational_full_sample/continuous_dictionary/dictionary_sensitivity_report.html. Three PNG figures and vector SVG versions reproduce the earlier dictionary forest-plot style, with four panels: election/county share, election/precinct share, ban/county share, ban/precinct share. Each point is a cuisine slope difference in rating stars per 10 percentage points higher Trump share, with pointwise 95% county-clustered confidence intervals, raw p symbols (+ included) and first/second cuisine N.

Six rows: inherited legacy baba flag; saved-text pre-election baba; saved-text pre-election core; saved-text pre-election broad; all-saved broad; full-raw pre-election core. The current full-raw core row is green; older broad row red; narrower pre-election rows blue; potentially post-event-informed definitions grey. Full-raw versus saved-core changes review coverage as well as classification; this is not a pure lexicon-only comparison.

Each dictionary/event/share-level condition uses ONE joint three-group county-FE regression. All three contrasts therefore share the same restaurants and covariance matrix within a row. Dictionary rows can differ in sample membership and cuisine allocation. Unlike the original historical forest plots, there is no pairwise common-county restriction or binary political split. Restaurants in single-cuisine counties remain in the data, though they do not identify county-share interactions.

None of the 72 displayed slope comparisons has raw p<.05. Three older pre-election baba-only results have p between .05 and .10: election precinct WPME-MED -.0782 (p=.0552,94 WPME); ban county ME-WPME -.1489 (p=.0903,98 WPME); ban county WPME-MED +.1387 (p=.0974,98 WPME). None persists across the current full-raw core definition. All 12 full-raw core results exactly reproduce the prior continuous county-FE analysis.

County voting main effects are absorbed by county FE; cuisine slope differences remain estimable. Precinct share varies within county, so a common precinct slope is also included. CR1 covariance uses fixest nonnested county-FE correction and t df=counties-1. Symbols use raw p: +<.10,*<.05,**<.01,***<.001. Companion Holm values across 72 displayed contrasts are downloadable. They do not adjust for every prior project specification or fix confounding.

Election: Oct10-Nov6 vs Nov14-Dec11,2016. Ban: Dec26-Jan22 vs Jan30-Feb26,2017. Holidays included, mixed event weeks omitted. Primary-category and dish-tag rules are retained within each historical definition; the newest main labels use the full raw pre-election core scan. No core mention is not verified menu absence.

Reproduce from workspace root (Python numpy/pandas/scipy; R data.table/fixest):
python analysis_clean/prepare_continuous_dictionary.py
Rscript analysis_clean/continuous_dictionary_models.R
python analysis_clean/report_continuous_dictionary.py

Frozen focal outcome inputs, label assignments, geography and final restaurant-level data are included; no multi-gigabyte raw review scan is needed. R regenerates model_verification_inputs.csv, omitted from this archive. Independent NumPy within-county calculations verify all24 models,72 contrasts,24 joint tests and their clustered uncertainties. Numerical reparameterization from MED to ME reference preserves every pairwise estimate and SE, as verified. Adding a restaurant category is a different sample/model change.

No American category has been added. A proposed broader food-and-label positioning definition (ME-food verified but no explicit ME-associated tag) is discussed in the report but has NOT been applied or substituted into these figures. It would require a broader review scan and a prespecified cue definition; category absence alone does not establish authenticity, white positioning, owner identity or intent.

No reviewer text or reviewer IDs are redistributed. Original source aggregate hashes and the archive SHA256 are recorded.
