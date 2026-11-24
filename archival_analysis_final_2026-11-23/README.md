# Archival analysis — consolidated, November 23, 2026

Hiding Their True Colors (Heshmati, Choe). This folder supersedes the earlier checkpoints (November 18, 19 and 22). All results are exploratory, descriptive evidence meant to sit beside the planned experiment.

Start with [RESULTS.md](RESULTS.md) for the numbers and [METHODS.md](METHODS.md) for every measure and model.

## The three steps

1. **Who positions broadly.** Restaurants serving Middle Eastern food lead with "Mediterranean" more where the local Middle Eastern community is small. County Trump share adds nothing once county size is held fixed.
2. **The explicit label is penalized after stigma events.** After the January 2017 travel ban, ratings of explicitly Middle Eastern restaurants fell in more Trump-leaning counties, relative to other restaurants in the same county, for about six weeks. The 2016 election shows a smaller dip in the same direction. Broadly positioned restaurants show no such pattern across counties, though we cannot say they were spared. (Wording revised November 24, after the reviewer-leniency check.)
3. **Mechanism.** Left to the experiment: animus versus unfamiliarity.

## Definitions

- **WPME (broadly positioned):** first Google category contains "Mediterranean", and at least one review in any year mentions baba ghanoush.
- **ME (explicitly positioned):** first Google category is Middle Eastern or a national label (Lebanese, Persian, Turkish, and so on), with or without a baba mention. The original 20-category list is reported as a check.
- **Trump support:** 2016 Trump votes divided by all presidential votes in the restaurant's county. Main measure: per 10 percentage points. Secondary: share above 50%.

## Headline numbers

| Exhibit | Result |
|---|---|
| 1. Label choice | −5.8 points in the chance of being WPME per percentage point of Middle Eastern ancestry in the county (p < .001) |
| 3. Events | The WPME-minus-ME gap rises +0.043 stars per 10 points of Trump share in the six weeks after the election and the travel ban, pooled (p < .01); zero in weeks 7–18 |
| 3. Which group moves (lead estimate for step 2) | Against American-first restaurants: ME −0.027 per 10 points (p = .02); WPME +0.006 (p = .65). ME by event: −0.019 after the election (p = .17), −0.035 after the travel ban (p = .01); −0.006 in the three later periods (p = .51) |
| 3. Reviewer leniency | Measured against each reviewer's usual rating: ME −0.025 (p = .04); WPME −0.016 (p = .18); WPME minus ME +0.009 (p = .61) |
| 4. Positioning over time | Among restaurants first reviewed within two years of the election, 47% are WPME before it and 48% after (+2 points, p = .48); no differential shift in Trump-leaning counties |

Exhibit 2 (ordinary-times rating and review-volume levels) is kept as a background table. The paper makes no claim about which position performs better in ordinary times.

## What to keep in mind

- The contrast between WPME and ME is not robust to who is reviewing. WPME restaurants in more Trump-leaning counties drew somewhat more lenient reviewers after the events; against each reviewer's usual rating the WPME-minus-ME difference is +0.009 (p = .61). The ME decline itself is unchanged. At 40% Trump share both groups are below American-first restaurants after the events (WPME −0.046, p = .01; ME −0.038, p = .07).
- For ME on its own, the travel ban carries the result; the election alone is not significant.
- The event result holds with continuous Trump share and not with the over-50% split (+0.092 pooled, p = .17).
- Six events were tested. The focus on the election and the first travel ban was chosen after seeing all six; the other four and the six-event pooled estimate (+0.019, p = .02) are in RESULTS.md.
- WPME requires a baba mention and ME does not. Against ME restaurants that also have one, the ordinary-times rating gap is zero. The event models use restaurant fixed effects and are not affected by this.
- Google categories are from 2021, not what customers saw at the time of each review, so a restaurant changing its label cannot be seen. Exhibit 4 uses the date of each restaurant's first review as a stand-in for when it opened. Owner identity is not observed.

## Run it

Python 3.12 with numpy, pandas, scipy, matplotlib. R with `sf` only for the from-raw build.

```
python run_all.py
```

rebuilds the exhibits, figures and RESULTS.md from the tables in `frozen/`. No raw data needed.

```
python run_all.py --from-raw <project root> --rscript <path to Rscript> --workers 20
```

also rebuilds the sample, county assignment, review extract and frozen tables from the raw Google files in the project Dropbox. The raw scan reads 666 million reviews and takes about five minutes on 20 workers.

## Files

| File | What it does |
|---|---|
| `common.py` | Definitions, event dates, Trump share, Census controls, estimator |
| `01_build_sample.py` | Sample: Mediterranean-first, ME-first and American-first restaurants |
| `02_geocode_counties.R` | County for each restaurant; county land area |
| `03_extract_reviews.py` | Every review of the sample with its exact timestamp |
| `04_build_frozen.py` | Analysis-ready tables in `frozen/` |
| `05_label_choice.py` | Exhibit 1 |
| `06_levels.py` | Exhibit 2 (background) |
| `07_events.py` | Exhibit 3 |
| `08_figures.py` | Figures 1–3 |
| `10_positioning_over_time.py` | Exhibit 4 and figure 4 |
| `11_story_figures.py` | Figure 5 (each group's change by county Trump share) and figure 6 (the gap over time) |
| `12_scan_text_and_reviewers.py` | Raw pass for review text and reviewer activity around the two events (output stays in `built/`) |
| `13_star_breakdown.py` | Which star ratings move after the events |
| `14_labels_and_pairs.py` | First categories of restaurants serving baba ghanoush; example WPME and ME pairs in the same county |
| `15_map.R` | County map of the WPME share |
| `16_text_and_reviewers.py` | Political mentions in review text; results by reviewer activity |
| `17_identity_lens.py` | Identity references in review text, by star rating and by group |
| `18_scan_reviewer_leniency.py` | Raw pass for each reviewer's rating history (output stays in `built/`) |
| `19_star_breakdown_leniency.py` | The star breakdown with reviewer-leniency adjustments |
| `21_each_group_over_time.py` | Figure 7: ME and WPME over time, each relative to American-first restaurants |
| `20_results_summary_html.py` | Writes RESULTS_SUMMARY.html, the working summary with figures and include/leave-out recommendations (local; it quotes three reviews) |
| `09_results_summary.py` | Writes RESULTS.md from the output tables |
| `inputs/` | MIT Election Lab county returns (2016); ACS 2017–2021 county tables; county land area |
| `frozen/` | `restaurants.csv`, `event_cells.csv.gz`, `timeline_cells.csv.gz`. No names, addresses, reviewer IDs or review text |
| `outputs/` | Exhibit tables and figures |

The raw Google files and the 154 MB review extract (`built/`) are not in the repository. The frozen tables are derived from Google Local data; this repository grants no rights to the underlying data.
