"""Append a reproducible dictionary page to the current chart PDF (idempotent)."""
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parent
registry=json.loads((ROOT/'dictionaries/country_food_registry_v1.json').read_text())
path=ROOT/'outputs/national_association_monthly.pdf'
reader=PdfReader(path)
w,h=float(reader.pages[0].mediabox.width),float(reader.pages[0].mediabox.height)
buf=BytesIO();c=canvas.Canvas(buf,pagesize=(w,h))
styles={
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=19,leading=24,textColor=HexColor('#17212B')),
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=11,leading=15,textColor=HexColor('#263440')),
 'country':ParagraphStyle('country',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=HexColor('#007F86')),
 'note':ParagraphStyle('note',fontName='Helvetica',fontSize=10,leading=13,textColor=HexColor('#36434D')),
}
def para(text,x,y,width,style):
 p=Paragraph(text,styles[style]);_,height=p.wrap(width,h);p.drawOn(c,x,y-height);return y-height
margin=44;full=w-2*margin
y=para('Country-listed foods used in the chart',margin,h-36,full,'title')-10
qualified=[e for e in registry['entries'] if e['country_list_qualifier']]
y=para(f"All {len(qualified)} qualifying dictionary entries across 12 country lists. One mention in any available review qualifies as food evidence for either a literal Middle Eastern or Mediterranean tag. National tags qualify directly.",margin,y,full,'body')-8
y=para('Shared entries appear under every linked country. These lists document culinary associations, not exclusive origins; their coverage is nonexhaustive. Names below consolidate selected variants, while the machine-readable dictionary retains matching patterns.',margin,y,full,'note')-19
display={'kubba':'kibbeh / kubba','aseeda':'aseeda / asida','lahoh':'lahoh / laxoox','qabili_pulao':'qabili / kabuli pulao','lahmacun':'lahmacun / lahmajoun','fesenjan':'fesenjan / fesenjoon','zaatar':"za'atar",'kabsa_machboos':'kabsa / machboos'}
def name(e):return escape(display.get(e['dish_id'],e['dish_id'].replace('_',' ')))
columns=[['Iran','Iraq','Syria','Afghanistan','Armenia','Morocco'],['Yemen','Libya','Somalia','Sudan','Lebanon','Egypt']]
gap=32;cw=(full-gap)/2;bottom=[];covered=set()
for col,countries in enumerate(columns):
 x=margin+col*(cw+gap);cy=y
 for country in countries:
  foods=[e for e in qualified if country in e['countries']];covered.update(e['dish_id'] for e in foods)
  cy=para(country,x,cy,cw,'country')-3
  cy=para('; '.join(name(e) for e in foods)+'.',x,cy,cw,'body')-13
 bottom.append(cy)
assert covered=={e['dish_id'] for e in qualified}
y=min(bottom)-4
y=para('Broader-dictionary entries not qualifying under the current country-list rule',margin,y,full,'country')-3
unmapped=[e for e in registry['entries'] if not e['country_list_qualifier']]
y=para('; '.join(name(e) for e in unmapped)+'. These remain in the broader dictionary but currently lack a documented link in the 12-country registry. They do not qualify a restaurant for WPME or the food-evidence route into nationally associated ME.',margin,y,full,'note')-10
y=para('<b>Excluded standalone terms:</b> shakshuka; generic dolma/dolmeh; baklava; hummus; falafel. The specific dishes dolmeh barg and dolmeh bademjan remain included.',margin,y,full,'note')-9
y=para('Source and pattern audit: dictionaries/country_food_registry_v1.json and outputs/national_association_dictionary.csv. Food mentions are not context-adjudicated and do not verify authenticity or historical menus.',margin,y,full,'note')
assert y>32, f'Food page overflow: {y}'
c.setFont('Helvetica',9);c.setFillColor(HexColor('#66717B'));c.drawRightString(w-margin,20,'2')
c.save();buf.seek(0)
writer=PdfWriter();writer.add_page(reader.pages[0]);writer.add_page(PdfReader(buf).pages[0])
final=BytesIO();writer.write(final);path.write_bytes(final.getvalue())
assert len(PdfReader(path).pages)==2
print(f'Added {len(qualified)} qualifying entries and {len(unmapped)} broader-only entries; bottom margin {y:.1f} pt.')
