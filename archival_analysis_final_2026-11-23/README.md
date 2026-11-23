# Archival analysis — consolidated, November 23, 2026

Hiding Their True Colors (Heshmati, Choe, Frake). This folder supersedes the earlier checkpoints (November 18, 19 and 22). All results are exploratory, descriptive evidence meant to sit beside the planned experiment.

Start with [RESULTS.md](RESULTS.md) for the numbers and [METHODS.md](METHODS.md) for every measure and model.

## The three steps

1. **Who positions broadly.** Restaurants serving Middle Eastern food lead with "Mediterranean" more where the local Middle Eastern community is small. County Trump share adds nothing once county size is held fixed.
2. **Broad positioning shields ratings after stigma events.** After the 2016 election and the January 2017 travel ban, ratings of explicitly Middle Eastern restaurants fell relative to other restaurants in more Trump-leaning counties, while broadly positioned ones did not, for about six weeks.
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
| 3. Which group moves | Against American-first restaurants: ME −0.027 per 10 points (p = .02); WPME +0.006 (p = .65) |
| 4. Positioning over time | Among restaurants first reviewed within two years of the election, 47% are WPME before it and 48% after (+2 points, p = .48); no differential shift in Trump-leaning counties |

Exhibit 2 (ordinary-times rating and review-volume levels) is kept as a background table. The paper makes no claim about which position performs better in ordinary times.

## What to keep in mind

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
| `09_results_summary.py` | Writes RESULTS.md from the output tables |
| `inputs/` | MIT Election Lab county returns (2016); ACS 2017–2021 county tables; county land area |
| `frozen/` | `restaurants.csv`, `event_cells.csv.gz`, `timeline_cells.csv.gz`. No names, addresses, reviewer IDs or review text |
| `outputs/` | Exhibit tables and figures |

The raw Google files and the 154 MB review extract (`built/`) are not in the repository. The frozen tables are derived from Google Local data; this repository grants no rights to the underlying data.
