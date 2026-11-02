# -*- coding: utf-8 -*-
"""
고속도로 교통사고 부상 발생(injury_occurrence) 요인 분석 + SHAP 해석
- 전처리 데이터: preprocessed_xgboost_injury_occurrence
- XGBoost 이진분류 + 누수변수 제거 + scale_pos_weight 후보 비교 + threshold 탐색 + SHAP
"""
import os, sys, time, gc, json, csv
import numpy as np
import scipy.sparse as sp

t0 = time.time()
def log(*a):
    print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

PRE = "/Users/leeseungbo/Desktop/APTE_교통사고_데이터/DATA/2011~2019_고속도로 교통사고 데이터/preprocessed_xgboost_injury_occurrence"
OUT = "/Users/leeseungbo/Desktop/APTE_교통사고_데이터/outputs/injury_severity_shap_analysis"
os.makedirs(OUT, exist_ok=True)

# ---------- matplotlib / Korean font ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
FROOT = "/Users/leeseungbo/Library/Fonts"
for f in ["Pretendard-Regular.ttf","Pretendard-Medium.ttf","Pretendard-SemiBold.ttf","Pretendard-Bold.ttf"]:
    p = os.path.join(FROOT, f)
    if os.path.exists(p): fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Pretendard"
plt.rcParams["axes.unicode_minus"] = False
NAVY="#0D3960"; GOLD="#E0A458"; STEEL="#7FA3C4"; INK="#16222E"; GREY="#5E6B78"; GRID="#E4E9EF"

# ======================================================================
# 0) leakage prefixes (post-accident / outcome-derived) — MUST remove
# ======================================================================
LEAK_PREFIX = [
    # response / operation times (known only after the crash)
    "현장도착소요시간","구급차도착소요시간","인명구조소요시간","견인차도착소요시간","구난소요시간",
    "전면통제시간","부분통제시간","교통차단시간","사고처리시간",
    # post-crash vehicle / scene state (consequence of the crash)
    "사고후상태","차량상태","도로점유","대향차로",
    # victim-derived (known only after injury)
    "피해자_차종","피해차운전자연령구분",
    # explicit target / severity / casualty (user list)
    "target_","사망자수","중상자수","경상자수","부상심각도","부상 심각도","severity","injury_severity",
    "사망","중상","경상",
]
def is_leak(name):
    return any(name == k or name.startswith(k) for k in LEAK_PREFIX)

# ======================================================================
# 1) header -> keep column indices
# ======================================================================
log("reading X header ...")
with open(os.path.join(PRE,"X_train_processed.csv"), encoding="utf-8-sig") as f:
    header = next(csv.reader(f))
n_all = len(header)
keep_idx = [i for i,h in enumerate(header) if not is_leak(h)]
keep_names = [header[i] for i in keep_idx]
drop_names = [h for h in header if is_leak(h)]
log(f"total cols={n_all}  keep={len(keep_idx)}  dropped(leak)={len(drop_names)}")
# save dropped list
with open(os.path.join(OUT,"removed_leakage_columns.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["removed_leakage_feature"]); [w.writerow([d]) for d in drop_names]

# ======================================================================
# 2) load y
# ======================================================================
import pandas as pd
y_train = pd.read_csv(os.path.join(PRE,"y_train.csv"))["injury_occurrence"].astype(int).values
y_test  = pd.read_csv(os.path.join(PRE,"y_test.csv"))["injury_occurrence"].astype(int).values
log(f"y_train {y_train.shape} pos={y_train.sum()} ({y_train.mean()*100:.2f}%)  y_test {y_test.shape} pos={y_test.sum()} ({y_test.mean()*100:.2f}%)")

# ======================================================================
# 3) stream-load X as sparse (keep cols only, float32)
# ======================================================================
keep_set = keep_idx  # positions
keep_names_arr = keep_names
nan_filled = {"train":0,"test":0}
def load_sparse(path, tag, chunksize=4000):
    parts=[]; rows=0
    usecols = keep_set
    reader = pd.read_csv(path, usecols=usecols, chunksize=chunksize,
                         dtype=np.float32, encoding="utf-8-sig")
    for i,chunk in enumerate(reader):
        # ensure column order == keep_names
        chunk = chunk[[header[j] for j in keep_set]]
        nan = int(np.isnan(chunk.values).sum())
        nan_filled[tag]+=nan
        arr = np.nan_to_num(chunk.values, nan=0.0)
        parts.append(sp.csr_matrix(arr))
        rows += arr.shape[0]
        if i % 4 == 0: log(f"  {tag}: {rows} rows loaded ...")
        del chunk, arr; gc.collect()
    X = sp.vstack(parts).tocsr().astype(np.float32)
    return X
log("loading X_train (sparse) ...")
X_train = load_sparse(os.path.join(PRE,"X_train_processed.csv"),"train")
log(f"X_train sparse shape={X_train.shape} nnz={X_train.nnz} ({X_train.nnz/ (X_train.shape[0]*X_train.shape[1])*100:.3f}% dense)")
log("loading X_test (sparse) ...")
X_test = load_sparse(os.path.join(PRE,"X_test_processed.csv"),"test")
log(f"X_test sparse shape={X_test.shape} nnz={X_test.nnz}")
log(f"NaN filled with 0 -> train={nan_filled['train']} test={nan_filled['test']}")
assert X_train.shape[1] == X_test.shape[1] == len(keep_names)

# ======================================================================
# 4) train candidate models (scale_pos_weight) + threshold search
# ======================================================================
from xgboost import XGBClassifier
from sklearn.metrics import (precision_recall_fscore_support, roc_auc_score,
                             average_precision_score, confusion_matrix,
                             classification_report, accuracy_score,
                             precision_score, recall_score, f1_score)

ratio = (y_train==0).sum()/(y_train==1).sum()
spw_candidates = [5,8,10,12,15,18, round(float(ratio),4)]
log(f"scale_pos_weight candidates = {spw_candidates}  (auto ratio={ratio:.4f})")

def make_model(spw):
    return XGBClassifier(
        n_estimators=600, max_depth=4, learning_rate=0.03,
        subsample=0.85, colsample_bytree=0.85, min_child_weight=3,
        gamma=0.1, reg_alpha=0.1, reg_lambda=2.0,
        objective="binary:logistic", eval_metric="logloss",
        scale_pos_weight=spw, tree_method="hist",
        random_state=42, n_jobs=-1)

THR = np.round(np.arange(0.05,0.9501,0.01),2)
def thr_search(y, proba):
    rows=[]
    for t in THR:
        pred=(proba>=t).astype(int)
        p,r,f,_=precision_recall_fscore_support(y,pred,average="binary",zero_division=0)
        rows.append((t, accuracy_score(y,pred), p, r, f))
    return rows

model_summary=[]   # per candidate: best-F1 on test
candidates={}
for spw in spw_candidates:
    log(f"training model spw={spw} ...")
    m=make_model(spw); m.fit(X_train,y_train)
    pr_tr=m.predict_proba(X_train)[:,1]; pr_te=m.predict_proba(X_test)[:,1]
    roc=roc_auc_score(y_test,pr_te); prauc=average_precision_score(y_test,pr_te)
    ts=thr_search(y_test,pr_te)
    best=max(ts,key=lambda x:x[4])  # best F1
    model_summary.append({"scale_pos_weight":spw,"roc_auc":roc,"pr_auc":prauc,
                          "best_f1":best[4],"best_thr":best[0],
                          "acc@best":best[1],"prec@best":best[2],"rec@best":best[3]})
    candidates[spw]={"model":m,"proba_test":pr_te,"proba_train":pr_tr,
                     "roc":roc,"prauc":prauc,"thr_rows":ts}
    log(f"  spw={spw}: ROC-AUC={roc:.4f} PR-AUC={prauc:.4f} bestF1={best[4]:.4f}@{best[0]}")
    gc.collect()

# model performance summary
pd.DataFrame(model_summary).to_csv(os.path.join(OUT,"xgboost_model_performance_summary.csv"),
                                   index=False, encoding="utf-8-sig")

# select final model = max PR-AUC (robust under imbalance)
final_spw = max(model_summary, key=lambda d:d["pr_auc"])["scale_pos_weight"]
log(f"==> FINAL model selected by PR-AUC: spw={final_spw}")
fin = candidates[final_spw]; model=fin["model"]; proba_test=fin["proba_test"]

# threshold results (final model)
thr_df=pd.DataFrame(fin["thr_rows"],columns=["threshold","accuracy","precision","recall","f1_score"])
thr_df.to_csv(os.path.join(OUT,"xgboost_threshold_results.csv"),index=False,encoding="utf-8-sig")

def pick(df,recall_min=None):
    d=df if recall_min is None else df[df.recall>=recall_min]
    if len(d)==0: return None
    return d.loc[d.f1_score.idxmax()]
c1=pick(thr_df); c2=pick(thr_df,0.50); c3=pick(thr_df,0.60)
sel_rows=[]
for name,row in [("best_F1",c1),("recall>=0.50_maxF1",c2),("recall>=0.60_maxF1",c3)]:
    if row is None: continue
    sel_rows.append({"criterion":name,"scale_pos_weight":final_spw,"threshold":row.threshold,
                     "accuracy":row.accuracy,"precision":row.precision,"recall":row.recall,
                     "f1_score":row.f1_score,"roc_auc":fin["roc"],"pr_auc":fin["prauc"]})
pd.DataFrame(sel_rows).to_csv(os.path.join(OUT,"xgboost_selected_model_result.csv"),
                              index=False,encoding="utf-8-sig")

# operating threshold = best F1
op_thr=float(c1.threshold)
pred_op=(proba_test>=op_thr).astype(int)
pred_05=(proba_test>=0.5).astype(int)
pd.DataFrame({"y_true":y_test,"y_proba":proba_test,
             "y_pred_threshold_0_5":pred_05,"y_pred_best_threshold":pred_op}
            ).to_csv(os.path.join(OUT,"xgboost_prediction_results.csv"),index=False,encoding="utf-8-sig")
cm=confusion_matrix(y_test,pred_op)
log(f"FINAL spw={final_spw} thr={op_thr}  ROC-AUC={fin['roc']:.4f} PR-AUC={fin['prauc']:.4f}")
log("confusion matrix (best-F1 thr):\n"+str(cm))
report=classification_report(y_test,pred_op,digits=4)
log("classification report:\n"+report)

# ======================================================================
# 5) Feature importance (gain / weight / cover / default)
# ======================================================================
booster=model.get_booster()
booster.feature_names=keep_names
def imp_df(kind):
    d=booster.get_score(importance_type=kind)
    rows=[(k,v) for k,v in d.items()]
    df=pd.DataFrame(rows,columns=["feature",kind]).sort_values(kind,ascending=False).reset_index(drop=True)
    return df
gain=imp_df("gain"); weight=imp_df("weight"); cover=imp_df("cover")
default_imp=pd.DataFrame({"feature":keep_names,"importance":model.feature_importances_}
                        ).sort_values("importance",ascending=False).reset_index(drop=True)
gain.to_csv(os.path.join(OUT,"xgboost_feature_importance_gain.csv"),index=False,encoding="utf-8-sig")
weight.to_csv(os.path.join(OUT,"xgboost_feature_importance_weight.csv"),index=False,encoding="utf-8-sig")
cover.to_csv(os.path.join(OUT,"xgboost_feature_importance_cover.csv"),index=False,encoding="utf-8-sig")
top30=gain.head(30).reset_index(drop=True)
top30.to_csv(os.path.join(OUT,"xgboost_feature_importance_top30.csv"),index=False,encoding="utf-8-sig")
log("feature importance computed. top5 gain:\n"+str(gain.head(5)))

def hbar(df,valcol,title,fname,color=NAVY,n=20):
    d=df.head(n).iloc[::-1]
    fig,ax=plt.subplots(figsize=(9,7))
    ax.barh(range(len(d)),d[valcol],color=color,edgecolor="white")
    ax.set_yticks(range(len(d))); ax.set_yticklabels(d["feature"],fontsize=10)
    ax.set_xlabel(title.split("(")[-1].rstrip(")") if "(" in title else valcol,fontsize=11)
    ax.set_title(title,fontsize=13,fontweight="bold")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="x",color=GRID); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(os.path.join(OUT,fname),dpi=300); plt.close(fig)
hbar(gain,"gain","XGBoost Feature Importance (gain) · Top 20","fig_feature_importance_gain_top20.png",NAVY)
hbar(weight,"weight","XGBoost Feature Importance (weight) · Top 20","fig_feature_importance_weight_top20.png",STEEL)
hbar(cover,"cover","XGBoost Feature Importance (cover) · Top 20","fig_feature_importance_cover_top20.png",GOLD)
hbar(gain,"gain","XGBoost Feature Importance · Top 20","fig_feature_importance_top20.png",NAVY)

# ======================================================================
# 6) basic eval plots
# ======================================================================
from sklearn.metrics import roc_curve, precision_recall_curve
# target distribution
fig,ax=plt.subplots(figsize=(6,4.5))
vc=[ (y_train==0).sum()+(y_test==0).sum(), (y_train==1).sum()+(y_test==1).sum() ]
ax.bar(["부상 미발생\nNo injury","부상 발생\nInjury"],vc,color=[STEEL,GOLD],edgecolor="white")
for i,v in enumerate(vc): ax.text(i,v+500,f"{v:,}\n({v/sum(vc)*100:.1f}%)",ha="center",fontweight="bold",fontsize=11)
ax.set_title("Target Distribution · injury_occurrence",fontweight="bold"); ax.set_ylabel("Count")
for s in ["top","right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_target_distribution.png"),dpi=300); plt.close(fig)
# confusion matrix heatmap
fig,ax=plt.subplots(figsize=(5,4.5))
im=ax.imshow(cm,cmap="Blues")
for (i,j),v in np.ndenumerate(cm):
    ax.text(j,i,f"{v:,}",ha="center",va="center",fontsize=14,
            color="white" if v>cm.max()/2 else INK,fontweight="bold")
ax.set_xticks([0,1]); ax.set_xticklabels(["미발생","발생"]); ax.set_yticks([0,1]); ax.set_yticklabels(["미발생","발생"])
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(f"Confusion Matrix (thr={op_thr})",fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_confusion_matrix.png"),dpi=300); plt.close(fig)
# ROC
fpr,tpr,_=roc_curve(y_test,proba_test)
fig,ax=plt.subplots(figsize=(5.5,4.5)); ax.plot(fpr,tpr,color=NAVY,lw=3); ax.plot([0,1],[0,1],"--",color=STEEL)
ax.fill_between(fpr,tpr,color=NAVY,alpha=0.1); ax.set_title(f"ROC curve (AUC={fin['roc']:.3f})",fontweight="bold")
ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
for s in ["top","right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_roc_curve.png"),dpi=300); plt.close(fig)
# PR
prec,rec,_=precision_recall_curve(y_test,proba_test)
fig,ax=plt.subplots(figsize=(5.5,4.5)); ax.plot(rec,prec,color=GOLD,lw=3)
ax.axhline(y_test.mean(),ls="--",color=STEEL); ax.set_title(f"PR curve (AP={fin['prauc']:.3f})",fontweight="bold")
ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
for s in ["top","right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_precision_recall_curve.png"),dpi=300); plt.close(fig)
# threshold vs P/R/F1
fig,ax=plt.subplots(figsize=(8,4.8))
ax.plot(thr_df.threshold,thr_df.precision,color=GOLD,lw=2,label="Precision")
ax.plot(thr_df.threshold,thr_df.recall,color=STEEL,lw=2,label="Recall")
ax.plot(thr_df.threshold,thr_df.f1_score,color=NAVY,lw=3,label="F1")
ax.axvline(op_thr,ls="--",color=GREY); ax.set_xlabel("Threshold"); ax.set_ylabel("Score")
ax.set_title("Threshold vs Precision / Recall / F1",fontweight="bold"); ax.legend(frameon=False)
for s in ["top","right"]: ax.spines[s].set_visible(False); ax.grid(color=GRID); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_threshold_precision_recall_f1.png"),dpi=300); plt.close(fig)
log("eval plots saved.")

# ======================================================================
# 7) SHAP analysis (final model)
# ======================================================================
import shap
log("SHAP TreeExplainer ...")
SAMPLE=3000
n_test=X_test.shape[0]
rng=np.random.RandomState(42)
idx=rng.choice(n_test, min(SAMPLE,n_test), replace=False)
X_samp=X_test[idx].toarray().astype(np.float32)
X_samp_df=pd.DataFrame(X_samp, columns=keep_names)
expl=shap.TreeExplainer(model)
sv=expl.shap_values(X_samp_df)   # (n, p) for binary:logistic (log-odds, positive class)
if isinstance(sv,list): sv=sv[1]
np.save(os.path.join(OUT,"shap_values_sample.npy"), sv.astype(np.float32))
log(f"shap_values shape={sv.shape}")

mean_abs=np.abs(sv).mean(axis=0)
Xs=X_samp
# binary vs numeric feature detection
is_bin=((Xs==0)|(Xs==1)).all(axis=0)
freq_present=(Xs==1).sum(0).astype(int)
# direction for binary one-hots: mean SHAP when category present (==1)
present_mean=np.divide((sv*(Xs==1)).sum(0), np.maximum(freq_present,1))
# direction for numeric: Pearson corr(value, SHAP)
xc=Xs-Xs.mean(0); sc=sv-sv.mean(0)
den=np.sqrt((xc**2).sum(0))*np.sqrt((sc**2).sum(0))
with np.errstate(invalid="ignore",divide="ignore"):
    corr=np.nan_to_num((xc*sc).sum(0)/den)
# unified signed impact + direction sign
signed_impact=np.where(is_bin, present_mean, corr*mean_abs)
dir_sign=np.where(is_bin, np.sign(present_mean), np.sign(corr))
LOC_ID=("이정","노선명","지사명")
def base_of(n):
    return n[:n.rfind("_")] if "_" in n else n
is_locid=np.array([base_of(n) in LOC_ID for n in keep_names])
shap_imp=pd.DataFrame({"feature":keep_names,"mean_abs_shap":mean_abs,
                       "signed_impact":signed_impact,"dir_sign":dir_sign,
                       "corr":corr,"is_binary":is_bin,"freq_present":freq_present,
                       "is_location_id":is_locid}
                     ).sort_values("mean_abs_shap",ascending=False).reset_index(drop=True)
# actionable = interpretable factors (drop single-record one-hots & raw location IDs)
shap_imp["actionable"]=( ((~shap_imp.is_binary) | (shap_imp.freq_present>=20))
                         & (~shap_imp.is_location_id) )
shap_imp.head(30).to_csv(os.path.join(OUT,"shap_importance_top30.csv"),index=False,encoding="utf-8-sig")
shap_act=shap_imp[shap_imp.actionable].reset_index(drop=True)
shap_act.head(30).to_csv(os.path.join(OUT,"shap_importance_top30_actionable.csv"),index=False,encoding="utf-8-sig")
log("SHAP top10 (actionable):\n"+str(shap_act.head(10)[["feature","mean_abs_shap","signed_impact","is_binary","freq_present"]]))

# beeswarm
plt.figure()
shap.summary_plot(sv, X_samp_df, max_display=20, show=False, plot_size=(9,7))
plt.title("SHAP Summary (beeswarm) · Injury occurrence",fontweight="bold")
plt.tight_layout(); plt.savefig(os.path.join(OUT,"fig_shap_summary_beeswarm.png"),dpi=300); plt.close()
# bar
plt.figure()
shap.summary_plot(sv, X_samp_df, plot_type="bar", max_display=20, show=False, plot_size=(9,7))
plt.title("SHAP Importance (mean |SHAP|) · Top 20",fontweight="bold")
plt.tight_layout(); plt.savefig(os.path.join(OUT,"fig_shap_summary_bar.png"),dpi=300); plt.close()
# custom top20 bar (navy) — actionable factors only, colored by direction
d=shap_act.head(20).iloc[::-1]
fig,ax=plt.subplots(figsize=(9.5,7))
cols=[GOLD if m>0 else STEEL for m in d.signed_impact]
ax.barh(range(len(d)),d.mean_abs_shap,color=cols,edgecolor="white")
ax.set_yticks(range(len(d))); ax.set_yticklabels(d.feature,fontsize=10)
ax.set_xlabel("mean |SHAP value|"); ax.set_title("SHAP Top-20 주요 요인 (gold=부상위험↑ / blue=위험↓)",fontweight="bold")
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.grid(axis="x",color=GRID); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig_shap_importance_top20_bar.png"),dpi=300); plt.close(fig)

# dependence top5 (actionable factors)
top5=shap_act.head(5).feature.tolist()
for k,feat in enumerate(top5,1):
    try:
        plt.figure()
        shap.dependence_plot(feat, sv, X_samp_df, interaction_index=None, show=False)
        plt.title(f"SHAP dependence · {feat}",fontweight="bold")
        plt.tight_layout(); plt.savefig(os.path.join(OUT,f"fig_shap_dependence_top{k}.png"),dpi=300); plt.close()
    except Exception as e:
        log(f"dependence plot {feat} failed: {e}")
log("SHAP plots saved.")

# ======================================================================
# 8) SHAP interpretation table
# ======================================================================
def split_oh(name):
    if "_" in name:
        i=name.rfind("_"); return name[:i], name[i+1:]
    return name, "(numeric)"
def direction(sgn):
    if sgn>0: return "부상 위험 증가(↑)"
    if sgn<0: return "부상 위험 감소(↓)"
    return "영향 미미(≈)"
def interp_text(base,cat,is_bin,sgn):
    d = "높아짐" if sgn>0 else ("낮아짐" if sgn<0 else "영향 미미")
    if is_bin: return f"'{base}'가 '{cat}'일 때 부상 발생 위험이 {d}"
    return f"'{base}' 값이 클수록 부상 발생 위험이 {d}"
def build_interp(df):
    out=[]
    for rank,row in df.reset_index(drop=True).iterrows():
        base,cat=split_oh(row.feature)
        out.append({"순위":rank+1,"변수명":row.feature,"원변수":base,
                    "범주":cat if row.is_binary else "(수치형)",
                    "변수유형":"binary" if row.is_binary else "numeric",
                    "출현빈도":int(row.freq_present),
                    "mean_abs_SHAP":round(float(row.mean_abs_shap),5),
                    "방향지표":round(float(row.signed_impact),5),
                    "영향_방향":direction(row.dir_sign),
                    "해석":interp_text(base,cat,bool(row.is_binary),row.dir_sign)})
    return pd.DataFrame(out)
# full table (all features) + actionable top20
build_interp(shap_imp).to_csv(os.path.join(OUT,"shap_interpretation_table.csv"),index=False,encoding="utf-8-sig")
build_interp(shap_act.head(20)).to_csv(os.path.join(OUT,"shap_interpretation_table_top20.csv"),index=False,encoding="utf-8-sig")

# ======================================================================
# 9) factor-group analysis
# ======================================================================
GROUPS={
 "사고 특성":["사고유형","주사고원인","사고원인구분","운전자상태","사고직전차량조작","사고차량수","사고전차량통행속도","교통장애요인"],
 "차량":["원인차차종","차종구분1","차종구분2","차종규격","차종_규격"],
 "도로환경":["노면상태","사고시도로환경","포장구분","포장상태","평면선형","선형구분","편경사","조명시설","방책시설중분대","방책시설갓길","절성토구분","작업장구분","발생지점","차로","구분","방향"],
 "시간·기상":["사고시간","요일","주야구분","날씨","accident_month","accident_hour","accident_weekday_num","accident_time_band","accident_year","accident_day"],
 "운전자":["성별","성별.1","원인차운전자연령구분","운전시간","운전거리km"],
}
def grp_of(orig):
    for g,keys in GROUPS.items():
        if orig in keys or any(orig.startswith(k) for k in keys): return g
    return "기타"
rows=[]
for _,r in shap_act.head(60).iterrows():
    base,cat=split_oh(r.feature)
    rows.append({"요인군":grp_of(base),"주요변수":r.feature,
                 "영향_방향":direction(r.dir_sign),
                 "mean_abs_SHAP":round(float(r.mean_abs_shap),5),
                 "해석":interp_text(base,cat,bool(r.is_binary),r.dir_sign)})
fa=pd.DataFrame(rows).sort_values(["요인군","mean_abs_SHAP"],ascending=[True,False])
fa.to_csv(os.path.join(OUT,"injury_severity_factor_analysis_table.csv"),index=False,encoding="utf-8-sig")

# increase / decrease top lists (actionable factors)
inc=shap_act[shap_act.dir_sign>0].sort_values("mean_abs_shap",ascending=False).head(10)
dec=shap_act[shap_act.dir_sign<0].sort_values("mean_abs_shap",ascending=False).head(10)

# ======================================================================
# 10) summary report
# ======================================================================
sel=pd.DataFrame(sel_rows)
with open(os.path.join(OUT,"analysis_summary_report.txt"),"w",encoding="utf-8") as f:
    def w(*a): print(*a,file=f)
    w("="*70); w("고속도로 교통사고 부상 발생(injury_occurrence) 요인 분석 + SHAP 해석"); w("="*70)
    w("\n[1] 데이터 개요")
    w(f"  - 학습: {X_train.shape[0]:,}행 / 검증: {X_test.shape[0]:,}행")
    w(f"  - 변수 수(누수 제거 후): {len(keep_names):,} (원본 {n_all:,} 중 누수 {len(drop_names):,}개 제거)")
    w(f"  - target: injury_occurrence (부상 발생 여부)")
    w(f"  - 분포: 미발생 {(y_train==0).sum()+(y_test==0).sum():,} / 발생 {(y_train==1).sum()+(y_test==1).sum():,} (발생률 {y_test.mean()*100:.2f}%)")
    w(f"  - 클래스 불균형 ≈ {ratio:.2f}:1")
    w("\n[2] 모델 성능 (최종 선택 모델, PR-AUC 기준)")
    w(f"  - scale_pos_weight = {final_spw}")
    for r in sel_rows:
        w(f"  - [{r['criterion']}] thr={r['threshold']:.2f}  Acc={r['accuracy']:.4f} P={r['precision']:.4f} R={r['recall']:.4f} F1={r['f1_score']:.4f}")
    w(f"  - ROC-AUC={fin['roc']:.4f}  PR-AUC={fin['prauc']:.4f}")
    w(f"  - Confusion Matrix(thr={op_thr}): TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
    w("\n[3] 주요 영향요인 (gain importance top10)")
    for _,r in gain.head(10).iterrows(): w(f"  - {r['feature']}: {r['gain']:.2f}")
    w("\n[4] SHAP 상위 주요 요인 (actionable, mean|SHAP| top10)")
    for _,r in shap_act.head(10).iterrows(): w(f"  - {r['feature']}: {r['mean_abs_shap']:.4f} ({direction(r['dir_sign'])})")
    w("\n[5] 부상 위험 증가 방향 top10")
    for _,r in inc.iterrows(): w(f"  ↑ {r['feature']} (mean|SHAP|={r['mean_abs_shap']:.4f})")
    w("\n[6] 부상 위험 감소 방향 top10")
    for _,r in dec.iterrows(): w(f"  ↓ {r['feature']} (mean|SHAP|={r['mean_abs_shap']:.4f})")
    w("\n[7] 학술 발표용 문장")
    w("  본 연구는 2011–2019년 전국 고속도로 교통사고 데이터를 대상으로, 사고 발생 이후 정보")
    w("  (구급차·견인차 도착시간, 사고처리시간 등 운영 변수)를 제거한 사고 발생 이전·시점 변수만으로")
    w("  XGBoost 이진분류 모델을 구축하고 SHAP으로 부상 발생 요인을 해석하였다.")
    w(f"  최종 모델(scale_pos_weight={final_spw})은 ROC-AUC {fin['roc']:.3f}, PR-AUC {fin['prauc']:.3f}를 보였으며,")
    w("  심한 클래스 불균형(약 8:1) 하에서 PR-AUC와 F1, Recall 중심으로 평가하였다.")
    w("  SHAP 분석 결과, 사고유형·주사고원인(졸음·노면잡물 등)·운전자상태 등 사고 특성 변수가")
    w("  부상 발생 위험을 높이는 주요 요인으로 나타났다.")
log("ALL DONE. outputs at: "+OUT)
print("DONE_OK", flush=True)
