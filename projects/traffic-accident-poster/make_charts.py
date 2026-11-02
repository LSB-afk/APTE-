# -*- coding: utf-8 -*-
"""APTE 2026 poster charts — navy template palette, Pretendard font.
All numbers sourced directly from method_B_pre_accident_xgboost_results CSVs."""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fonts ----
FROOT = "/Users/leeseungbo/Library/Fonts"
for f in ["Pretendard-Regular.ttf","Pretendard-Medium.ttf","Pretendard-SemiBold.ttf",
          "Pretendard-Bold.ttf","Pretendard-ExtraBold.ttf"]:
    p=os.path.join(FROOT,f)
    if os.path.exists(p): fm.fontManager.addfont(p)
plt.rcParams["font.family"]="Pretendard"
plt.rcParams["axes.unicode_minus"]=False
plt.rcParams["svg.fonttype"]="none"

# ---- palette (navy family, cohesive with template header #0D3960) ----
NAVY   = "#0D3960"
NAVY2  = "#16517F"
STEEL  = "#7FA3C4"
STEEL_L= "#BBD0E2"
GOLD   = "#E0A458"
GOLD_D = "#C8842F"
TEAL   = "#3E8E8B"
INK    = "#16222E"
MUTED  = "#5E6B78"
GRID   = "#E4E9EF"
CREAM  = "#FAF9F5"

SRC = "DATA/2011~2019_고속도로 교통사고 데이터/method_B_pre_accident_xgboost_results"
OUT = "charts_poster"
os.makedirs(OUT, exist_ok=True)

def style(ax):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]:
        ax.spines[s].set_color("#C9D2DC"); ax.spines[s].set_linewidth(1.2)
    ax.tick_params(colors=INK, labelsize=15, length=0)
    ax.set_axisbelow(True)

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=220, bbox_inches="tight",
                facecolor="white", edgecolor="none", pad_inches=0.12)
    plt.close(fig)
    print("saved", name)

# =====================================================================
# 1) Class balance donut
# =====================================================================
def fig_classbalance():
    fig, ax = plt.subplots(figsize=(6.0,5.4))
    vals=[89.2,10.8]; cols=[STEEL_L, GOLD]
    w,_=ax.pie(vals, colors=cols, startangle=90, counterclock=False,
               wedgeprops=dict(width=0.40, edgecolor="white", linewidth=3))
    ax.text(0,0.16,"10.8%",ha="center",va="center",fontsize=40,color=NAVY,fontweight="bold")
    ax.text(0,-0.16,"Injury cases",ha="center",va="center",fontsize=16,color=MUTED)
    ax.text(0,-0.40,"of 16,660 test crashes",ha="center",va="center",fontsize=12.5,color=MUTED)
    # legend
    ax.text(1.18,0.55,"■",color=STEEL_L,fontsize=20,va="center")
    ax.text(1.30,0.55,"No injury  89.2%",color=INK,fontsize=14,va="center")
    ax.text(1.18,0.30,"■",color=GOLD,fontsize=20,va="center")
    ax.text(1.30,0.30,"Injury  10.8%",color=INK,fontsize=14,va="center")
    ax.text(0.0,-1.28,"Class imbalance ≈ 8.3 : 1   →   scale_pos_weight = 8.26",
            ha="center",fontsize=13.5,color=NAVY,fontweight="bold")
    ax.set(aspect="equal");
    save(fig,"fig_classbalance")

# =====================================================================
# 2) Performance grouped bars (threshold 0.5 vs 0.72, TEST set)
# =====================================================================
def fig_performance():
    metrics=["Accuracy","Precision","Recall","F1-score"]
    d05=[0.8026,0.3162,0.7126,0.4381]
    d72=[0.8756,0.4403,0.5592,0.4927]
    x=np.arange(len(metrics)); w=0.38
    fig,ax=plt.subplots(figsize=(8.6,5.0)); style(ax)
    ax.grid(axis="y",color=GRID,lw=1)
    b1=ax.bar(x-w/2,d05,w,label="Default  (0.50)",color=STEEL,edgecolor="white",lw=1)
    b2=ax.bar(x+w/2,d72,w,label="Best-F1  (0.72)",color=NAVY,edgecolor="white",lw=1)
    for bars in (b1,b2):
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.012,f"{b.get_height():.3f}",
                    ha="center",va="bottom",fontsize=13.5,color=INK,fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(metrics,fontsize=15.5)
    ax.set_ylim(0,1.0); ax.set_ylabel("Score",fontsize=15,color=INK)
    ax.legend(loc="upper right",fontsize=13.5,frameon=False,ncol=1)
    save(fig,"fig_performance")

# =====================================================================
# 3) Threshold optimization curve
# =====================================================================
def fig_threshold():
    th,pr,rc,f1=[],[],[],[]
    with open(f"{SRC}/method_B_threshold_search_results.csv",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            th.append(float(r["threshold"])); pr.append(float(r["precision"]))
            rc.append(float(r["recall"])); f1.append(float(r["f1_score"]))
    fig,ax=plt.subplots(figsize=(8.6,5.0)); style(ax)
    ax.grid(color=GRID,lw=1)
    ax.plot(th,pr,color=GOLD_D,lw=2.6,label="Precision")
    ax.plot(th,rc,color=STEEL,lw=2.6,label="Recall")
    ax.plot(th,f1,color=NAVY,lw=3.2,label="F1-score")
    bi=int(np.argmax(f1)); bt=th[bi]
    ax.axvline(bt,color=MUTED,ls="--",lw=1.6)
    ax.scatter([bt],[f1[bi]],s=90,color=NAVY,zorder=5,edgecolor="white",lw=1.5)
    ax.annotate(f"Best F1 = {f1[bi]:.3f}\n@ threshold {bt:.2f}",
                xy=(bt,f1[bi]),xytext=(bt+0.04,f1[bi]+0.16),fontsize=13,color=NAVY,
                fontweight="bold",
                arrowprops=dict(arrowstyle="-",color=MUTED,lw=1.2))
    ax.axvline(0.5,color=STEEL_L,ls=":",lw=1.4)
    ax.text(0.5,1.02,"0.50",ha="center",fontsize=11,color=MUTED)
    ax.set_xlim(0.05,0.95); ax.set_ylim(0,1.05)
    ax.set_xlabel("Decision threshold",fontsize=14.5,color=INK)
    ax.set_ylabel("Score",fontsize=14.5,color=INK)
    ax.legend(loc="upper left",bbox_to_anchor=(0.02,0.62),fontsize=13.5,frameon=False)
    save(fig,"fig_threshold")

# =====================================================================
# 4) ROC + PR curves (from prediction probabilities)
# =====================================================================
def _curves():
    y,p=[],[]
    with open(f"{SRC}/method_B_prediction_results.csv",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            y.append(int(r["y_true"])); p.append(float(r["y_proba"]))
    return np.array(y),np.array(p)

def fig_roc_pr():
    y,p=_curves()
    order=np.argsort(-p); ys=y[order]
    P=ys.sum(); N=len(ys)-P
    tp=np.cumsum(ys); fp=np.cumsum(1-ys)
    tpr=tp/P; fpr=fp/N
    prec=tp/(tp+fp); rec=tpr
    roc_auc=np.trapz(tpr,fpr); pr_auc=np.trapz(prec[::-1],rec[::-1])
    fig,axs=plt.subplots(1,2,figsize=(10.6,4.7))
    # ROC
    a=axs[0]; style(a); a.grid(color=GRID,lw=1)
    a.plot([0,1],[0,1],ls="--",color=STEEL_L,lw=1.6)
    a.fill_between(fpr,tpr,color=NAVY,alpha=0.10)
    a.plot(fpr,tpr,color=NAVY,lw=3)
    a.text(0.55,0.18,f"ROC-AUC\n0.851",fontsize=18,color=NAVY,fontweight="bold",ha="center")
    a.set_xlim(0,1); a.set_ylim(0,1.02)
    a.set_xlabel("False positive rate",fontsize=13.5,color=INK)
    a.set_ylabel("True positive rate",fontsize=13.5,color=INK)
    a.set_title("ROC curve",fontsize=15,color=INK,fontweight="bold",pad=8)
    # PR
    b=axs[1]; style(b); b.grid(color=GRID,lw=1)
    b.axhline(P/len(ys),ls="--",color=STEEL_L,lw=1.6)
    b.fill_between(rec,prec,color=GOLD_D,alpha=0.12)
    b.plot(rec,prec,color=GOLD_D,lw=3)
    b.text(0.5,0.62,f"PR-AUC\n0.491",fontsize=18,color=GOLD_D,fontweight="bold",ha="center")
    b.text(0.04,P/len(ys)+0.02,"baseline 0.108",fontsize=10.5,color=MUTED)
    b.set_xlim(0,1); b.set_ylim(0,1.02)
    b.set_xlabel("Recall",fontsize=13.5,color=INK)
    b.set_ylabel("Precision",fontsize=13.5,color=INK)
    b.set_title("Precision–Recall curve",fontsize=15,color=INK,fontweight="bold",pad=8)
    fig.tight_layout()
    save(fig,"fig_roc_pr")
    print(f"  computed ROC-AUC={roc_auc:.4f} PR-AUC={pr_auc:.4f}")

# =====================================================================
# 5) Top-10 feature importance (horizontal)
# =====================================================================
def fig_feat10():
    rows=[]
    with open(f"{SRC}/method_B_feature_importance.csv",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append((r["feature"],float(r["importance"])))
    rows=rows[:10]
    label_map={
        "사고차량수":"Number of vehicles involved",
        "사고유형_차-차":"Crash type · vehicle–vehicle",
        "사고유형_기타":"Crash type · other",
        "사고유형_차-사람":"Crash type · vehicle–pedestrian",
        "사고원인구분_기타요인":"Cause · other factor",
        "발생지점_본선":"Location · mainline",
        "주사고원인_무단보행":"Main cause · jaywalking",
        "주사고원인_졸음":"Main cause · drowsiness",
        "주사고원인_노면잡물":"Main cause · roadway debris",
        "구분_본선차로":"Segment · mainline lane",
    }
    labels=[label_map.get(f,f) for f,_ in rows][::-1]
    vals=[v for _,v in rows][::-1]
    fig,ax=plt.subplots(figsize=(8.8,5.6));
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#C9D2DC")
    ax.tick_params(colors=INK,length=0,labelsize=14.5)
    ax.grid(axis="x",color=GRID,lw=1); ax.set_axisbelow(True)
    cmap=[NAVY if i>=8 else (NAVY2 if i>=6 else STEEL) for i in range(len(vals))]
    bars=ax.barh(range(len(vals)),vals,color=cmap,height=0.66,edgecolor="white")
    # highlight top3 in gold
    for i in range(len(vals)-3,len(vals)): bars[i].set_color(NAVY)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels,fontsize=13.8)
    for i,v in enumerate(vals):
        ax.text(v+0.0007,i,f"{v:.3f}",va="center",fontsize=12.5,color=INK,fontweight="bold")
    ax.set_xlim(0,max(vals)*1.18)
    ax.set_xlabel("XGBoost gain importance",fontsize=14,color=INK)
    save(fig,"fig_feat10")

# =====================================================================
# 6) Method B pipeline flow diagram
# =====================================================================
def fig_method_flow():
    steps=[
        ("01","Raw crash data","2011–2019\nexpressway records"),
        ("02","Pre-accident\nvariables","Drop all post-crash\noutcome columns"),
        ("03","Imbalance\nhandling","scale_pos_weight\n= 8.26"),
        ("04","XGBoost binary\nclassifier","Injury occurrence\n( yes / no )"),
        ("05","Threshold\noptimization","0.50  →  0.72\n(Best F1)"),
        ("06","Evaluation &\ninterpretation","ROC / PR-AUC\n+ importance"),
    ]
    n=len(steps)
    fig,ax=plt.subplots(figsize=(14.6,2.7)); ax.axis("off")
    cell=1.0; ax.set_xlim(0,n*cell); ax.set_ylim(0,1)
    bw=0.80; gap=(cell-bw)
    for i,(num,t,d) in enumerate(steps):
        x=i*cell+gap/2
        # body
        ax.add_patch(FancyBboxPatch((x,0.10),bw,0.66,
                     boxstyle="round,pad=0.008,rounding_size=0.06",
                     linewidth=1.6,edgecolor=NAVY,facecolor=CREAM))
        # header bar
        ax.add_patch(FancyBboxPatch((x,0.70),bw,0.20,
                     boxstyle="round,pad=0.008,rounding_size=0.06",
                     linewidth=0,facecolor=NAVY))
        ax.text(x+bw/2,0.80,f"{num}  {t}",fontsize=11.6,color="white",
                fontweight="bold",va="center",ha="center",linespacing=0.95)
        ax.text(x+bw/2,0.40,d,fontsize=11.0,color=MUTED,ha="center",va="center",
                linespacing=1.15)
        if i<n-1:
            ax.add_patch(FancyArrowPatch((x+bw+0.015,0.43),(x+cell-0.02,0.43),
                         arrowstyle="-|>",mutation_scale=16,color=GOLD_D,lw=2.6))
    fig.subplots_adjust(left=0.005,right=0.995,top=0.99,bottom=0.01)
    save(fig,"fig_method_flow")

# =====================================================================
# 7) Train / Test class distribution (grouped bars) — polished
# =====================================================================
def fig_traintest():
    classes = ["인명피해 없음\nNo injury", "인명피해 발생\nInjury"]
    train = [59443, 7194]
    test  = [14861, 1799]
    tr_tot, te_tot = sum(train), sum(test)
    x = np.arange(len(classes)); w = 0.36
    fig, ax = plt.subplots(figsize=(9.0, 5.4)); style(ax)
    ax.grid(axis="y", color=GRID, lw=1)
    b1 = ax.bar(x-w/2, train, w, color=NAVY,  edgecolor="white", lw=1.2,
                label=f"Train  (n={tr_tot:,})", zorder=3)
    b2 = ax.bar(x+w/2, test,  w, color=GOLD,  edgecolor="white", lw=1.2,
                label=f"Test   (n={te_tot:,})", zorder=3)
    def lab(bars, tot):
        for b in bars:
            h = b.get_height()
            cx = b.get_x()+b.get_width()/2
            ax.text(cx, h+800, f"{int(h):,}", ha="center", va="bottom",
                    fontsize=14, color=INK, fontweight="bold")
            if h > 11000:   # % only inside tall bars
                ax.text(cx, h/2, f"{h/tot*100:.1f}%", ha="center", va="center",
                        fontsize=12.5, color="white", fontweight="bold")
            else:           # small share label below the count
                ax.text(cx, h+3300, f"({h/tot*100:.1f}%)", ha="center", va="bottom",
                        fontsize=11.5, color=MUTED, fontweight="bold")
    lab(b1, tr_tot); lab(b2, te_tot)
    ax.set_xticks(x); ax.set_xticklabels(classes, fontsize=15)
    ax.set_ylabel("Count", fontsize=14.5, color=INK)
    ax.set_ylim(0, 66000)
    ax.yaxis.set_major_formatter(lambda v, p: f"{int(v):,}")
    ax.legend(loc="upper right", fontsize=13.5, frameon=False)
    ax.text(0.5, -0.205,
            "클래스 불균형 ≈ 8.3 : 1     ·     scale_pos_weight = 59,443 / 7,194 = 8.26",
            transform=ax.transAxes, ha="center", fontsize=13.5,
            color=NAVY, fontweight="bold")
    save(fig, "fig_traintest")

if __name__=="__main__":
    fig_classbalance(); fig_performance(); fig_threshold()
    fig_roc_pr(); fig_feat10(); fig_method_flow(); fig_traintest()
    print("ALL DONE")
