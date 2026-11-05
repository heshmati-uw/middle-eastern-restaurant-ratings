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

Steps 1-3 have an initial raw-derived pipeline and baseline/snapshot-price specifications. Steps 4-7 are planned extensions, not completed analyses. The present political models are an initial pass, not the completed robustness sequence. The outcome window was chosen before this pipeline was run, after earlier exploratory analyses; this is not a preregistration.

`outputs/` contains aggregate results and validation records. No raw review text, reviewer IDs, or individual restaurant rows are committed. Interpret National versus American and Mediterranean versus ME as different theoretical comparisons. Mediterranean positioning is the observed label; whiteness, stigma and authenticity remain constructs requiring additional evidence.

## Initial run on November 4, 2026

The raw scan read 666,324,103 review rows. Of 1,626,521 selected historical/outcome records, 1,595,419 remained after deduplication. There were 45,335 raw-metadata businesses with qualifying primary labels; 45,151 had usable geography and no metadata conflicts. The outcome sample contains 34,234 restaurants. County-FE support restricts this to 24,706 restaurants in 526 counties with at least two positioning labels.

With county FE and log prior volume, National, literal Middle Eastern and Mediterranean labels have higher ratings than American labels by 0.182, 0.228 and 0.194 stars (all p < .001). The remaining three positioning contrasts are uncertain. These broad label comparisons do not hold cuisine constant and do not reproduce the earlier food-matched estimand.

Initial political-gradient differences per 10 percentage points of Trump share are +0.034 for National versus American (p = .017; Holm p = .069), +0.044 for literal ME versus American (p = .00054; Holm p = .0033), and +0.017 for Mediterranean versus American (p = .013; Holm p = .066). All six gradients are exported. These are cross-county differences in within-county positioning contrasts, not absolute effects of county politics on a label group.

The absorbed county-FE coefficients and county-clustered covariance were independently checked against explicit county-dummy OLS on 20 counties, agreeing within 1e-8. Figure: [first pass](outputs/first_pass.png). Full estimates, Holm p-values and sample counts are in the adjacent CSVs. The next step is auditing culinary evidence and comparison-specific geographic support, before drawing substantive conclusions about stigma or authenticity.
