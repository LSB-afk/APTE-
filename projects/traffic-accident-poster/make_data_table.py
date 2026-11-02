# -*- coding: utf-8 -*-
"""Standalone styled Data table (PPTX) — copy-paste directly into PowerPoint."""
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

FONT="Pretendard"
NAVY=RGBColor(0x0D,0x39,0x60); WHITE=RGBColor(0xFF,0xFF,0xFF)
INK=RGBColor(0x1A,0x1C,0x1F); BODY=RGBColor(0x2A,0x2E,0x33); CREAM=RGBColor(0xEC,0xF2,0xF7)

rows=[("Item","Value"),
      ("Source","2011–2019 nationwide expressway crashes"),
      ("Target","Injury occurrence (binary)"),
      ("Records","83,297  (Train 66,637 / Test 16,660)"),
      ("Class balance","Injury 10.8%  →  imbalance ≈ 8.3 : 1"),
      ("Predictors","9,684 pre-accident features (one-hot)"),
      ("Leakage control","Post-crash response / outcome vars removed")]

prs=Presentation()
prs.slide_width=Cm(33.87); prs.slide_height=Cm(19.05)
slide=prs.slides.add_slide(prs.slide_layouts[6])  # blank
nr,nc=len(rows),2
gf=slide.shapes.add_table(nr,nc,Cm(4.0),Cm(4.5),Cm(26.0),Cm(10.0))
tbl=gf.table
tbl.first_row=False; tbl.horz_banding=False
tbl.columns[0].width=Cm(7.5); tbl.columns[1].width=Cm(18.5)

def setrun(run,size,bold,color):
    run.font.name=FONT; run.font.size=Pt(size); run.font.bold=bold; run.font.color.rgb=color
    rPr=run._r.get_or_add_rPr()
    for t in ("a:latin","a:ea","a:cs"):
        e=rPr.find(qn(t))
        if e is None: e=rPr.makeelement(qn(t),{}); rPr.append(e)
        e.set("typeface",FONT)

for r,(k,v) in enumerate(rows):
    for c,val in enumerate((k,v)):
        cell=tbl.cell(r,c); cell.text=val; cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.margin_left=Cm(0.3); cell.margin_right=Cm(0.25); cell.margin_top=Cm(0.1); cell.margin_bottom=Cm(0.1)
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.LEFT
        hdr=(r==0)
        setrun(p.runs[0],size=20 if hdr else 18,bold=hdr or c==0,
               color=WHITE if hdr else (NAVY if c==0 else BODY))
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if hdr else (CREAM if r%2 else WHITE)

prs.save("Data_table.pptx")
print("SAVED Data_table.pptx")
