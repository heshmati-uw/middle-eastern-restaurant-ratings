# Common-sample matching and holiday follow-ups

Extract matching_followups.zip into the workspace/repository root. Open analysis_clean/full_pre_election_core/attribute_matching/common_triplets/common_sample_report.html.

Common matching: one ME, one WPME and one MED restaurant per county-price matched triplet, no replacement, outcome-blind geographic assignment anchored to the smallest group in each county-price stratum. See design.json for exact algorithm. All three contrasts use the same restaurants and common MED comparator within an event and county stratum. Different events have different cohorts. Holidays included.

Common mean sample sizes per group: election Trump 14 (7 counties), non-Trump 319 (88); ban Trump 19 (11), non-Trump 364 (93). Weekly diagnostics retain complete triplets meeting pre/post observation requirements: ban Trump 18 per group in 10 counties. Weekly observation composition can still vary.

Ban Trump: ME-WPME -0.517 (p=.164), ME-MED -0.393 (p=.267), WPME-MED +0.123 (p=.729). Ban non-Trump: ME-WPME +0.140 (p=.098). Equal restaurant weights, triplet FE and county-clustered inference. All 12 mean contrasts and four weekly models were independently verified, including covariance matrices and the three-group contrast identity. Trump joint pretests have very few clusters, may be unstable or not estimable. Undated price metadata cannot establish historical comparability or causality.

Reproduce estimates/plots: Rscript analysis_clean/common_triplet_models.R
Verify and rebuild report: python analysis_clean/report_common_triplets.py
Requires R data.table, fixest, jsonlite and Python numpy/pandas. R regenerates the omitted large numerical-verification input CSVs. Frozen common matched data and weekly inputs are included. Reconstruct triplets using common_triplet_matching.py (SciPy required) plus restaurant_attributes.csv and six pairwise sample CSVs from the prior full_pre_election_core snapshot.

Also included: holiday-restored non-Trump price ME-WPME results; separate-pair Trump Mediterranean plots; raw two-line Trump ME-WPME plot with weekly counts. These older pairwise follow-ups use separate samples and should not be confused with the common-triplet analysis. Their underlying matched inputs are in the earlier attribute_matching.zip. All food tags remain full-raw pre-election core labels; MED excludes core mentions, shared mentions allowed.
