"""Run from the packaged weekly input; no Dropbox access required."""
from pathlib import Path
import subprocess, sys
root=Path(__file__).resolve().parent
rscript=sys.argv[1] if len(sys.argv)>1 else 'Rscript'
subprocess.run([rscript,str(root/'county_difference_models.R')],cwd=root,check=True)
subprocess.run([sys.executable,str(root/'report_county_differences.py')],cwd=root,check=True)
