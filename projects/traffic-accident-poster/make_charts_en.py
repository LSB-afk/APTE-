# -*- coding: utf-8 -*-
"""English charts for APTE 2026 poster — XGBoost-SHAP injury-occurrence factor analysis.
All numbers from outputs/injury_severity_shap_analysis (the new SHAP run)."""
import os, csv
import numpy as np, pandas as pd
import scipy.sparse as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FROOT="/Users/leeseungbo/Library/Fonts"
for f in ["Pretendard-Regular.ttf","Pretendard-Medium.ttf","Pretendard-SemiBold.ttf","Pretendard-Bold.ttf"]:
    p=os.path.join(FROOT,f)
    if os.path.exists(p): fm.fontManager.addfont(p)
plt.rcParams["font.family"]="Pretendard"; plt.rcParams["axes.unicode_minus"]=False

NAVY="#0D3960"; NAVY2="#16517F"; STEEL="#7FA3C4"; STEEL_L="#BBD0E2"
GOLD="#E0A458"; GOLD_D="#C8842F"; INK="#16222E"; MUTED="#5E6B78"; GRID="#E4E9EF"; CREAM="#FAF9F5"

RES="/Users/leeseungbo/Desktop/APTE_교통사고_데이터/outputs/injury_severity_shap_analysis"
PRE="/Users/leeseungbo/Desktop/APTE_교통사고_데이터/DATA/2011~2019_고속도로 교통사고 데이터/preprocessed_xgboost_injury_occurrence"
OUT="charts_en"; os.makedirs(OUT,exist_ok=True)

def style(ax):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color("#C9D2DC"); ax.spines[s].set_linewidth(1.2)
    ax.tick_params(colors=INK,labelsize=15,length=0); ax.set_axisbelow(True)
def save(fig,name,dpi=220):
    fig.savefig(f"{OUT}/{name}.png",dpi=dpi,bbox_inches="tight",facecolor="white",pad_inches=0.12)
    plt.close(fig); print("saved",name)

# ---------------- KO -> EN feature translation ----------------
BASE={'사고유형':'Crash type','주사고원인':'Main cause','사고원인구분':'Cause category',
 '사고직전차량조작':'Pre-crash maneuver','사고시도로환경':'Road environment','평면선형':'Alignment',
 '선형구분':'Alignment type','차로':'Lane','방향':'Direction','날씨':'Weather','성별':'Driver sex',
 '원인차운전자연령구분':'Driver age group','절성토구분':'Cut/fill','발생지점':'Location','구분':'Segment',
 '노면상태':'Road surface','조명시설':'Lighting','포장구분':'Pavement','포장상태':'Pavement cond.',
 '운전자상태':'Driver state','교통장애요인':'Traffic obstacle','원인차차종':'At-fault vehicle',
 '차종구분1':'Vehicle class','차종구분2':'Vehicle class2','차종규격':'Vehicle size','주야구분':'Day/Night',
 '요일':'Day of week','지사명':'Branch','노선명':'Route','이정':'Milepost','사고시간':'Crash time'}
NUM={'운전시간':'Driving time (h)','사고차량수':'No. of vehicles','운전거리km':'Driving distance (km)',
 '사고전차량통행속도':'Pre-crash speed','accident_hour':'Hour of day','accident_month':'Month',
 'accident_weekday_num':'Weekday','accident_year':'Year','accident_day':'Day','accident_time_band':'Time band'}
CAT={'차-차':'vehicle–vehicle','차-사람':'vehicle–pedestrian','차-시설':'vehicle–facility','차-열차':'vehicle–train',
 '기타':'other','졸음':'drowsiness','노면잡물':'roadway debris','무단보행':'jaywalking','과속':'speeding',
 '단독차량화재':'single-vehicle fire','핸들과대조작':'steering overcorrection','포트홀':'pothole',
 '우커브':'right curve','좌커브':'left curve','직선':'straight','갓길':'shoulder','눈':'snow','비':'rain','맑음':'clear',
 '여자':'female','남자':'male','본선':'mainline','본선차로':'mainline lane','터널':'tunnel','TG(TCS)':'tollgate',
 '기타요인':'other factor','운전자요인':'driver factor','질병':'illness','타이어파손':'tire blowout',
 '서창':'Seochang','완주':'Wanju','대구지사':'Daegu','부여지사':'Buyeo','구례지사':'Gurye',
 '절토부 10M 미만':'cut slope <10m','0.0':'unknown','':'unspecified',' ':'unspecified'}
def tr(name):
    name=str(name).strip()
    if name in NUM: return NUM[name]
    if '_' in name:
        i=name.rfind('_'); b,c=name[:i],name[i+1:]
        return f"{BASE.get(b,b)}: {CAT.get(c, c.strip() or 'unspecified')}"
    return BASE.get(name, NUM.get(name, name))

# ============================================================
# 1) Train/Test class distribution
# ============================================================
def fig_traintest():
    classes=["No injury","Injury"]; train=[59443,7194]; test=[14861,1799]
    trt,tet=sum(train),sum(test); x=np.arange(2); w=0.36
    fig,ax=plt.subplots(figsize=(9.0,5.4)); style(ax); ax.grid(axis="y",color=GRID,lw=1)
    b1=ax.bar(x-w/2,train,w,color=NAVY,edgecolor="white",lw=1.2,label=f"Train  (n={trt:,})",zorder=3)
    b2=ax.bar(x+w/2,test,w,color=GOLD,edgecolor="white",lw=1.2,label=f"Test   (n={tet:,})",zorder=3)
    def lab(bars,tot):
        for b in bars:
            h=b.get_height(); cx=b.get_x()+b.get_width()/2
            ax.text(cx,h+800,f"{int(h):,}",ha="center",va="bottom",fontsize=14,color=INK,fontweight="bold")
            if h>11000: ax.text(cx,h/2,f"{h/tot*100:.1f}%",ha="center",va="center",fontsize=12.5,color="white",fontweight="bold")
            else: ax.text(cx,h+3300,f"({h/tot*100:.1f}%)",ha="center",va="bottom",fontsize=11.5,color=MUTED,fontweight="bold")
    lab(b1,trt); lab(b2,tet)
    ax.set_xticks(x); ax.set_xticklabels(classes,fontsize=15.5); ax.set_ylabel("Count",fontsize=14.5,color=INK)
    ax.set_ylim(0,66000); ax.yaxis.set_major_formatter(lambda v,p:f"{int(v):,}")
    ax.legend(loc="upper right",fontsize=13.5,frameon=False)
    ax.text(0.5,-0.205,"Class imbalance ≈ 8.3 : 1     ·     scale_pos_weight = 59,443 / 7,194 = 8.26",
            transform=ax.transAxes,ha="center",fontsize=13.5,color=NAVY,fontweight="bold")
    save(fig,"fig_en_traintest")

# ============================================================
# 2) Performance: Default 0.50 vs Selected 0.65
# ============================================================
def fig_performance():
    metrics=["Accuracy","Precision","Recall","F1-score"]
    d05=[0.8477,0.3771,0.6292,0.4716]; d65=[0.8856,0.4729,0.5181,0.4944]
    x=np.arange(4); w=0.38
    fig,ax=plt.subplots(figsize=(8.8,5.0)); style(ax); ax.grid(axis="y",color=GRID,lw=1)
    b1=ax.bar(x-w/2,d05,w,label="Default  (0.50)",color=STEEL,edgecolor="white")
    b2=ax.bar(x+w/2,d65,w,label="Selected  (0.65)",color=NAVY,edgecolor="white")
    for bars in (b1,b2):
        for b in bars: ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.012,f"{b.get_height():.3f}",
                               ha="center",va="bottom",fontsize=13.5,color=INK,fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(metrics,fontsize=15.5); ax.set_ylim(0,1.0)
    ax.set_ylabel("Score",fontsize=15,color=INK); ax.legend(loc="upper right",fontsize=13.5,frameon=False)
    save(fig,"fig_en_performance")

# ============================================================
# 3) Threshold curve
# ============================================================
def fig_threshold():
    df=pd.read_csv(f"{RES}/xgboost_threshold_results.csv")
    fig,ax=plt.subplots(figsize=(8.6,5.0)); style(ax); ax.grid(color=GRID,lw=1)
    ax.plot(df.threshold,df.precision,color=GOLD_D,lw=2.6,label="Precision")
    ax.plot(df.threshold,df.recall,color=STEEL,lw=2.6,label="Recall")
    ax.plot(df.threshold,df.f1_score,color=NAVY,lw=3.2,label="F1-score")
    bi=df.f1_score.idxmax(); bt=df.threshold[bi]
    ax.axvline(bt,color=MUTED,ls="--",lw=1.6)
    ax.scatter([bt],[df.f1_score[bi]],s=90,color=NAVY,zorder=5,edgecolor="white",lw=1.5)
    ax.annotate(f"Best F1 = {df.f1_score[bi]:.3f}\n@ threshold {bt:.2f}",xy=(bt,df.f1_score[bi]),
                xytext=(bt-0.34,df.f1_score[bi]+0.16),fontsize=13,color=NAVY,fontweight="bold",
                arrowprops=dict(arrowstyle="-",color=MUTED,lw=1.2))
    ax.axvline(0.5,color=STEEL_L,ls=":",lw=1.4); ax.text(0.5,1.02,"0.50",ha="center",fontsize=11,color=MUTED)
    ax.set_xlim(0.05,0.95); ax.set_ylim(0,1.05)
    ax.set_xlabel("Decision threshold",fontsize=14.5,color=INK); ax.set_ylabel("Score",fontsize=14.5,color=INK)
    ax.legend(loc="upper left",bbox_to_anchor=(0.02,0.62),fontsize=13.5,frameon=False)
    save(fig,"fig_en_threshold")

# ============================================================
# 4) ROC + PR
# ============================================================
def fig_roc_pr():
    d=pd.read_csv(f"{RES}/xgboost_prediction_results.csv"); y=d.y_true.values; p=d.y_proba.values
    from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score, average_precision_score
    fpr,tpr,_=roc_curve(y,p); prec,rec,_=precision_recall_curve(y,p)
    ra=roc_auc_score(y,p); pa=average_precision_score(y,p); base=y.mean()
    fig,axs=plt.subplots(1,2,figsize=(10.6,4.7))
    a=axs[0]; style(a); a.grid(color=GRID,lw=1); a.plot([0,1],[0,1],ls="--",color=STEEL_L,lw=1.6)
    a.fill_between(fpr,tpr,color=NAVY,alpha=0.10); a.plot(fpr,tpr,color=NAVY,lw=3)
    a.text(0.55,0.18,f"ROC-AUC\n{ra:.3f}",fontsize=18,color=NAVY,fontweight="bold",ha="center")
    a.set_xlim(0,1); a.set_ylim(0,1.02); a.set_xlabel("False positive rate",fontsize=13.5,color=INK)
    a.set_ylabel("True positive rate",fontsize=13.5,color=INK); a.set_title("ROC curve",fontsize=15,fontweight="bold",pad=8)
    b=axs[1]; style(b); b.grid(color=GRID,lw=1); b.axhline(base,ls="--",color=STEEL_L,lw=1.6)
    b.fill_between(rec,prec,color=GOLD_D,alpha=0.12); b.plot(rec,prec,color=GOLD_D,lw=3)
    b.text(0.5,0.62,f"PR-AUC\n{pa:.3f}",fontsize=18,color=GOLD_D,fontweight="bold",ha="center")
    b.text(0.04,base+0.02,f"baseline {base:.3f}",fontsize=10.5,color=MUTED)
    b.set_xlim(0,1); b.set_ylim(0,1.02); b.set_xlabel("Recall",fontsize=13.5,color=INK)
    b.set_ylabel("Precision",fontsize=13.5,color=INK); b.set_title("Precision–Recall curve",fontsize=15,fontweight="bold",pad=8)
    fig.tight_layout(); save(fig,"fig_en_roc_pr")

# ============================================================
# 5) Gain feature importance top-12 (English)
# ============================================================
def fig_importance():
    g=pd.read_csv(f"{RES}/xgboost_feature_importance_gain.csv").head(12).copy()
    g["en"]=g.feature.map(tr); d=g.iloc[::-1]
    fig,ax=plt.subplots(figsize=(8.8,5.8))
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#C9D2DC"); ax.tick_params(colors=INK,length=0,labelsize=13.5)
    ax.grid(axis="x",color=GRID,lw=1); ax.set_axisbelow(True)
    cmap=[NAVY if i>=9 else (NAVY2 if i>=6 else STEEL) for i in range(len(d))]
    ax.barh(range(len(d)),d.gain,color=cmap,height=0.7,edgecolor="white")
    ax.set_yticks(range(len(d))); ax.set_yticklabels(d.en,fontsize=13)
    for i,v in enumerate(d.gain): ax.text(v+8,i,f"{v:.0f}",va="center",fontsize=12,color=INK,fontweight="bold")
    ax.set_xlim(0,max(d.gain)*1.16); ax.set_xlabel("XGBoost gain importance",fontsize=14,color=INK)
    save(fig,"fig_en_importance")

# ============================================================
# 6) SHAP directional bar (risk up/down) top-12 actionable (English)
# ============================================================
def fig_shap_factors():
    s=pd.read_csv(f"{RES}/shap_importance_top30_actionable.csv").head(12).copy()
    s["en"]=s.feature.map(tr); d=s.iloc[::-1]
    fig,ax=plt.subplots(figsize=(9.2,5.9))
    for ss in ["top","right","left"]: ax.spines[ss].set_visible(False)
    ax.spines["bottom"].set_color("#C9D2DC"); ax.tick_params(colors=INK,length=0,labelsize=13.5)
    ax.grid(axis="x",color=GRID,lw=1); ax.set_axisbelow(True)
    cols=[GOLD if v>0 else STEEL for v in d.signed_impact]
    ax.barh(range(len(d)),d.mean_abs_shap,color=cols,height=0.72,edgecolor="white")
    ax.set_yticks(range(len(d))); ax.set_yticklabels(d.en,fontsize=12.5)
    ax.set_xlabel("mean |SHAP value|",fontsize=14,color=INK)
    ax.set_title("Gold = raises injury risk    ·    Blue = lowers injury risk",fontsize=13,color=MUTED,pad=8)
    save(fig,"fig_en_shap_factors")

# ============================================================
# 7) SHAP beeswarm (top-12 actionable, English) — reconstruct sample
# ============================================================
def fig_shap_beeswarm():
    import shap
    # rebuild keep_names (same leak filter as analysis)
    LEAK=["현장도착소요시간","구급차도착소요시간","인명구조소요시간","견인차도착소요시간","구난소요시간",
          "전면통제시간","부분통제시간","교통차단시간","사고처리시간","사고후상태","차량상태","도로점유","대향차로",
          "피해자_차종","피해차운전자연령구분","target_","사망자수","중상자수","경상자수","부상심각도","부상 심각도",
          "severity","injury_severity","사망","중상","경상"]
    def leak(n): return any(n==k or n.startswith(k) for k in LEAK)
    with open(f"{PRE}/X_train_processed.csv",encoding="utf-8-sig") as f: header=next(csv.reader(f))
    keep_names=[h for h in header if not leak(h)]
    name2col={n:i for i,n in enumerate(keep_names)}
    # top-12 actionable features + their column indices
    act=pd.read_csv(f"{RES}/shap_importance_top30_actionable.csv").head(12)
    feats=[f for f in act.feature if f in name2col]
    cols=[name2col[f] for f in feats]
    # load shap values, subset columns
    sv=np.load(f"{RES}/shap_values_sample.npy")[:,cols]
    # reproduce sample rows from X_test (seed 42, same as analysis)
    n_test=16660; idx=np.random.RandomState(42).choice(n_test,min(3000,n_test),replace=False)
    Xt=pd.read_csv(f"{PRE}/X_test_processed.csv",usecols=feats,encoding="utf-8-sig")[feats]
    Xs=Xt.iloc[idx].reset_index(drop=True)
    # sanity: mean|shap| should match CSV
    chk=np.abs(sv).mean(0)
    Xs_en=Xs.copy(); Xs_en.columns=[tr(f) for f in feats]
    plt.figure()
    shap.summary_plot(sv, Xs_en, max_display=12, show=False, plot_size=(9.2,6.2), sort=True)
    fig=plt.gcf(); fig.suptitle("SHAP summary (beeswarm) · injury occurrence",fontsize=14,fontweight="bold",y=1.02)
    plt.tight_layout(); fig.savefig(f"{OUT}/fig_en_shap_beeswarm.png",dpi=220,bbox_inches="tight",facecolor="white"); plt.close()
    print("saved fig_en_shap_beeswarm  (check mean|shap| top:",dict(zip([tr(f) for f in feats[:3]],chk[:3].round(3))),")")

# ============================================================
# 8) Confusion matrix (English, thr 0.65)
# ============================================================
def fig_confusion():
    cm=np.array([[13822,1039],[867,932]])
    fig,ax=plt.subplots(figsize=(5.2,4.6)); im=ax.imshow(cm,cmap="Blues")
    labels=[["TN","FP"],["FN","TP"]]
    for (i,j),v in np.ndenumerate(cm):
        ax.text(j,i,f"{labels[i][j]}\n{v:,}",ha="center",va="center",fontsize=15,
                color="white" if v>cm.max()/2 else INK,fontweight="bold")
    ax.set_xticks([0,1]); ax.set_xticklabels(["No injury","Injury"],fontsize=12)
    ax.set_yticks([0,1]); ax.set_yticklabels(["No injury","Injury"],fontsize=12)
    ax.set_xlabel("Predicted",fontsize=13); ax.set_ylabel("Actual",fontsize=13)
    ax.set_title("Confusion matrix (threshold 0.65)",fontsize=13.5,fontweight="bold",pad=8)
    save(fig,"fig_en_confusion",dpi=240)

# ============================================================
# 9) Method flow (English)
# ============================================================
def fig_method_flow():
    steps=[("01","Crash data","2011–2019\nexpressway"),
           ("02","Pre-accident\nfeatures","Remove post-crash\nleakage cols"),
           ("03","Imbalance\nhandling","scale_pos_weight\n= 8.26"),
           ("04","XGBoost\nclassifier","Injury occurrence\n( yes / no )"),
           ("05","Threshold\noptimization","0.50  →  0.65"),
           ("06","SHAP\ninterpretation","Risk factors\n& direction")]
    n=len(steps); fig,ax=plt.subplots(figsize=(14.6,2.7)); ax.axis("off")
    cell=1.0; ax.set_xlim(0,n*cell); ax.set_ylim(0,1); bw=0.80; gap=cell-bw
    for i,(num,t,d) in enumerate(steps):
        x=i*cell+gap/2
        ax.add_patch(FancyBboxPatch((x,0.10),bw,0.66,boxstyle="round,pad=0.008,rounding_size=0.06",lw=1.6,edgecolor=NAVY,facecolor=CREAM))
        ax.add_patch(FancyBboxPatch((x,0.70),bw,0.20,boxstyle="round,pad=0.008,rounding_size=0.06",lw=0,facecolor=NAVY))
        ax.text(x+bw/2,0.80,f"{num}  {t}",fontsize=11.4,color="white",fontweight="bold",va="center",ha="center",linespacing=0.95)
        ax.text(x+bw/2,0.40,d,fontsize=11.0,color=MUTED,ha="center",va="center",linespacing=1.15)
        if i<n-1: ax.add_patch(FancyArrowPatch((x+bw+0.015,0.43),(x+cell-0.02,0.43),arrowstyle="-|>",mutation_scale=16,color=GOLD_D,lw=2.6))
    fig.subplots_adjust(left=0.005,right=0.995,top=0.99,bottom=0.01); save(fig,"fig_en_method_flow")

if __name__=="__main__":
    fig_traintest(); fig_performance(); fig_threshold(); fig_roc_pr()
    fig_importance(); fig_shap_factors(); fig_confusion(); fig_method_flow()
    fig_shap_beeswarm()
    print("ALL EN CHARTS DONE")
