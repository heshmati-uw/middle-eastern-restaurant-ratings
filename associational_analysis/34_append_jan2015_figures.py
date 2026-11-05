"""Preserve earlier versions and append vote-group overlays as pages 8 and 9."""
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader,PdfWriter
root=Path(__file__).resolve().parent/'outputs';path=root/'national_association_monthly.pdf'
reader=PdfReader(path);assert len(reader.pages)>=7,'Run steps 20-31 first.'
w=PdfWriter()
for page in reader.pages[:7]:w.add_page(page)
for name in ['county_vote_jan2015_broad.pdf','county_vote_jan2015_ban.pdf']:w.add_page(PdfReader(root/name).pages[0])
b=BytesIO();w.write(b);path.write_bytes(b.getvalue());assert len(PdfReader(path).pages)==9
print('Nine-page packet; January 2015 extensions on pages 8 and 9.')
