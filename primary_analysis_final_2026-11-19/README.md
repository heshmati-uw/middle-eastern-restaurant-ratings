# Final 11-19 with pre-trends | November 19, 2026

Start with the [standalone results summary](travel_ban_summary_results.html). Download and extract the [analysis archive](primary_analysis_final_2026-11-19.zip) for code, analysis inputs, results, tables, plots and diagnostics. The [November 18 checkpoint](../primary_analysis_final_2026-11-18/README.md) preserves the preceding analysis.

## Restaurant-level results

The main ME/WPME regression compares December 16-January 26 with January 27-March 9. Each restaurant contributes one equally weighted post-minus-pre mean rating change. The comparison uses 2,346 restaurants eligible under both aligned outcome-window definitions and county fixed effects. Historical rating and activity controls pool October 10-November 6 and November 14-December 11. Price, service and alcohol measures are undated. The WPME-ME association is +0.213 stars in Trump-majority counties (p=.028), -0.004 elsewhere (p=.926), and +0.216 in the direct county-type comparison (p=.028). These are correlational results.

The archive also retains the aligned four-week restaurant models for all three pairs, the four- versus six-week comparisons, the earlier-control sensitivity checks, and summary descriptives and county-clustered Pearson correlation tests.

## Pretrends and weekly results

- [Exact raw ten-week pretrend plot](raw_pretrends_ten_weeks.png) and [exact raw four-week pretrend plot](raw_pretrends_four_weeks.png). The ten-week Trump-county trend slope has p=.032 with all controls. The Trump four-week joint pretest has p=.004 with all controls. The raw-only report in the archive explains each regression and displays both plots.
- Six-week Friday-to-Thursday event study, with January 27 as the calendar-date boundary and Monday midpoints. The restaurant and county-by-week FE model estimates +0.260 (p=.041) in Trump-majority counties and -0.013 (p=.788) elsewhere. Those estimates use a different sample, weighting across observed weeks and historical controls from the restaurant-change regression.
- The Monday-based comparison, the July-April raw ratings timeline and the ban close-up are included. Several pretrend tests raise concerns about a causal ban interpretation.

## Reopen or rerun

Open the standalone summary in a browser. After extracting the archive, the original report hierarchy is under `analysis_clean/`. Exact pretrend diagnostics are in `preban_trends_2026_11_19/preban_trends_report.html`. The Friday event-study report is in `ban_friday_event_study_2026_11_19/friday_event_study_report.html`.

From the extracted root, install the R packages fixest, data.table and jsonlite and Python packages numpy, pandas and scipy. The following commands refit the main model from frozen rated-review and restaurant inputs and rebuild the figures and summary:

```sh
Rscript analysis_clean/compare_aligned_outcome_windows.R
Rscript analysis_clean/plot_six_week_eight_week_history.R
Rscript analysis_clean/plot_six_week_adjusted_pre_post.R
python analysis_clean/build_six_week_summary.py
```

For the weekly and pretrend fits, run `Rscript analysis_clean/ban_friday_event_study_2026_11_19.R` and `Rscript analysis_clean/preban_trends_2026_11_19.R`. Frozen verification outputs are included. Older integrity-check scripts that compare the original desktop files reference local paths. Raw scanning scripts require access to the original project archives. The archive contains frozen extracted ratings, not the original multi-gigabyte archives, reviewer names or review text.
