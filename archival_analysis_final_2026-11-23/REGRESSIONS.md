# Regression details and verification

Hiding Their True Colors (Heshmati, Choe). Written November 24, 2026. This file states each regression behind the publication figures, what was checked, and one result of the check that affects how the lead finding should be described.

## Notation and conventions

- **ME**: first Google category is Middle Eastern or a national label (Lebanese, Persian, Turkish and so on). **WPME**: first category contains "Mediterranean" and at least one review mentions baba ghanoush. **American**: American-first restaurants, used as the reference group.
- **Z**: county 2016 Trump vote share, centered at 40% and scaled so one unit is 10 percentage points: Z = (share − 0.40) / 0.10.
- **Period**: 42 days. Pre-period: the five periods (210 days) before November 8, 2016. After the election: November 8 to December 19, 2016. After the travel ban: January 27 to March 9, 2017. Dates are UTC, from exact review timestamps.
- **Unit**: restaurant × period. The outcome is the mean star rating of the restaurant's reviews dated in that period. Restaurant-periods with no reviews are absent. **Each restaurant-period has equal weight**, whatever its number of reviews (median 3; 24% have one review).
- **Standard errors**: clustered by county; the sandwich estimator is multiplied by G/(G − 1), and p-values use the t distribution with G − 1 degrees of freedom.

## Model 1. Label choice (Figure 1B)

WPME_i = α_state + β·Z_c + γ′X_c + ε_i

- Sample: 3,895 WPME and ME restaurants in 455 counties; 44.6% are WPME. Linear probability model, state fixed effects.
- X_c added in steps: log population and log density; percent of residents of Middle Eastern ancestry; percent college graduates and percent foreign-born (ACS 2017–2021).

| Controls | Trump share, per 10 pts | Middle Eastern ancestry, per 1 pt |
|---|---|---|
| State fixed effects only | +0.026 (0.009), p < .01 | |
| + population, density | −0.007 (0.011), p = .54 | |
| + Middle Eastern ancestry | −0.005 (0.010), p = .66 | −0.061 (0.011), p < .001 |
| + college, foreign-born | −0.008 (0.010), p = .44 | −0.058 (0.011), p < .001 |

Figure 1B plots raw shares by ancestry group with county-clustered intervals.

## Model 2. Which group moves (Figure 3; the lead result)

rating_it = α_i + λ_ct + Σ_g Σ_e [ β_ge·G_g,i·After_e,t + δ_ge·G_g,i·After_e,t·Z_c ] + ε_it

- g ∈ {ME, WPME}; e ∈ {election, travel ban}; α_i restaurant fixed effects; λ_ct county-by-period fixed effects.
- American restaurants in the same county and period identify λ_ct, so every coefficient is relative to them. County-level shocks in a period, including anything that moves all restaurants' ratings in Trump-leaning counties, are absorbed.
- δ_ge is the change in the group's rating after event e per 10 points of Trump share. β_ge is the change at 40% Trump share.
- Sample: 170,379 restaurant-periods; 1,568 ME, 1,245 WPME and 29,789 American restaurants; 2,672 counties.

| Coefficient (δ, per 10 pts) | After the travel ban | After the election | Average of the two |
|---|---|---|---|
| ME | −0.035 (0.014), p = .01 | −0.019 (0.014), p = .17 | −0.027 (0.012), p = .02 |
| WPME | −0.008 (0.015), p = .61 | +0.019 (0.017), p = .25 | +0.006 (0.013), p = .65 |

The lines in Figure 3 are β_ge + δ_ge·Z over the range of Trump share, with pointwise 95% intervals.

## Model 3. Each group over time (Figure 4)

rating_it = α_i + λ_ct + Σ_g Σ_{p≠4} [ β_gp·G_g,i·1(t = p) + δ_gp·G_g,i·1(t = p)·Z_c ] + ε_it

- Eleven consecutive periods, April 12, 2016 to July 13, 2017; period 4 (the last before the election) is omitted. The plotted value for period p is δ_gp minus the average of δ over the five pre-election periods.
- Sample: 285,105 restaurant-periods; 1,652 ME, 1,304 WPME and 31,655 American restaurants.
- ME: −0.017 (p = .22) after the election, +0.010 between the events, −0.037 (p < .01) after the travel ban, −0.006 (p = .51) on average over the three later periods. Joint test of the pre-election periods: p = .28 for ME, p = .06 for WPME.

## Model 4. Star shares (Figure 5)

Model 2 with the outcome replaced by the share of the restaurant's reviews in the period at a given star level; one regression per star level. For ME, one-star reviews rise by 0.66 points per 10 points of Trump share after the travel ban (p = .02) and 0.82 after the election (p = .01). WPME: +0.09 and −0.12 (p = .78, .79).

## Model 5. Reviewer leniency

Model 2 with each review's rating replaced by rating minus that reviewer's average rating on every other review they wrote in the data (any business, any year), then averaged to the restaurant-period. Reviews by people with no other reviews (6%) are dropped. 166,026 restaurant-periods. ME after the travel ban: −0.037 (0.014), p < .01. WPME after the travel ban: −0.026 (0.015), p = .09.

## Model 6. The WPME-minus-ME gap (comparison, not the lead result)

rating_it = α_i + λ_ct + β·WPME_i·After_t + δ·WPME_i·After_t·Z_c + ε_it, on WPME and ME restaurants only, one event at a time (five pre-periods and the first post-period), and stacked over the two events with event-specific fixed effects.

| | δ, per 10 pts | Observations |
|---|---|---|
| 2016 election | +0.048 (0.023), p = .03 | 13,683 |
| Travel ban | +0.038 (0.018), p = .03 | 14,639 |
| Pooled | +0.043 (0.015), p < .01 | 28,322 |

## What was checked

1. **Independent re-estimation.** The Python scripts use their own estimator. `25_verify_with_fixest.R` rebuilds each model's data from the frozen tables with separate code and estimates it with `fixest::feols`. All 22 coefficients compared (Models 1 to 6) agree to 14 decimal places, and every standard error ratio is 1.0000. See `outputs/verification_report.csv`.
2. **Data.** No duplicate restaurants or restaurant-periods; no restaurant in two groups; all cell means lie between 1 and 5. Two cell files built by separate scripts agree exactly on 170,379 cells. The after-travel-ban cells were recomputed directly from the review extract (193,282 reviews, January 27 to March 9, 2017) and match exactly.
3. **Alternative specifications of the lead estimate** (ME × after travel ban × Z; Figure A1):

| Specification | Estimate | p |
|---|---|---|
| As reported | −0.035 (0.014) | .01 |
| Original 20-category list of explicit labels | −0.037 (0.015) | .01 |
| Standard errors clustered by state | −0.035 (0.013) | < .01 |
| State-by-period instead of county-by-period fixed effects | −0.034 (0.013) | < .01 |
| Restaurant and period fixed effects only | −0.036 (0.012) | < .01 |
| Rating relative to each reviewer's usual | −0.037 (0.014) | < .01 |
| Restaurant-periods with 3 or more reviews | −0.006 (0.012) | .59 |
| Weighted by number of reviews | −0.013 (0.009) | .18 |

## The one result that needs a decision: weighting

The lead estimate is stable to everything except how restaurant-periods are weighted. With each restaurant-period weighted equally it is −0.035 (p = .01). Weighted by the number of reviews it is −0.013 (p = .18), and among restaurant-periods with three or more reviews it is −0.006 (p = .59).

The two weightings answer different questions. Equal weights estimate the change for the average restaurant; review weights estimate the change for the average review. The difference means the decline is concentrated in restaurants with few reviews:

| ME restaurants by reviews in the 210 pre-election days | ME × after travel ban × Z | p |
|---|---|---|
| 8 or fewer (552 restaurants) | −0.065 | .06 |
| 9 to 18 (540) | −0.044 | .04 |
| More than 18 (476) | −0.012 | .51 |

Other estimates under review weights: ME one-star share after the travel ban +0.32 points (p = .09) and after the election +0.38 (p = .10); the pooled WPME-minus-ME gap +0.030 (p = .01), which stays significant.

Two readings are possible. Low-volume restaurants may be more exposed, since each review moves their rating more and they have fewer regulars. Or the equal-weight estimate may lean on noisy cells with one or two reviews. The monotone pattern across the three size groups favors the first reading, but each group is imprecise.

What this means for the paper: the unit and weighting must be stated wherever the result is reported, the review-weighted estimate belongs in the robustness table, and the claim should be about the average restaurant, with the concentration among smaller restaurants reported as a finding.

## Files

| File | Role |
|---|---|
| `30_publication_figures.py`, `31_publication_map.R` | Publication figures in `outputs/publication/` (PDF and 600 dpi PNG) and `FIGURE_CAPTIONS.md` |
| `25_verify_with_fixest.R` | Independent re-estimation and alternative specifications |
| `26_verification_report.py` | Python-versus-fixest comparison and data checks |
| `outputs/verification_report.csv`, `verification_fixest.csv`, `verification_robustness.csv` | Results of the checks |
