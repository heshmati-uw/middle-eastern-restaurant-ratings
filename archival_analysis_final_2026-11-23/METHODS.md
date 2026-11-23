# Measures and empirical specification

Hiding Their True Colors (Heshmati, Choe, Frake). Written 2026-11-23. Describes exactly what the scripts in this folder do. All results are exploratory.

## 1. Data sources

| Source | File | Used for |
|---|---|---|
| Google Local reviews, raw | `analysis/2025-08-18-rohan/inputs/review-<State>.json.gz` (52 files, 666,324,103 reviews) | Review-level ratings with exact timestamps |
| Restaurant frame | `analysis/2025-08-18-rohan/categorized output/all-states.csv` (34,636 businesses) | Categories, coordinates, food-mention flags |
| Business metadata | `data/Google Reviews/Meta_data_combined.csv` | American-first benchmark restaurants |
| 2016 county presidential returns | MIT Election Data and Science Lab, version 20190722 (`inputs/medsl-countypres-2000-2016.csv`) | County Trump share |
| County boundaries | Census 2018 cartographic boundary file, 1:500k | Assigning restaurants to counties |
| County demographics | ACS 2017–2021 five-year tables B01003, B04006, B15003, B05002 (www2.census.gov) | Population, ancestry, education, nativity |

The restaurant frame was built in September 2025. It contains every business with at least one Google review, in any year through 2021, that mentions hummus or baba ghanoush.

## 2. Restaurant groups

All group definitions use Google's category list for the business as of the 2021 data snapshot. The "first category" is the first entry in that list.

**WPME (broadly positioned).** First category contains "mediterranean" (case-insensitive), and at least one review in any year mentions baba ghanoush.
- The baba flag is `review_baba` in the frame. It is 1 if any review matches a list of spellings: baba ghanoush, baba ganoush, baba ghanouj, baba ghannouj, babaganoush and about twenty further variants (`BABA_PATTERN` in `review_analysis_toshare.py`).

**ME (explicitly positioned).** First category matches the national list, with or without a baba mention.
- National list (primary): first category contains any of: middle eastern, lebanese, persian, iranian, syrian, iraqi, turkish, yemeni, yemenite, palestinian, jordanian, egyptian, moroccan, north african, kuwaiti, qatari, bahraini, omani, saudi, armenian, afghan, afghani. Israeli is excluded.
- Original list (robustness): first category is exactly one of 20 names: Middle Eastern, North African, Armenian, Halal, Egyptian, Moroccan, Persian, Lebanese, Syrian, Afghani, Yemenite, Iraqi, Palestinian, Jordanian, Kuwaiti, Qatari, Bahraini, Omani restaurant; Kebab shop; Shawarma restaurant.

**Not in either group.** Mediterranean-first restaurants without a baba mention, and restaurants whose first category is anything else.

**American benchmark** (used only where stated). First category is exactly "American restaurant".

Counts with a county and Trump share: 1,736 WPME and 2,159 ME (national list).

One consequence of these definitions: WPME must have a baba mention and ME need not. Restaurants with a baba mention have more reviews and higher ratings in both groups, so level comparisons favor WPME for that reason. The event analysis in section 6 uses restaurant fixed effects and is not affected by level differences.

## 3. Geography and Trump support

- **County.** Each restaurant's latitude and longitude is placed in a 2018 Census county polygon (`02_geocode_counties.R`, `sf::st_join`).
- **Trump share.** 2016 votes for Donald Trump divided by the sum of votes for all candidates in the county. Kansas City, MO is reported separately in the source and is folded into Jackson County. Alaska has no county-level returns, so its 115 restaurants drop.
- **Continuous measure (main).** Z = (share − 0.40) / 0.10, so coefficients are per 10 percentage points.
- **Majority measure (secondary).** 1 if share > 0.50.
- Over 60% and over 70% were examined and are too thin (120 and 27 restaurants).

## 4. Review data

`03_extract_reviews.py` reads every line of the 52 raw state files and keeps reviews of sample restaurants.
- Kept fields: restaurant ID, timestamp in milliseconds (UTC), star rating.
- Dropped: ratings other than 1–5; exact duplicates (same restaurant, reviewer, timestamp, rating).
- No reviewer names, IDs or text are saved.
- Result: 20,502,231 reviews for the full sample; 2,352,548 for Mediterranean-first and ME-first restaurants.

## 5. Outcome

Star rating, 1 to 5. For the event analysis the unit is a restaurant in a 42-day period, and the outcome is the simple mean of all its reviews dated in that period. A restaurant with no reviews in a period has no observation for it.

## 6. Event specification (main analysis)

For an event on date E (start of day, UTC):

- **Periods.** b = floor((review time − E) / 42 days). Periods −5 to −1 are the 210 days before E. Period 0 is the 42 days starting on E.
- **Sample.** WPME and ME restaurants with a county and Trump share, observed in at least one period.
- **Model.**

  rating(i, b) = a(i) + g(c, b) + β · WPME(i) · Post(b) + δ · WPME(i) · Post(b) · Z(c) + e(i, b)

  - a(i): restaurant fixed effect.
  - g(c, b): county-by-period fixed effect. It absorbs anything that moves all restaurants in a county in a period, including the direct effect of Trump share after the event.
  - Post(b) = 1 for period 0.
  - Z(c): county Trump measure from section 3.
  - **δ is the reported estimate**: the change in the WPME-minus-ME rating gap, after versus before, per 10 points of county Trump share.
- **Weights.** Each restaurant-period counts equally.
- **Estimation.** Fixed effects are removed by alternating projections, then OLS (`Fit` in `common.py`, called from `07_events.py`).
- **Standard errors.** Clustered by county, scaled by G/(G−1). p-values use a t distribution with G−1 degrees of freedom.
- **What identifies δ.** Counties that have both a WPME and an ME restaurant reviewed in the period.
- **Persistence.** Same model with Post = 1 for periods 1 and 2 (days 43–126) and period 0 left out.
- **Pre-period test.** Within periods −5 to −1, WPME × period × Z for periods −5, −4, −2, −1 (period −3 omitted); joint F test.

**Two events together.**
- *Pooled.* The two event datasets are stacked. Fixed effects become restaurant-by-event and county-by-period-by-event. One β and one δ.
- *Shared baseline.* One timeline. Before = the 210 days before Nov 8, 2016. After-election = Nov 8 – Dec 19, 2016. After-ban = Jan 27 – Mar 9, 2017. Dec 20 – Jan 26 is left out. Separate δ for each event, and their average. This keeps the election out of the ban's comparison period.

**Ordinary-date comparison.** The same model is run for a date every 42 days from June 6, 2016 to January 6, 2020. Dates whose after-period overlaps the 42 days following any of the six tested events are dropped, leaving 22.

## 7. Event results

Events in focus: the 2016 election (Nov 8, 2016) and the first travel ban (Jan 27, 2017). National ME list, continuous Trump share.

| | δ, first 6 weeks | SE | p | Restaurants | Counties | Reviews in after-period |
|---|---|---|---|---|---|---|
| 2016 election | +0.048 | 0.023 | .03 | 2,730 | 398 | 14,275 |
| Travel ban | +0.038 | 0.018 | .03 | 2,807 | 404 | 18,172 |
| Both, pooled | +0.043 | 0.015 | < .01 | 2,820 | | 32,447 |
| Both, shared baseline: election | +0.049 | 0.022 | .03 | 2,813 | | |
| Both, shared baseline: ban | +0.046 | 0.021 | .03 | | | |
| Both, shared baseline: average | +0.048 | 0.018 | < .01 | | | |

- Days 43–126: 0.000 pooled (p = .98).
- Majority measure (share > 50%): +0.092 pooled (p = .17); +0.108 with the shared baseline (p = .16).
- Original ME list: +0.043 pooled (p < .01).
- Pre-period test: p = .30 for the election; p = .05 for the ban, whose pre-period contains the election.
- Ordinary dates: mean −0.002, SD 0.014, range −0.024 to +0.026, none significant.
- Size: moving from a county at 30% Trump share to one at 60% shifts the gap by about 0.13 stars for six weeks.

**Which group moves** (`07_events.py`, part D). American-first restaurants in the same county and period are added as a third group, on the shared-baseline timeline: rating = restaurant FE + county-by-period FE + {ME, WPME} × {after-election, after-ban} × {1, Z}. Coefficients are relative to American-first restaurants. 1,245 WPME, 1,568 ME and 29,789 American restaurants; 802,858 reviews.

| Per 10 points of Trump share, relative to American-first | After election | After ban | Average | p (average) |
|---|---|---|---|---|
| ME | −0.019 | −0.035 | −0.027 | .02 |
| WPME | +0.020 | −0.008 | +0.006 | .65 |
| WPME minus ME | | | +0.033 | .02 |

At 60% Trump share the average change is −0.093 stars for ME (p = .02) and −0.034 for WPME (p = .33).

**Gap levels by window** (restaurant mean rating in the window; county fixed effects; WPME and WPME × Z).

| Window | Gap where share ≤ 50% | Gap where share > 50% | Gap at 60% (fitted) | Slope per 10 pts |
|---|---|---|---|---|
| 210 days before the election | +0.067 (p < .01) | −0.015 (p = .83) | +0.009 (p = .84) | −0.019 (p = .17) |
| 6 weeks after the election | +0.011 (p = .71) | 0.000 (p = 1.00) | +0.097 (p = .11) | +0.032 (p = .07) |
| 6 weeks after the ban | +0.052 (p = .08) | +0.033 (p = .70) | +0.086 (p = .14) | +0.013 (p = .49) |

Four other events were tested with the same model and are not in focus: travel ban 2.0, Mar 6, 2017 (+0.007, p = .66); travel ban 3.0, Sep 24, 2017 (+0.026, p = .16); Supreme Court ruling, Jun 26, 2018 (0.000, p = .99); Soleimani strike, Jan 3, 2020 (+0.006, p = .67). All six pooled: +0.019 (p = .02). The focus on two events was chosen after these results were seen.

## 8. Level specifications (supporting analyses)

**Ratings and review volume** (`06_levels.py`; background table, no claim is made from it). One row per restaurant.
- Rating: mean of all the restaurant's reviews, all years; restaurants with 10 or more reviews.
- Volume: log of total reviews.
- Model: outcome(i) = county fixed effect + β · WPME(i) + δ · WPME(i) · Z(c) + e(i). The volume model adds fixed effects for the year of the restaurant's first review.
- Standard errors clustered by county, scaled by G/(G−1) · (N−1)/(N−K−G).
- Results: β = +0.026 stars without the interaction (p < .01); δ = −0.014 per 10 points (p = .03). Against ME restaurants that also have a baba mention, β = +0.001 (p = .96).

**Label choice** (`05_label_choice.py`). One row per restaurant.
- Outcome: 1 if WPME, 0 if ME.
- Model: linear probability, state fixed effects, county Trump share, county controls.
- Controls: log population; log population per square kilometer; Middle Eastern ancestry share (Arab, Iranian, Turkish, Afghan, Armenian, Assyrian/Chaldean/Syriac as a percent of residents, table B04006); percent of adults 25+ with a bachelor's degree or more; percent foreign-born.
- Results: −5.8 points per percentage point of Middle Eastern ancestry (p < .001); −0.8 points per 10 points of Trump share (p = .44).

## 8b. Positioning over time (Exhibit 4)

`10_positioning_over_time.py`. One row per WPME or ME restaurant.
- Google categories are a 2021 snapshot, so a restaurant changing its label cannot be observed. The date of each restaurant's first review is used as a stand-in for when it opened. Google reviews were sparse before 2016, so many restaurants first reviewed in 2016-17 are older than that.
- Outcome: 1 if WPME, 0 if ME. After = first review on or after November 8, 2016.
- Samples: restaurants first reviewed within two years of the election (main) or within one year.
- Models: linear probability. Overall shift: After with county fixed effects. Differential shift: After x Trump measure with county and first-review-year fixed effects. County-clustered standard errors.
- Checks: controlling for log review count, and requiring a baba mention on both sides, because newer restaurants have fewer reviews and are less likely to have any given dish mentioned.
- Results: 47% WPME before and 48% after (+2.1 points, p = .48); After x Trump share -2.1 points per 10 points (p = .32).

## 9. Known limitations

- Categories are from 2021, not what customers saw at the time of each review.
- The frame includes only businesses with a hummus or baba mention in some review.
- Owner identity is not observed.
- Review timestamps are UTC; the travel ban was signed on the afternoon of Jan 27 Eastern time, so period 0 includes some hours before it.
- The event effect is significant with continuous Trump share and not with the majority split.
- Many specifications and six events were examined before these two were chosen.

## 10. Scripts

| Step | Script |
|---|---|
| Sample and benchmark | `01_build_sample.py` |
| Counties and land area | `02_geocode_counties.R` |
| Exact-date reviews | `03_extract_reviews.py` |
| Analysis-ready tables | `04_build_frozen.py` |
| Label choice (Exhibit 1) | `05_label_choice.py` |
| Levels (Exhibit 2) | `06_levels.py` |
| Events (Exhibit 3) | `07_events.py` |
| Positioning over time (Exhibit 4) | `10_positioning_over_time.py` |
| Figures | `08_figures.py` |
| Results summary | `09_results_summary.py` |
