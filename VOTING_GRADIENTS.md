# Continuous county and precinct Trump support

Download [voting_gradients.zip](voting_gradients.zip), extract, and open:
- analysis_clean/county_continuous/county_continuous_report.html
- analysis_clean/precinct_analysis/precinct_report.html

All estimates below are ME-minus-WPME rating-change gradients per +10 percentage points of Trump vote share. Negative values support ME losing more ground in more pro-Trump places. Four-week windows; frozen broad pre-election dish dictionary; equal restaurant weights; county-clustered standard errors.

## Continuous county share, full county sample
| Shock | Gradient | SE | Raw p | Restaurants | Counties |
|---|---:|---:|---:|---:|---:|
| Election | -0.0085 | 0.0286 | .7667 | 2,229 | 181 |
| Ban | -0.0071 | 0.0318 | .8238 | 2,478 | 200 |

Baseline adjustment also yields near-zero gradients. These estimates do not establish a causal effect or an absence of heterogeneity.

## Continuous precinct share
Pooled election gradient -0.0106 (p=.5983; N=2,223); pooled ban +0.0249 (p=.2729; N=2,473). Within non-Trump counties, basic ban gradient +0.0526 (p=.0342) points opposite ME losing more ground, and is not robust to stricter controls (county gradient p=.1037; county-by-group FE p=.3550; baseline adjustment p=.2211); Holm across six main results p=.2054.

Precinct geometry/votes come from SAGE (https://github.com/noahdasanaike/sage), documenting VEST and other upstream sources. The report explains point-in-polygon matching, coverage, vote denominator, source limitations and placebo checks. Raw national geometry stays local. The compact archive includes linked data, complete reproducible regression inputs, code, plots and independent verification of all 44 models.
