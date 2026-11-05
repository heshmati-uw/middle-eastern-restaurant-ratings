"""Append unrestricted-county charts as pages 4 and 5, retaining earlier versions."""
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader,PdfWriter
root=Path(__file__).resolve().parent/'outputs';path=root/'national_association_monthly.pdf'
reader=PdfReader(path);assert len(reader.pages)>=3,'Run steps 20-24 first.'
w=PdfWriter()
for page in reader.pages[:3]:w.add_page(page)
for name in ['all_trump_broad.pdf','all_trump_ban.pdf']:w.add_page(PdfReader(root/name).pages[0])
b=BytesIO();w.write(b);path.write_bytes(b.getvalue());assert len(PdfReader(path).pages)==5
print('Five-page packet: original chart, food lists, original ban chart, all-county broad chart, all-county ban chart.')
