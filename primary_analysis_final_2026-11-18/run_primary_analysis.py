from pathlib import Path
import argparse,os,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--rscript',default='Rscript');a=p.parse_args()
r=Path(__file__).resolve().parent;os.chdir(r)
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
steps=[[a.rscript,'analysis_clean/ban_controls_preview.R'],[sys.executable,'analysis_clean/ban_controls_preview_verify.py','--numerical-only'],[a.rscript,'analysis_clean/ban_observed_all_controls_figure.R'],[sys.executable,'analysis_clean/original_primary_tables.py'],[sys.executable,'analysis_clean/export_shareable_pdf.py']]
for cmd in steps:subprocess.run(cmd,check=True)
print('Primary analysis reproduced. Open output/pdf/restaurant_positioning_ban_results.pdf')
