# Symmetric food verification, shawarma removed, and targeted cuisine associations

Latest analysis requested November3,2026. Download symmetric_food_no_shawarma.zip and extract into the workspace root. Open analysis_clean/symmetric_food_no_shawarma/no_shawarma_report.html.

The report starts with ME and WPME restaurant ratings shown next to each other, before and after, with county types side by side. Raw group means, conditional county-FE gaps, and the difference of those gaps across county types are separate views.

## Main observed ratings

Broad dictionary, food evidence required in BOTH label groups, full eligible equal-restaurant-weight ban sample:

| County type | Group | N | Before | After | Change |
|---|---|---:|---:|---:|---:|
| Trump-majority | ME | 101 | 4.512 | 4.419 | -.093 |
| Trump-majority | WPME | 281 | 4.446 | 4.450 | +.004 |
| Non-Trump | ME | 991 | 4.341 | 4.379 | +.038 |
| Non-Trump | WPME | 1636 | 4.395 | 4.393 | -.002 |

Thus ME's observed mean declines in Trump counties while WPME is nearly flat in this full raw sample. The standalone ME mean-change test has p=.271 and CI spans zero. Do not infer confirmed population decline or causal ban effects from the point estimates alone.

## Direct county-type tests

Each restaurant contributes one unit-weight pre/post rating change. County-FE pairwise models use counties containing both compared groups. Main direct coefficient = (WPME-ME change gap in Trump counties) minus (that gap in non-Trump counties).

| Dictionary | Event | ME eligibility | Direct gap | Raw p |
|---|---|---|---:|---:|
| Core | Election | All ME labels | +.231 | .3764 |
| Core | Election | Food verified | +.035 | .9279 |
| Core | Ban | All ME labels | +.356 | .1646 |
| Core | Ban | Food verified | +.198 | .5090 |
| Broad | Election | All ME labels | +.124 | .3945 |
| Broad | Election | Food verified | +.196 | .1865 |
| Broad | Ban | All ME labels | +.311 | .0106 |
| Broad | Ban | Food verified | +.372 | .0028 |

For broad food-verified ban samples, conditional WPME-ME gap is +.337 (p=.0036;150 WPME/77 ME,35 Trump counties) versus -.035 (p=.438;1481 WPME/969 ME,167 non-Trump counties). The direct p=.0028 tests whether these gaps differ. Companion Holm p across the8 primary direct tests=.0224. Core does not confirm the broad pattern.

The exact unit-weight FE decomposition has implied WPME change +.160 and ME change -.177 in Trump counties. These use shared-county support and the county weights implicit in the FE regression; they are different from the unrestricted raw means above. No regression reweighting is introduced. Both summaries and exact identities are exported.

## Symmetric dictionaries and full raw reviews

Core = original27 core dishes minus shawarma (26). Broad = revised26 core + original10 shared dishes (36); shawarma excluded from both. Same pre-election cutoff and regex rules applied to primary ME and Mediterranean restaurants. All52 raw state-review files were scanned,666,324,103 rows, yielding159,407 unique eligible pre-election reviews after deduplication. The old Mediterranean core counts were exactly reproduced before removing shawarma. Core-positive Mediterranean businesses fall1293->603; ME-label businesses948->603. Broad verifies1496 ME-label and2578 Mediterranean-label businesses. Food evidence is a review-mention proxy, not certified authenticity or menu absence.

ME primary-category rules unchanged. WPME = primary Mediterranean with dictionary evidence; MED = primary Mediterranean, eligible pre-election text and no evidence under that same dictionary. Unknown pre-election histories excluded. All-ME-label and food-verified-ME variants are both retained. No matching or price/format filters.

## Seven-country association and review-cuisine expansion

Category-only baseline uses explicit primary national-cuisine categories: Persian/Iranian, Iraqi, Syrian, Yemenite/Yemeni, Libyan, Somali/Somalian, Sudanese. In the supplied primary-category frame only Persian, Syrian and Yemenite are observed. These are cuisine labels, not owner citizenship or actual policy exposure.

Requested expanded variant = primary category OR explicit PRE-ELECTION review-cuisine phrase. A second raw52-file pass found416 restaurants with positive country-cuisine evidence,1609 unique cue-bearing reviews. Examples include Persian food, Iraqi cuisine and Syrian restaurant. Bare nationality/geographic mentions and immediate negations are excluded. These phrases expand COUNTRY ASSOCIATION ONLY; they do not change food evidence or label groups. Review cues add Iraqi and Somali associations among ME labels. Libyan evidence is observed in a Mediterranean-labeled restaurant that remains in its label group; no Sudanese cue is found. Per-country associations can overlap.

Both country definitions are reported separately. Targeted core shared-county Trump cells can have only3-5 ME restaurants in2-4 counties: pooled CR1 p-values can be highly unstable. Report shows county support and a smaller-county-type-df sensitivity; this changes t df only and does not fix sparse-cluster variance. Direct stronger-targeted comparisons use one joint WPME/targeted-ME/other-ME model. For food-verified ban samples, category-only stronger-targeted interaction p=.018 Core/.022 Broad; after review-cuisine expansion p=.137/.167. That interpretation is definition-sensitive.

## Timing and inference

Election Oct10-Nov6 vs Nov14-Dec11,2016; ban Dec26-Jan22 vs Jan30-Feb26,2017. Four weeks each side, holidays included, mixed event weeks omitted. Trump county share strictly>50% of all-candidate votes. County clustering, CR1 finite-sample corrections, fixest nonnested county-FE adjustment and t df=counties-1. Raw p symbols:+<.10,*<.05,**<.01,***<.001. Companion primary8-test Holm correction and broader exploratory adjustments are separate. All comparisons remain observational; prior pretrend/reviewer-selection concerns remain.

## Reproduction using frozen aggregates

Python numpy/pandas/scipy; R data.table/fixest. From workspace root:
python analysis_clean/prepare_symmetric_no_shawarma.py
Rscript analysis_clean/symmetric_no_shawarma_models.R
python analysis_clean/verify_symmetric_no_shawarma.py
Rscript analysis_clean/symmetric_no_shawarma_models.R --expanded-country
python analysis_clean/verify_symmetric_no_shawarma.py --expanded-country
python analysis_clean/symmetric_group_mean_uncertainty.py
Rscript analysis_clean/plot_symmetric_no_shawarma.R
Rscript analysis_clean/plot_raw_ME_WPME.R
python analysis_clean/report_symmetric_no_shawarma.py

The archive includes frozen review-derived flags/cuisine counts, metadata/outcome inputs, analysis data, code, figures and results. Raw review checkpoints and SQLite dedup stores are omitted, as are model_verification_inputs.csv files regenerated by R. Raw source files are required only to rerun the two scanner scripts, preserved as provenance. No reviewer IDs, review hashes or full review text are redistributed; phrase audit retains matched cuisine phrases only.

Independent within-county/OLS calculations verified96 fitted models,192 pairwise contrasts,96 stronger-targeted contrasts,64 exact FE decompositions and all paired raw-mean uncertainty calculations. Expanded country association is checked to leave food tags and all-ME comparisons unchanged. Source files were not modified. Original analyses and the earlier with-shawarma dictionary remain separate reproducible snapshots.
