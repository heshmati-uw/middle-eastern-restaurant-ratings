# Election and ban trends: all three pairs, holiday/window sensitivities

Extract [event_holiday_trends.zip](event_holiday_trends.zip) and open analysis_clean/full_pre_election_core/event_holiday_trends/event_holiday_report.html. Contains all data/code/results, PNG/SVG figures, and independent NumPy verification of 333 mean models plus 72 weekly models.

Core tags and full pre-election review labels unchanged; MED is observed text with no core hit, shared mentions allowed. All rows use unit restaurant weights; weekly regressions give each restaurant total observed-panel weight one. Restaurant and county-by-week FE; county-clustered inference.

## Main plotted joint pre-trend p-values
| Comparison | Election Trump | Election non-Trump | Ban Trump, holidays excluded | Ban non-Trump, holidays excluded |
|---|---:|---:|---:|---:|
| ME-WPME | .0000085 | .8385 | .2245 | .1539 |
| ME-MED | .0870 | .5595 | .8381 | .6322 |
| WPME-MED | .0044 | .1510 | .1788 | .7050 |

Holiday exclusion removes the Dec 19 and Dec 26 weeks (Christmas Dec 25 and New Year Jan 1). A wider sensitivity removes Jan 2-8 as well. The mixed Jan 23 ban week stays omitted. Election windows end before Christmas and are unchanged by these exclusions. Thanksgiving is retained.

## Average ME-WPME ban comparison, Trump counties
Original full sample -.4334 (raw p=.0191; 72/62 restaurants). On the holiday-retained sample original ratings give -.4509 (p=.0143), versus -.3607 (p=.0441) after removing holiday ratings (66/57, 22 counties). Baseline adjustment gives -.2180 (p=.0315). Holm across six calendar-excluded split-county comparisons gives .2649 for the raw .0441. The fixed-cohort means still show a WPME pre-ban dip; no rejected test does not establish parallel trends.

Matched shorter ban windows: two-week -.4427 (p=.0961), three-week -.3653 (p=.0674). All three pairs and both events are reported, including original ratings on retained samples. These are exploratory sensitivities, not a window selected by a passing pretest. The shorter-window pretests have smaller samples and fewer restrictions.

Trump took office January 20, 2017 (https://www.govinfo.gov/app/details/DCPD-201700058); the ban order is dated January 27 (https://www.govinfo.gov/app/details/DCPD-201700076). January 9 is earlier; the screenshot discussed restaurant counts rather than ratings. Weekly data cannot cleanly isolate inauguration from the ban one week later.

A passing pretest is not proof of parallel trends; conditioning on it can distort inference (Roth 2022, https://pubs.aeaweb.org/doi/10.1257/aeri.20210236). All specifications remain visible.
