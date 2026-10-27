# ME versus WPME only: average changes versus precinct gradients

Extract [ME_WPME_focus.zip](ME_WPME_focus.zip) and open analysis_clean/full_pre_election_core/ME_WPME_focus/focus_report.html. Includes inputs, code, results and independent NumPy verification of 32 models.

The prior precinct regressions already used only these two groups, but tested how their relative changes vary with precinct Trump share. This focused analysis also directly compares their average before/after changes, without the continuous-share interaction. Full raw pre-election core tags, four-week windows, equal restaurant weights, same common-county and precinct-eligible samples, county FE and county-clustered inference. Negative estimates indicate ME losing ground relative to WPME.

| Event | County stratum | County-FE ME-WPME difference in changes | Raw p | N ME / WPME |
|---|---|---:|---:|---:|
| Election | Trump | -.223 | .1789 | 59 / 55 |
| Election | Non-Trump | +.018 | .7381 | 998 / 744 |
| Ban | Trump | -.433 | .0191 | 72 / 62 |
| Ban | Non-Trump | +.070 | .2095 | 1,114 / 838 |

Ban Trump raw means: ME 4.501 -> 4.358 (-.144), WPME 4.319 -> 4.542 (+.223); raw difference in changes -.367 (p=.0142). County-FE estimate -.433, baseline-adjusted -.231 (p=.0175). The direct Trump-minus-non-Trump county-FE difference is -.503 (p=.0049).

Causal limits: pre-ban mean-change placebo in Trump counties is +.305 (p=.0757) on the 117-restaurant history-observed subset. This creates a parallel-trends/mean-reversion concern. Main ban-Trump p=.0191 becomes .0763 with Holm across four split-county event tests, or .1144 including pooled events. The project includes further exploratory tests. These are associations, not established causal effects.
