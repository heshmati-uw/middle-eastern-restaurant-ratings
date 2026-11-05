"""Preserve earlier versions and append vote-group overlays as pages 6 and 7."""
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader,PdfWriter
root=Path(__file__).resolve().parent/'outputs';path=root/'national_association_monthly.pdf'
reader=PdfReader(path);assert len(reader.pages)>=5,'Run steps 20-28 first.'
w=PdfWriter()
for page in reader.pages[:5]:w.add_page(page)
for name in ['county_vote_broad.pdf','county_vote_ban.pdf']:w.add_page(PdfReader(root/name).pages[0])
b=BytesIO();w.write(b);path.write_bytes(b.getvalue());assert len(PdfReader(path).pages)==7
print('Seven-page packet; county vote overlays on pages 6 and 7.')
