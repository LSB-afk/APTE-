# -*- coding: utf-8 -*-
"""APTE 2026 English poster — XGBoost-SHAP injury-occurrence factor analysis.
Keeps template chrome, replaces all content with English text + EN charts."""
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image
from lxml import etree as ET

SRC="2026_APTE_학회_이승보.pptx"; OUT="2026_APTE_Poster_EN.pptx"; CH="charts_en"
FONT="Pretendard"
NAVY=RGBColor(0x0D,0x39,0x60); CYAN=RGBColor(0x2C,0x8F,0xC4); INK=RGBColor(0x1A,0x1C,0x1F)
BODY=RGBColor(0x2A,0x2E,0x33); WHITE=RGBColor(0xFF,0xFF,0xFF); GREY=RGBColor(0x5E,0x6B,0x78)
CREAMHDR=RGBColor(0xEC,0xF2,0xF7)
BP=25

prs=Presentation(SRC); slide=prs.slides[0]
# drop stale OMML formula shapes
spTree=slide.shapes._spTree
for ch in list(spTree):
    if ET.QName(ch).localname=="AlternateContent" and any(ET.QName(d).localname=="oMath" for d in ch.iter()):
        spTree.remove(ch)

def allsh(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type==6: yield from allsh(sh.shapes)
BYID={sh.shape_id:sh for sh in allsh(slide.shapes)}

def no_bullet(p):
    pPr=p._p.get_or_add_pPr()
    for t in ("a:buChar","a:buAutoNum","a:buNone"):
        e=pPr.find(qn(t));  pPr.remove(e) if e is not None else None
    pPr.append(pPr.makeelement(qn("a:buNone"),{}))
def set_font(r,size=None,bold=None,color=None,name=FONT):
    r.font.name=name; rPr=r._r.get_or_add_rPr()
    for t in ("a:latin","a:ea","a:cs"):
        e=rPr.find(qn(t))
        if e is None: e=rPr.makeelement(qn(t),{}); rPr.append(e)
        e.set("typeface",name)
    if size is not None: r.font.size=Pt(size)
    if bold is not None: r.font.bold=bold
    if color is not None: r.font.color.rgb=color
def fill_body(shape,items,size=BP,color=BODY,align=PP_ALIGN.LEFT,sa=6,line=1.06,anchor=None):
    tf=shape.text_frame; tf.word_wrap=True
    if anchor is not None: tf.vertical_anchor=anchor
    tf.clear()
    for i,it in enumerate(items):
        txt,b=(it if isinstance(it,tuple) else (it,False))
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(sa); p.space_before=Pt(0); p.line_spacing=line
        no_bullet(p); r=p.add_run(); r.text=txt; set_font(r,size=size,bold=b,color=color)
def set_header(shape,text,size=None,color=None):
    tf=shape.text_frame; p=tf.paragraphs[0]; cur=None
    for r in p.runs:
        if r.font.size: cur=r.font.size.pt; break
    if not p.runs: r=p.add_run()
    else:
        r=p.runs[0]
        for ex in p.runs[1:]: ex._r.getparent().remove(ex._r)
    for ex in tf.paragraphs[1:]: ex._p.getparent().remove(ex._p)
    r.text=text; set_font(r,size=(size or cur),color=color)
def delete(sid):
    sh=BYID.get(sid)
    if sh is not None: sh._element.getparent().remove(sh._element)
def move(sid,x=None,y=None,w=None,h=None):
    sh=BYID[sid]
    if x is not None: sh.left=Cm(x)
    if y is not None: sh.top=Cm(y)
    if w is not None: sh.width=Cm(w)
    if h is not None: sh.height=Cm(h)
def img_h(path,w): im=Image.open(path); return w*im.height/im.width
def add_img(path,x,y,w):
    slide.shapes.add_picture(path,Cm(x),Cm(y),width=Cm(w)); return img_h(path,w)
def add_text(x,y,w,h,items,size=BP,color=BODY,align=PP_ALIGN.LEFT,bold=False,line=1.06,sa=5,anchor=MSO_ANCHOR.TOP):
    tb=slide.shapes.add_textbox(Cm(x),Cm(y),Cm(w),Cm(h)); tf=tb.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=Cm(0.1); tf.margin_right=Cm(0.1); tf.margin_top=Cm(0.05); tf.margin_bottom=Cm(0.05)
    for i,it in enumerate(items):
        txt,b=(it if isinstance(it,tuple) else (it,bold))
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(sa); p.space_before=Pt(0); p.line_spacing=line
        no_bullet(p); r=p.add_run(); r.text=txt; set_font(r,size=size,bold=b,color=color)
    return tb
def subheader(x,y,w,text,size=25):
    bar=slide.shapes.add_shape(1,Cm(x),Cm(y+0.05),Cm(0.28),Cm(0.95))
    bar.fill.solid(); bar.fill.fore_color.rgb=CYAN; bar.line.fill.background()
    add_text(x+0.5,y-0.1,w-0.5,1.3,[text],size=size,color=NAVY,bold=True,anchor=MSO_ANCHOR.MIDDLE)

# ================= HEADER =================
set_header(BYID[5],"2026 APTE Conference")
set_header(BYID[6],"Factors Associated with Injury Occurrence in Expressway Crashes: An Interpretable XGBoost–SHAP Analysis",size=42)
set_header(BYID[7],"Nonlinear and interaction-based injury-risk factors in nationwide freeway crash data (2011–2019)",size=30)
# authors (abstract: Seungbo Lee, Seonjae Lee, Eunjeong Ko)
def author(sid,text,x,w):
    sh=BYID[sid]; sh.left=Cm(x); sh.top=Cm(8.4); sh.width=Cm(w)
    set_header(sh,text)
    sh.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
    sh.text_frame.word_wrap=False
author(116,"Seungbo Lee¹",21.5,13)
author(115,"Seonjae Lee¹",36.0,12)
author(60,"Eunjeong Ko²·*",48.5,15)
delete(113)
set_header(BYID[24],"¹Dept. of Management Information Systems, Hannam University    ²Dept. of Big Data Application, Hannam University    * Corresponding author: eunjeong.ko@hnu.kr")

# ================= LEFT COLUMN =================
set_header(BYID[168],"Introduction",size=36)
fill_body(BYID[199],[
    "• High-speed expressway crashes are more likely to cause injuries and large socioeconomic losses.",
    "• Prior injury-severity studies often assume linear / additive effects → they miss nonlinear and interaction-based risk structures.",
    "• Severe class imbalance further challenges conventional models.",
    "• We build an interpretable XGBoost model and use SHAP to reveal injury-occurrence risk factors.",
])
set_header(BYID[28],"Objective")
fill_body(BYID[209],[
    "• Identify factors associated with injury occurrence and interpret their direction via SHAP.",
    "• Support proactive expressway safety management and countermeasure prioritization.",
],color=INK)

set_header(BYID[216],"Methodology",size=34)
def flow_title(sid,text,x):
    sh=BYID[sid]; sh.left=Cm(x); sh.top=Cm(49.0); sh.width=Cm(12.0); sh.height=Cm(2.0)
    fill_body(sh,[text],size=22,color=NAVY,align=PP_ALIGN.CENTER,sa=0,anchor=MSO_ANCHOR.MIDDLE)
    sh.text_frame.paragraphs[0].runs[0].font.bold=True
flow_title(236,"① Data & preprocessing",1.9)
flow_title(294,"② Model training",15.2)
flow_title(303,"③ Evaluation & SHAP",28.5)
fill_body(BYID[229],["2011–2019 expressway crashes","Remove post-crash leakage cols","One-hot → 9,684 features"])
fill_body(BYID[292],["XGBoost binary (n=600, depth=4)","scale_pos_weight = 8.26","Stratified 80 / 20 split"])
fill_body(BYID[301],["Threshold opt (0.50 → 0.65)","ROC · PR-AUC · F1","SHAP global + direction"])

set_header(BYID[320],"Data")
move(323,w=16.8)
fill_body(BYID[323],[
    ("■ Dataset",True),
    "• Source: 2011–2019 nationwide expressway crashes",
    "• Target: injury occurrence (binary)",
    "• 83,297 records (Train 66,637 / Test 16,660)",
    "• Injury 10.8% → class imbalance ≈ 8.3 : 1",
    "• 9,684 pre-accident features (one-hot)",
    "• Post-crash response / outcome vars removed (leakage)",
],sa=5)
add_img(f"{CH}/fig_en_traintest.png",19.2,63.5,21.5)

move(331,w=20); set_header(BYID[331],"Pre-accident variables",size=30)
move(335,w=12); set_header(BYID[335],"Model setup",size=34)
fill_body(BYID[336],[
    "• Model: XGBoost binary classification",
    "• Imbalance: scale_pos_weight + threshold optimization",
    "• Validation: stratified 80 / 20 train–test split",
    "• Interpretation: feature importance (gain) + SHAP",
])
move(441,w=20); set_header(BYID[441],"Conclusion & future work",size=30)
fill_body(BYID[58],[
    "• Pre-accident information predicts expressway injury occurrence (Test ROC-AUC 0.853, PR-AUC 0.499).",
    "• SHAP identifies vehicle–pedestrian crashes, long driving time, steering overcorrection, drowsiness and roadway debris as key risk-raising factors.",
    "• Threshold optimization (0.50→0.65) improves precision and F1 under severe class imbalance.",
    "• Findings support proactive safety management and early-warning systems; future work: SHAP interaction analysis.",
],sa=4)

# ---- pre-accident variable table (id=2) ----
t=BYID[2].table; nrows=len(t.rows); ncols=len(t.columns)
rows=[("Category","Examples"),
      ("Crash","Crash type, No. of vehicles, main cause, pre-crash maneuver"),
      ("Driver / Vehicle","Driver state, sex, age group, vehicle type & size"),
      ("Road geometry","Route, milepost, lane, alignment, superelevation"),
      ("Environment / Location","Weather, road surface, day-night, hour, branch, mainline / tunnel / tollgate")]
for r in range(nrows):
    for c in range(ncols): t.cell(r,c).text=""
for r in range(min(nrows,len(rows))):
    cat,ex=rows[r]; t.cell(r,0).text=cat
    t.cell(r,1).merge(t.cell(r,ncols-1)); t.cell(r,1).text=ex
t.columns[0].width=Cm(9.5)
for c in range(1,ncols): t.columns[c].width=Cm(30.0/(ncols-1))
for r in range(nrows):
    for c in range(ncols):
        cell=t.cell(r,c); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.margin_left=Cm(0.2); cell.margin_right=Cm(0.2); cell.margin_top=Cm(0.06); cell.margin_bottom=Cm(0.06)
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                set_font(run,size=24,bold=(r==0 or c==0),
                         color=WHITE if r==0 else (NAVY if c==0 else BODY))
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if r==0 else (CREAMHDR if r%2 else WHITE)

# ================= RIGHT COLUMN =================
set_header(BYID[40],"Results")
for sid in (15,14,16,17,4,51,56,1030,54,55,59): delete(sid)
RX=43.4; RW=37.0
add_text(RX,18.9,RW,1.5,["Under severe class imbalance, F1 and PR-AUC matter more than accuracy; the decision threshold was tuned 0.50 → 0.65."],size=25,color=GREY,line=1.05)

# 1. performance
subheader(RX,21.4,RW,"1. Model performance (Test set)",size=25)
add_img(f"{CH}/fig_en_performance.png",RX+0.3,23.4,20.2)
perf=[("Metric","0.50","0.65"),("Accuracy","0.848","0.886"),("Precision","0.377","0.473"),
      ("Recall","0.629","0.518"),("F1-score","0.472","0.494"),("ROC-AUC","0.853","0.853"),("PR-AUC","0.499","0.499")]
ptx,pty,ptw=64.7,23.6,15.2
g=slide.shapes.add_table(len(perf),3,Cm(ptx),Cm(pty),Cm(ptw),Cm(11.0)).table
g.columns[0].width=Cm(6.4); g.columns[1].width=Cm(4.4); g.columns[2].width=Cm(4.4)
for r,row in enumerate(perf):
    for c,val in enumerate(row):
        cell=g.cell(r,c); cell.text=val; cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.margin_left=Cm(0.15); cell.margin_right=Cm(0.1); cell.margin_top=Cm(0.04); cell.margin_bottom=Cm(0.04)
        for p in cell.text_frame.paragraphs:
            p.alignment=PP_ALIGN.LEFT if c==0 else PP_ALIGN.CENTER
            for run in p.runs:
                hl=(c==2 and r in (1,2,4))
                set_font(run,size=25,bold=(r==0 or c==0 or hl),
                         color=WHITE if r==0 else (CYAN if hl else (NAVY if c==0 else BODY)))
        cell.fill.solid(); cell.fill.fore_color.rgb=NAVY if r==0 else (CREAMHDR if r%2 else WHITE)
add_text(ptx,pty+11.3,ptw,1.2,["Selected threshold = 0.65 (best F1)"],size=18,color=GREY)

# 2. ROC / PR
subheader(RX,36.0,RW,"2. Discrimination · ROC / PR curves",size=25)
rh=add_img(f"{CH}/fig_en_roc_pr.png",RX+1.4,37.8,34.0)
ycur=37.8+rh+0.15
add_text(RX,ycur,RW,1.4,["ROC-AUC 0.853 (strong ranking) · PR-AUC 0.499 (≈4.6× the 0.108 baseline)"],size=25,color=GREY,line=1.05)

# 3. SHAP beeswarm
subheader(RX,53.6,RW,"3. SHAP summary — injury-risk factors",size=25)
bh=add_img(f"{CH}/fig_en_shap_beeswarm.png",RX+2.0,55.6,32.0)

# 4. SHAP direction
yd=55.6+bh+0.6
subheader(RX,yd,RW,"4. Risk direction (gold ↑ raises / blue ↓ lowers)",size=25)
fh=add_img(f"{CH}/fig_en_shap_factors.png",RX+2.6,yd+1.9,30.0)
add_text(RX,yd+1.9+fh+0.2,RW,2.2,
         ["Vehicle–pedestrian crashes, long driving time, steering overcorrection, drowsiness and roadway debris raise injury risk — all identifiable before the crash."],
         size=25,color=BODY,line=1.08)

# ---- acknowledgment prefix KO->EN ----
for _sh in allsh(slide.shapes):
    if _sh.has_text_frame:
        for _p in _sh.text_frame.paragraphs:
            for _r in _p.runs:
                if "사사" in _r.text:
                    _r.text = _r.text.replace("사사:", "Acknowledgment: ").replace("사사", "Acknowledgment: ")

# ---- normalize all fonts to Pretendard ----
def force(tf):
    for para in tf.paragraphs:
        for r in para.runs:
            r.font.name=FONT; rPr=r._r.get_or_add_rPr()
            for t2 in ("a:latin","a:ea","a:cs"):
                e=rPr.find(qn(t2))
                if e is None: e=rPr.makeelement(qn(t2),{}); rPr.append(e)
                e.set("typeface",FONT)
for sh in allsh(slide.shapes):
    if sh.has_text_frame: force(sh.text_frame)
    if sh.has_table:
        for row in sh.table.rows:
            for c in row.cells: force(c.text_frame)

prs.save(OUT)
print("SAVED",OUT)
print("roc bottom:",37.8+img_h(f'{CH}/fig_en_roc_pr.png',34.0))
print("beeswarm bottom:",55.6+img_h(f'{CH}/fig_en_shap_beeswarm.png',32.0))
print("factors block end:",yd+1.9+img_h(f'{CH}/fig_en_shap_factors.png',30.0))
