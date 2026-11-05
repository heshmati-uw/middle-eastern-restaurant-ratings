# Associational analysis of restaurant positioning

This folder implements a separate, exploratory associational workflow. Earlier repository analyses are preserved. The core questions concern positioning and rating levels, political heterogeneity, and temporal variation. Event coefficients are associations, not causal effects.

## Agreed starting specification

- Outcome period: November 14, 2016 through April 9, 2017, inclusive, using UTC posting dates.
- Unit: one restaurant. Average its deduplicated posted ratings in the outcome period; give every restaurant equal regression weight.
- Labels: American, Mediterranean, literal Middle Eastern, and National. National pools Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite primary categories. Exclude halal and kebab shop from these four groups.
- All restaurants with an outcome review and valid linked county/vote are eligible. No requirement for reviews in multiple periods, no food matching, and no positive historical-review minimum.
- Historical volume: all valid raw reviews observed strictly before November 8, 2016, with log(1 + count). A zero is zero records in the supplied corpus, not proof that the restaurant was new.
- Primary model: county fixed effects and historical volume. Report all six positioning contrasts, raw and Holm-adjusted p-values, sample sizes, county counts and 95% county-clustered intervals.
- County-FE sample retains counties containing at least two of the four label groups. All four groups are estimated jointly. This does not require every county to contain every pair; the county-by-label support table makes that limitation visible. Pair-specific shared-county models are a planned check.
- Price is taken from original metadata and included only as a sensitivity model, with an explicit missing category. Its historical validity is not established.

## Start from the raw files

Requires Python 3 (standard library only) and R (base packages only). From the repository root:

```text
python associational_analysis/01_build_from_raw.py --raw-dir PATH_TO_ORIGINAL_INPUTS --geography PATH_TO_METADATA_WITH_GEOGRAPHY.csv
Rscript associational_analysis/02_positioning_models.R
```

`--raw-dir` must contain the original 52 `meta-*.json.gz` and 52 `review-*.json.gz` files. The geography file is the existing `analysis_clean/expanded_positioning/metadata_with_geography.csv` linked input, also distributed in the earlier expanded-positioning project bundle. Only its business-ID/county/vote linkage is reused. Primary labels and prices are rebuilt from raw metadata; outcomes and historical counts are rebuilt from raw reviews. County assignment and election returns are linked inputs, not inferred from review text.

The builder scans raw metadata, excludes conflicting duplicate metadata, joins valid geography, scans raw review files and deduplicates across files on SHA256 of JSON `[gmap_id,user_id,time,rating,text]`. It exports no reviewer IDs or full review text. Local intermediate hashes, selected records, restaurant inputs and the source manifest stay in the ignored `private/` directory. File sizes, modification times and the linkage-file SHA256 are recorded; raw gzip contents are not separately hashed. Source files are never modified.

Re-running the model uses the cached raw-derived restaurant file. Re-running the builder rebuilds the scan and deduplication database. The initial scan can take several minutes and requires disk space for private intermediates.

## Step-by-step implementation plan

1. **Freeze definitions and audit inputs.** Confirm the outcome calendar, mutually exclusive primary labels, raw-source coverage, missing geography/price and counts by positioning and politics. Deduplicate before computing outcomes. Do not treat unknown historical label visibility as measured fact.
2. **Estimate rating-level associations.** Run county-FE models without controls, then with prior volume. Add snapshot price as sensitivity. Report adjusted contrasts; subsequently produce standardized means on explicit common support. Separate available-sample and fixed-cohort questions.
3. **Estimate political moderation.** Add each nonreference positioning indicator interacted with county Trump share, centered at 50% and scaled per 10 percentage points. County FE absorb the standalone share term. Show the direct differences between positioning gradients, not separate significance tests by majority group. Check pair-specific shared counties and influential counties/cuisines.
4. **Add culinary comparability.** Rebuild food evidence strictly before November 8 from raw text. For visibly ME versus Mediterranean, apply the same dictionary in both groups, add culinary profiles, and compare with existing distinctive-dish/tradition matching as sensitivity. Do not interpret American comparisons as holding food constant. No culinary adjustment is included in the first pass.
5. **Assess recurrence.** Re-estimate on fixed calendar blocks. Report available and balanced cohorts separately. Restaurant fixed effects are useful for changes, but absorb stable positioning differences. Do not call repeated estimates independent replications.
6. **Add event-period associations.** Estimate restaurant-period ratings with county and period FE, positioning, positioning-by-vote, positioning-by-post, vote-by-post, and positioning-by-vote-by-post interactions. For Orlando and the ban, report one-, two-, and four-week windows together. Main descriptive models use all available restaurant-periods; paired and fixed-cohort placebo samples are checks. Event estimates are not causal effects.
7. **Audit inference and interpretation.** County clustering, direct contrasts, prespecified comparison families and Holm adjustments. Add small-cluster sensitivity where support is sparse. Check raw data, geography, review activity, leave-one-county and leave-one-cuisine influence. Analyze contemporaneous review counts separately; do not silently use them as predetermined controls.

## Implementation status

Steps 1-3 have an initial raw-derived pipeline and baseline/snapshot-price specifications. Step 4 now has a separate raw-text culinary-support analysis described below. Steps 5-7 remain planned extensions. The present political models are an initial pass, not the completed robustness sequence. The outcome window was chosen before this pipeline was run, after earlier exploratory analyses; this is not a preregistration.

`outputs/` contains aggregate results and validation records. No raw review text, reviewer IDs, or individual restaurant rows are committed. Interpret National versus American and Mediterranean versus ME as different theoretical comparisons. Mediterranean positioning is the observed label; whiteness, stigma and authenticity remain constructs requiring additional evidence.

## Initial run on November 4, 2026

The raw scan read 666,324,103 review rows. Of 1,626,521 selected historical/outcome records, 1,595,419 remained after deduplication. There were 45,335 raw-metadata businesses with qualifying primary labels; 45,151 had usable geography and no metadata conflicts. The outcome sample contains 34,234 restaurants. County-FE support restricts this to 24,706 restaurants in 526 counties with at least two positioning labels.

With county FE and log prior volume, National, literal Middle Eastern and Mediterranean labels have higher ratings than American labels by 0.182, 0.228 and 0.194 stars (all p < .001). The remaining three positioning contrasts are uncertain. These broad label comparisons do not hold cuisine constant and do not reproduce the earlier food-matched estimand.

Initial political-gradient differences per 10 percentage points of Trump share are +0.034 for National versus American (p = .017; Holm p = .069), +0.044 for literal ME versus American (p = .00054; Holm p = .0033), and +0.017 for Mediterranean versus American (p = .013; Holm p = .066). All six gradients are exported. These are cross-county differences in within-county positioning contrasts, not absolute effects of county politics on a label group.

The absorbed county-FE coefficients and county-clustered covariance were independently checked against explicit county-dummy OLS on 20 counties, agreeing within 1e-8. Figure: [first pass](outputs/first_pass.png). Full estimates, Holm p-values and sample counts are in the adjacent CSVs. The next step is auditing culinary evidence and comparison-specific geographic support, before drawing substantive conclusions about stigma or authenticity.

## Culinary comparability extension

Run after the raw-data builder:

```text
python associational_analysis/04_culinary_from_raw.py --raw-dir PATH_TO_ORIGINAL_INPUTS
python associational_analysis/05_culinary_support.py
Rscript associational_analysis/06_culinary_models.R
```

The scanner rereads all 52 original review files for the 5,162 outcome restaurants with Mediterranean, literal Middle Eastern or National primary labels. Food evidence uses valid-star text reviews strictly before November 8, 2016. Each feature is binary presence in at least one review, so duplicated review records cannot change it. The same frozen dictionaries and rules apply to both labels. No outcome-period food evidence is used. This is sentiment-agnostic keyword detection, not manual confirmation of neutral statements or actual consumption.

The comparison pools literal Middle Eastern and National labels as visibly ME. A restaurant is retained only if another restaurant in its county has the opposite positioning and shares either a qualifying dish or a culinary tradition. All qualifying restaurants remain, with equal weights; there is no nearest-neighbor selection or matching weight. Hummus, falafel, baba ghanoush, generic kebab, other shared-sensitivity foods, dolma/dolmeh and shakshouka do not independently establish eligibility. Shared specific dishes such as kibbeh can qualify without being exclusive to a country. The seven-country registry's country-associated entries supply nonexclusive tradition proxies; shared entries do not infer countries. The established core dictionary additionally supplies Levantine, Afghan, Egyptian and Iranian profiles, with exact mappings in `culinary_regional_mapping.json`. These are culinary proxies, not identified restaurant nationalities, and the seven-country registry's classifications do not establish global dish exclusivity.

On the resulting fixed sample, estimate restaurant mean rating on a Mediterranean indicator and county FE, then add log prior review count, then binary dish and tradition profiles. The food-adjusted model is primary; snapshot price is a sensitivity. Food controls include shared dishes even though these cannot independently qualify restaurants. Exact redundant features are removed by QR and recorded. No feature is selected by its p-value. Price accepts dollar tiers 1-4; missing or unrecognized currencies enter the missing category. All models have equal restaurant weights and county-clustered CR1 uncertainty with county-count-minus-one t degrees of freedom. Displayed p-values test the Mediterranean coefficient in nested specifications; they are not independent replications or a family of distinct substantive hypotheses.

Comparable measured offerings do not mean identical menus. Food evidence depends on review availability, dictionary coverage and mention context. This sample can differ from the earlier 563-restaurant matched cohort, which used different labels, timing and selection rules. Snapshot positioning, unmeasured quality, service and reviewer selection preclude a causal interpretation of the label coefficient.

The first culinary run retains 487 restaurants in 57 counties: 215 Mediterranean and 272 visibly ME (181 National and 91 literal Middle Eastern), contributing 12,718 outcome reviews. The Mediterranean coefficient is +0.037 stars with county FE (p = .406), +0.043 after historical volume (p = .312), +0.011 after culinary profiles (95% CI -0.094 to +0.115; p = .841), and +0.002 with snapshot price (p = .969). The primary result does not establish a Mediterranean rating advantage, but its interval still permits modest positive or negative differences. Figure: [culinary positioning](outputs/culinary_positioning.png). These specifications do not test political moderation or event effects. Baseline absorbed coefficients and clustered covariance match explicit county-dummy OLS within 1e-8.

### County vote moderation on the same culinary sample

Run `Rscript associational_analysis/07_culinary_county_vote.R`. Trump-majority means strictly over 50% of the 2016 all-candidate county vote. The sample remains exactly 487 restaurants. Other counties contain 451 restaurants (200 Mediterranean, 251 visibly ME) in 50 counties; Trump-majority counties contain 36 (15 Mediterranean, 21 visibly ME) in seven counties. Outcome reviews number 11,586 and 1,132, respectively.

The pooled model adds Mediterranean x Trump-majority to the county-FE, historical-volume and full culinary-profile specification. The majority main effect is absorbed by county FE. The positioning association varies by county group; culinary and historical-volume slopes remain shared. This is not two independently fitted regressions, which would be fragile with only 36 restaurants in the Trump-majority subset. No price control is added to the primary model.

The adjusted Mediterranean-minus-visibly-ME association is +0.015 stars in other counties (95% CI -0.096 to +0.127; p = .784) and -0.041 in Trump-majority counties (95% CI -0.396 to +0.314; p = .787). The direct difference between associations is -0.056 (95% CI -0.436 to +0.324; p = .729). These results do not establish political moderation, but the sparse Trump-majority sample leaves substantial uncertainty. They do not establish equivalence.

All intervals use county-clustered CR1 covariance. To reflect sparse group support, displayed t degrees of freedom are 49 for other counties and 6 for Trump-majority and the interaction (the smaller county group minus one). This conservative degrees-of-freedom choice is not an exact small-sample correction. Conventional df56 p-values are also exported; the interaction p is .718. The complete adjusted design and covariance are independently checked against explicit county-dummy OLS to 1e-8. Figure: [county vote moderation](outputs/culinary_vote.png); counts, contrasts and validation are in adjacent culinary_vote files.

### Review activity in the seven Trump-majority counties

This descriptive extension uses **all available restaurants** with the four primary-label categories in the seven counties contributing to the culinary-supported Trump-majority sample: El Paso, CO; Brevard and Lee, FL; Sedgwick, KS; Macomb, MI; Monmouth, NJ; and Collin, TX. It does not require culinary evidence, an outcome-period review in the earlier regression window, or activity both before and after the ban. It does not cover every Trump-majority county nationally.

Run `08_county_activity_raw.py --raw-dir PATH_TO_ORIGINAL_INPUTS`, then `09_county_activity_plot.py`, then `Rscript associational_analysis/10_county_activity_figure.R`. The scanner rereads all 52 original review files for December 1, 2015 through April 30, 2017, inclusive, using UTC dates and valid 1-5-star reviews. Binary restaurant-day activity makes duplicate records irrelevant to these counts. Primary categories and county links come from the raw-derived metadata and frozen geography used in the earlier builder. There are 766 metadata restaurants in scope before date-specific review requirements (590 American, 109 Mediterranean, 42 literal Middle Eastern, 25 National).

The monthly plot counts each restaurant once in each month with at least one review. It shows all four categories and a closer view excluding American for readability. January 24 coverage and January 27 implementation are marked; January's monthly total includes both pre- and post-ban activity and cannot identify a discontinuity at either date. Counts measure recorded review activity, not the number of operating restaurants or openings/closures.

The equal-duration before/after table uses December 27, 2016-January 23, 2017 and January 27-February 23, 2017 (28 days each), excluding January 24-26. Counts before, after, both, either, before-only and after-only are exported by category and county. A separate full-window table uses December 1, 2015-January 23, 2017 versus January 27-April 30, 2017; these unequal durations should not be interpreted as a comparable activity-rate test. No hypothesis tests accompany these descriptive counts. Category definitions remain mutually exclusive and unchanged; National comprises Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite labels. Neither halal nor kebab shop is included.


