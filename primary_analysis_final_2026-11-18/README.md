# Primary analysis - final 11/18 (November 18, 2026)

This is the approved starting point for the next session. Earlier analyses remain archived; do not substitute their samples, dictionaries, matching rules, or estimators for this checkpoint.

## Start here

- Read [the shareable PDF](restaurant_positioning_ban_results.pdf).
- Download and extract [the reproducibility bundle](primary_analysis_final_2026-11-18.zip). Open `analysis_clean/original_primary_county_fe/regression_tables.html` locally. It includes the observed-means figure, methods, compact Panels A-C, and no-controls / earlier-controls / all-controls checks. A separate HTML appendix shows all coefficients.
- The main specification is the **all-controls ban-only restaurant-level county-FE model**. The figure shows **observed equal-restaurant pre/post means**, annotated with all-controls relative-change estimates and p values, not standardized lines.

## Frozen definitions and estimator

- Original 20 primary-category ME rules (including Halal, North African and Shawarma categories), preserved in `analysis_clean/config.json`. Names and secondary categories do not override primary labels.
- WPME: primary Mediterranean plus pre-election hummus OR baba-ghanoush review evidence. MED: primary Mediterranean with searchable pre-election review text but neither mention. Unknown pre-election text is excluded from the Mediterranean comparison frame. ME does not require food mentions.
- Tags use reviews strictly before November 8, 2016 UTC. All rated outcome reviews are used regardless of text or food mentions.
- Ban pre: December 26, 2016-January 22, 2017. Post: January 30-February 26, 2017 (UTC). Mixed event week omitted, no other holiday exclusions.
- One observation per restaurant: post mean rating minus pre mean rating. Equal restaurant weights, both periods required, no matching. Each pair uses counties containing both groups.
- Separate Trump-majority (>50% of all-candidate 2016 presidential votes) and other-county regressions, with county FE. Stable restaurant intercepts are differenced out, not separate restaurant dummy regressors.
- Main controls: earlier mean rating and log(1 + review count), October 10-November 6, 2016; price-tier indicators; listed dine-in, takeout, delivery and alcohol; missing-data indicators. Pooled direct tests interact control slopes with Trump-majority status as well as positioning.
- Price/service metadata are undated snapshots and are not confirmed to precede the ban. Earlier-controls-only models are retained as the cleaner timing robustness check. Missing-data indicators preserve the samples.
- County-clustered CR1 SEs, original nonnested FE correction, t df = counties minus one. Raw two-sided p values: + <.10, * <.05, ** <.01, *** <.001. No multiplicity adjustment in the main tables.

## Main all-controls results

| Comparison | Non-Trump estimate (p) | Trump estimate (p) | Direct Trump minus non-Trump (p) | Non-Trump / Trump N |
|---|---:|---:|---:|---:|
| WPME - ME | -0.055 (.278) | +0.334 (.026) | +0.390 (.009) | 2,216 / 214 |
| WPME - MED | -0.053 (.331) | +0.032 (.828) | +0.085 (.580) | 1,837 / 230 |
| ME - MED | -0.031 (.531) | -0.314 (.027) | -0.284 (.042) | 1,890 / 157 |

N is restaurants, not reviews. These are separate pairwise shared-county samples, not one common three-group regression. Positive differences mean the first group's change is higher; they do not establish that its own rating increased. The prior parallel-trends and specification exploration do not establish a causal ban effect. This checkpoint is exploratory correlational evidence to accompany future experimental work.

## Reproduce from frozen inputs

The ZIP preserves analysis-ready restaurant data, rating-only individual review records, all 27 control-check designs/covariances, results, source scripts and provenance. No review text or multi-gigabyte raw archives are included. Older election/dictionary files inside the provenance folder are historical inputs, not part of the approved main presentation.

From the extracted root, with Python (pandas, numpy, scipy, reportlab, pypdf) and R (fixest) installed:

```
python run_primary_analysis.py
```

If Rscript is not on PATH, use `python run_primary_analysis.py --rscript "C:/Program Files/R/R-4.5.0/bin/Rscript.exe"`. The runner refits the 27 ban models from frozen `controls_preview/analysis_data.csv`, independently checks estimates/SEs, rebuilds the observed-means figure with full-controls annotations, builds compact tables and the full appendix, and exports the nine-page PDF. PDF export uses Windows Arial fonts. Running from raw source archives instead requires the original Dropbox sources and prerequisite geography/metadata files documented in the retained provenance scripts; it is not required to reproduce this checkpoint.

The old preview-only verification records document immutability at the time of that preview. Use `checkpoint_verification.json` for numerical checks after the user-authorized report edits. `SHA256SUMS.json` inside the ZIP records the frozen files before extraction/rerun.

## Next session

Start from this checkpoint and the PDF. Maintain the current definitions, sample restrictions, full-controls main model, observed-means figure, and control-check progression unless explicitly changing them. Discuss extensions as robustness checks and keep this dated checkpoint intact.
