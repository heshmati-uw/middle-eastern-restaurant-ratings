# ME-WPME parallel-trends plots around the ban

Extract [ban_ME_WPME_trends.zip](ban_ME_WPME_trends.zip), then open analysis_clean/full_pre_election_core/ban_ME_WPME_trends/ban_trends_report.html. Includes all data, code, PNG/SVG plots and independent verification.

Fixed-cohort four-week means use the same restaurants at every point, with unit restaurant weights: Trump counties 63 ME / 54 WPME; non-Trump 938 ME / 746 WPME. Blocks: Nov 28-Dec 25; Dec 26-Jan 22; Jan 30-Feb 26. The mixed Jan 23 week is omitted. WPME ratings decline before the ban and rebound afterward in Trump counties, while ME moves in the opposite direction.

Weekly event study: restaurant and county-by-week FE; each restaurant has total observed-panel weight one; county-clustered 95% intervals. Nine pre-leads are tested jointly against the Jan 16 reference week. Trump p=.001054 (69 ME / 61 WPME, 23 counties); non-Trump p=.236803 (1,056 ME / 817 WPME, 148 counties). This rejects parallel pre-trends in Trump counties; non-rejection in non-Trump counties is not proof of parallel trends. Samples differ from the fixed-cohort plot; the report explains sparse-week coverage and shows weekly observed means and Ns. The Trump test is a finite-cluster approximation and does not identify why trends differ.

Mediterranean definition confirmed by user: observed eligible pre-election review text and no core-dish mention. Shared-food mentions remain allowed. The full raw scan already implements this; Mediterranean restaurants are absent from ME-WPME models.
