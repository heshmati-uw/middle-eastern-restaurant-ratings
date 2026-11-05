"""Keep the chart and dictionary pages; append the seven-country figure as page 3."""
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader,PdfWriter
root=Path(__file__).resolve().parent/'outputs'
path=root/'national_association_monthly.pdf'
reader=PdfReader(path);extra=PdfReader(root/'ban_country_monthly.pdf')
assert len(reader.pages)>=2,'Run steps 20 and 21 first to create the chart and dictionary pages.'
writer=PdfWriter()
for p in reader.pages[:2]:writer.add_page(p)
writer.add_page(extra.pages[0]);buf=BytesIO();writer.write(buf);path.write_bytes(buf.getvalue())
assert len(PdfReader(path).pages)==3
print('Chart packet now has three pages.')
