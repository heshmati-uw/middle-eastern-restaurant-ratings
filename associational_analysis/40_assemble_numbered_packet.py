"""Replace the chart packet with revised counts, dictionary, and both rating levels."""
from pathlib import Path
import runpy,shutil
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parent;O=R/'outputs';dest=O/'national_association_monthly.pdf'
shutil.copyfile(O/'figure_01_counts.pdf',dest)
runpy.run_path(str(R/'21_append_food_list.py'))
w=PdfWriter();initial=PdfReader(dest);readers=[initial]
for page in initial.pages:w.add_page(page)
for n in range(2,13):
 stem=f'figure_{n:02d}_'+('counts' if n<=8 else 'ratings')
 reader=PdfReader(O/(stem+'.pdf'));readers.append(reader);w.add_page(reader.pages[0])
with dest.open('wb') as f:w.write(f)
assert len(PdfReader(dest).pages)==13
print('13-page packet: Figures 1-12 plus dictionary page')
