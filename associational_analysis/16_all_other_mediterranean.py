"""Package the requested all-other-Mediterranean definitions (prior V2/V4)."""
from pathlib import Path
import csv,shutil
from pypdf import PdfWriter
ROOT=Path(__file__).resolve().parent;out=ROOT/'outputs'
with (out/'positioning_variants_monthly.csv').open() as f:rows=list(csv.DictReader(f))
selected=[{**r,'group':'All other Mediterranean restaurants' if r['group']=='Other Mediterranean' else r['group']} for r in rows if r['version'] in ['V2','V4'] and r['group']!='Unclassified']
with (out/'all_other_mediterranean_monthly.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
with (out/'seven_county_monthly_counts.csv').open() as f:original=list(csv.DictReader(f))
for v in ['V2','V4']:
    for m in {r['month'] for r in selected}:
        assert sum(int(r['restaurants']) for r in selected if r['version']==v and r['month']==m)==sum(int(r['restaurants']) for r in original if r['month']==m and r['label']!='American')
writer=PdfWriter()
for v,suffix in [('V2','broader'),('V4','seven_country')]:
    for ext in ['png','pdf']:shutil.copyfile(out/f'positioning_variants_{v}.{ext}',out/f'all_other_mediterranean_{suffix}.{ext}')
    writer.append(str(out/f'all_other_mediterranean_{suffix}.pdf'))
writer.write(str(out/'all_other_mediterranean_figures.pdf'));writer.close()
# Refresh the historical four-version packet with the clarified residual labels.
writer=PdfWriter()
for v in ['V1','V2','V3','V4']:writer.append(str(out/f'positioning_variants_{v}.pdf'))
writer.write(str(out/'positioning_variants_all_figures.pdf'));writer.close()
(out/'all_other_mediterranean_validation.txt').write_text('Both definitions exhaust all monthly review-active non-American restaurants in the seven counties. No matching, balanced-cohort, additional Mediterranean-food, or later-outcome restriction. WPME remains classified from pre-election food evidence.\n')
