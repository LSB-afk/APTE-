# -*- coding: utf-8 -*-
"""Standalone styled Model setup table (PPTX) — copy-paste directly into PowerPoint."""
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

FONT="Pretendard"
NAVY=RGBColor(0x0D,0x39,0x60); WHITE=RGBColor(0xFF,0xFF,0xFF)
NAVYC=RGBColor(0x0D,0x39,0x60); BODY=RGBColor(0x2A,0x2E,0x33); CREAM=RGBColor(0xEC,0xF2,0xF7)

rows=[("Item","Specification"),
      ("Model","XGBoost binary classifier (binary:logistic)"),
      ("Target","Injury occurrence (binary)"),
      ("Hyperparameters","600 trees · depth 4 · LR 0.03 · subsample/colsample 0.85"),
      ("Regularization","min_child_weight 3 · gamma 0.1 · L1 0.1 · L2 2.0"),
      ("Imbalance handling","scale_pos_weight = 5  (tested 5–18, 8.26)"),
      ("Validation","Stratified 80 / 20 train–test split"),
      ("Threshold","0.65  (tuned 0.05–0.95, best F1)"),
      ("Interpretation","Feature importance (gain/weight/cover) + SHAP"),
      ("Metrics","Accuracy · Precision · Recall · F1 · ROC-AUC · PR-AUC")]

prs=Presentation(); prs.slide_width=Cm(33.87); prs.slide_height=Cm(19.05)
slide=prs.slides.add_slide(prs.slide_layouts[6])
nr,nc=len(rows),2
tbl=slide.shapes.add_table(nr,nc,Cm(3.0),Cm(3.2),Cm(28.0),Cm(12.6)).table
tbl.first_row=False; tbl.horz_banding=False
tbl.columns[0].width=Cm(8.0); tbl.columns[1].width=Cm(20.0)

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
        cell.margin_left=Cm(0.3); cell.margin_right=Cm(0.25); cell.margin_top=Cm(0.08); cell.margin_bottom=Cm(0.08)
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.LEFT
        hdr=(r==0)
        setrun(p.runs[0],size=19 if hdr else 17,bold=hdr or c==0,
               color=WHITE if hdr else (NAVYC if c==0 else BODY))
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if hdr else (CREAM if r%2 else WHITE)

prs.save("Model_setup_table.pptx")
print("SAVED Model_setup_table.pptx")
