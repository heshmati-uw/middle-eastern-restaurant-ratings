# Full raw pre-election core-tag scan and precinct reruns

Extract [full_pre_election_core.zip](full_pre_election_core.zip), then open analysis_clean/full_pre_election_core/full_core_report.html. Contains all derived modeling inputs, code, results, plots, sample-growth tables, old sample comparisons and independent verification. Raw review text and reviewer identities are excluded.

All 52 review files read to completion: 666,324,103 rows. Exact review duplicates removed among selected primary-Mediterranean pre-election reviews. Core dictionary unchanged; tags frozen before November 8, 2016 UTC for both shocks. Observed pre-election text businesses: 2,765 -> 3,450; core-tagged primary-Mediterranean businesses: 661 -> 1,293. Remaining unknown: 1,992.

Four-week windows and equal restaurant weights unchanged; existing full rating/count outcomes reused. Main model: county FE, group indicator, continuous precinct Trump share, and group-by-share interaction; county-clustered CR1 inference. Gradient units are first-group-minus-second-group rating changes per +10 percentage points of precinct Trump share. Negative means the first group loses more ground as local Trump support rises.

| Shock | County stratum | Comparison | Gradient | Raw p | N first / second |
|---|---|---|---:|---:|---:|
| Election | All counties | ME vs WPME | -0.0039 | 0.8646 | 1,057 / 799 |
| Election | Trump counties | ME vs WPME | +0.0512 | 0.4629 | 59 / 55 |
| Election | Non-Trump counties | ME vs WPME | +0.0061 | 0.8175 | 998 / 744 |
| Election | All counties | ME vs MED | -0.0221 | 0.3850 | 1,084 / 977 |
| Election | Trump counties | ME vs MED | -0.1222 | 0.2018 | 50 / 106 |
| Election | Non-Trump counties | ME vs MED | -0.0105 | 0.7017 | 1,034 / 871 |
| Election | All counties | WPME vs MED | -0.0163 | 0.5680 | 825 / 961 |
| Election | Trump counties | WPME vs MED | -0.1456 | 0.0513 | 55 / 87 |
| Election | Non-Trump counties | WPME vs MED | -0.0030 | 0.9276 | 770 / 874 |
| Ban | All counties | ME vs WPME | +0.0118 | 0.6634 | 1,186 / 900 |
| Ban | Trump counties | ME vs WPME | -0.0346 | 0.7158 | 72 / 62 |
| Ban | Non-Trump counties | ME vs WPME | +0.0465 | 0.0802 | 1,114 / 838 |
| Ban | All counties | ME vs MED | +0.0340 | 0.1726 | 1,231 / 1,113 |
| Ban | Trump counties | ME vs MED | +0.1290 | 0.0834 | 92 / 136 |
| Ban | Non-Trump counties | ME vs MED | +0.0455 | 0.1199 | 1,139 / 977 |
| Ban | All counties | WPME vs MED | +0.0350 | 0.2315 | 921 / 1,095 |
| Ban | Trump counties | WPME vs MED | +0.0859 | 0.3876 | 74 / 122 |
| Ban | Non-Trump counties | WPME vs MED | +0.0280 | 0.3725 | 847 / 973 |

Includes the same 120 model/sensitivity/placebo calculations, all independently verified in NumPy. Separate Holm corrections are saved alongside raw p-values. Full source scanning and deduplication audit is included. The ban WPME-MED pre-event placebo gradient is negative (raw p=.0098; six-placebo Holm=.0588), an identification concern for causal interpretation. MED is observed eligible text without a core-dish tag; it is not verified absence of Middle Eastern food. Mentions are a proxy for offerings, not nationality or authenticity. Local resident votes are not reviewer ideology. Expanded samples and non-rejected placebos do not establish causal effects.
