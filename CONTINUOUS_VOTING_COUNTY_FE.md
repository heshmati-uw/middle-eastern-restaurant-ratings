# Continuous voting associations with county fixed effects

The current specification uses actual 2016 Trump vote shares, not a Trump-majority split, for ME/WPME/review-screened Mediterranean. Full eligible samples, equal restaurant weights, four-week windows, holidays included, no matching or price restrictions. Conditional associations, not causal event effects.

Extract continuous_voting_county_fe.zip into the workspace root. Open analysis_clean/full_pre_election_core/correlational_full_sample/continuous_county_fe/county_fe_report.html. Unadjusted continuous results and plots are at the adjacent continuous_vote_share/continuous_report.html. Restored original dictionary plots are at analysis_clean/county_fe_regressions/dictionary_plot_gallery.html.

## Current county-FE findings

Coefficients below are cuisine slope differences in rating stars per 10 percentage points higher Trump vote share. Raw two-sided county-clustered p in parentheses.

| Event | Share geography | ME-WPME | ME-MED | WPME-MED |
|---|---|---:|---:|---:|
| Election | County | -.011 (.743) | +.017 (.566) | +.028 (.489) |
| Election | Precinct | +.001 (.978) | -.022 (.369) | -.023 (.403) |
| Ban | County | -.010 (.805) | -.011 (.704) | -.001 (.970) |
| Ban | Precinct | +.005 (.859) | +.032 (.180) | +.028 (.312) |

None is significant at .10. Joint equality-of-cuisine-slope tests do not reject either. N unchanged: county election3300/ban3687; precinct election3292/ban3678. All three contrasts use the same model/sample within event and geography.

## What county FE can identify

County vote share is constant inside a county. Its common main effect is absorbed; only cuisine differences in voting slopes can be estimated. ME/MED and WPME/MED interactions are reported, with ME/WPME as their difference. Setting the MED common county slope to zero is a parameterization, not a substantive zero result. Mixed-cuisine counties supply identifying variation; single-cuisine counties remain in the data but do not identify those county-share interactions.

Precinct vote share varies within counties, permitting the common precinct slope and each cuisine-specific slope in a county-FE model. Both geographic models report the same cuisine slope contrasts. Main plots show ME and WPME relative rating-change gaps against one shared Mediterranean reference, with pointwise 95% county-clustered bands over each pair's overlapping central90% vote range. All observed restaurants enter fits.

Each restaurant's rating change has unit regression weight. County-clustered CR1 uses fixest nonnested FE corrections and t df G-1. Current models omit matching, price, format and demographic controls. Precinct analyses also cluster by county. Within-county FE adjust county-wide changes, not every unobserved cuisine-specific local shock. Prior pretrend concerns remain.

## Historical figures restored

The screenshot's five-dictionary forest plots were regenerated using their original saved results and independently rechecked against original inputs (240 pairwise/sample-specification models). Their split Trump/non-Trump panels and older broad/core classifications are deliberately preserved. They compare group rating-change gaps within county strata, not continuous share gradients. Grey dictionary definitions can use post-event information; blue/red pre-election definitions predate the newer full raw scan. No old dictionary is silently substituted for the current full-core labels.

## Reproduction

Requires Python numpy/pandas/scipy and R data.table/fixest/jsonlite.

python analysis_clean/continuous_correlational.py
Rscript analysis_clean/plot_continuous_correlational.R
Rscript analysis_clean/continuous_county_fe.R
python analysis_clean/report_continuous_county_fe.py

Original forest figures: Rscript analysis_clean/plot_dictionary_focus.R county_fe
Original pairwise checks: python analysis_clean/verify_county_fe.py

The archive includes the frozen current restaurant-change input, unadjusted R result tables used for cross-checking, current code/results/plots, and original county-FE results/inputs/plotting code. Current R run regenerates its omitted model_verification_inputs.csv. Independent NumPy within-county checks reproduce all4 FE models,12 cuisine slope contrasts,6 precinct group slopes,1452 plotted predictions and4 joint tests. Maximum numerical discrepancy is about3e-14. Current unadjusted Python fits also agree with independently verified full-sample R fits. No reviewer text or reviewer IDs are redistributed.

Election windows Oct10-Nov6 vs Nov14-Dec11,2016. Ban Dec26-Jan22 vs Jan30-Feb26,2017. Labels frozen from the full raw pre-election core review scan: primary-ME categories; primary Mediterranean plus core evidence for WPME; eligible pre-election text and no core evidence for MED (shared dishes allowed). Absence of a core mention is not verified menu absence. Voting describes locations, not reviewer ideology.
