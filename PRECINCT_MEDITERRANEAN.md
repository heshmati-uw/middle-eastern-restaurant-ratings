# Core-only precinct comparisons with Mediterranean

Extract [precinct_core_mediterranean.zip](precinct_core_mediterranean.zip) and open analysis_clean/precinct_core_mediterranean/precinct_mediterranean_report.html. Includes inputs, code, results, plots and independent NumPy verification of 80 models.

The gradient measures first-group-minus-MED rating changes per +10 percentage points of precinct Trump share. Four-week windows; 27 core pre-election dish tags only; equal restaurant weights; county fixed effects; county-clustered standard errors. Negative gradients mean the first group loses more ground as Trump support rises.

| Shock | Comparison | Gradient | Raw p | First-group/MED restaurants | Counties |
|---|---|---:|---:|---:|---:|
| Election | ME-MED | -.0196 | .3919 | 1,118 / 1,148 | 192 |
| Election | WPME-MED | -.0254 | .4104 | 490 / 1,069 | 154 |
| Ban | ME-MED | +.0323 | .1795 | 1,260 / 1,314 | 208 |
| Ban | WPME-MED | +.0435 | .1893 | 525 / 1,201 | 167 |

No pooled primary gradient reaches p<.05. Election WPME-MED within Trump counties has a weak negative gradient (p=.0945); ban ME-MED within non-Trump counties has a weak positive gradient (p=.0744). Additional county-gradient control yields a positive pooled ban ME-MED slope p=.0207, but county-by-group FE p=.0742 and baseline adjustment p=.3667. All specifications, raw p-values and separate Holm corrections are reported.

MED means primary Mediterranean with observed pre-election text and no detected core tag; it includes shared-only food mentions and is not verified absence of Middle Eastern food. Pairwise common-county samples differ. Precinct geography/source provenance is inherited from the earlier documented SAGE linkage. These are exploratory associations, not established causal effects.
