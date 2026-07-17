# -*- coding: utf-8 -*-
"""
02_model_xgboost.py
부상발생(injury occurrence) 이진분류 XGBoost 모델링
- 주 설계: 1:1 랜덤 언더샘플링 균형 데이터 → stratified 80/20 분할
  (참고문헌의 심각도 분석 연구에서 표준적으로 사용되는 균형화 설계)
- 반복 샘플링(5 seeds)으로 성능 안정성 확인
- 보조 설계: 전체 불균형 데이터 + scale_pos_weight + 임계값 최적화
- 로지스틱 회귀 베이스라인 비교
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve,
)
from xgboost import XGBClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TAB = os.path.join(BASE, "outputs", "tables")
OUT_FIG = os.path.join(BASE, "outputs", "figures")
OUT_MODEL = os.path.join(BASE, "outputs", "model")
os.makedirs(OUT_MODEL, exist_ok=True)

SEED = 42
N_RESAMPLE = 5

XGB_PARAMS = dict(
    n_estimators=600,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    gamma=0.0,
    objective="binary:logistic",
    eval_metric="auc",
    early_stopping_rounds=50,
    random_state=SEED,
    n_jobs=-1,
)


def load_data():
    df = pd.read_csv(os.path.join(BASE, "data", "processed",
                                  "analysis_dataset.csv"))
    y = df["injury"].values
    X = pd.get_dummies(df.drop(columns="injury"))  # 전체 더미 유지(트리 모델)
    return X, y


def undersample(X, y, seed):
    rng = np.random.default_rng(seed)
    pos = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    neg_s = rng.choice(neg, size=len(pos), replace=False)
    idx = np.concatenate([pos, neg_s])
    rng.shuffle(idx)
    return X.iloc[idx], y[idx]


def evaluate(y_true, prob, thr=0.5):
    pred = (prob >= thr).astype(int)
    return {
        "Accuracy": accuracy_score(y_true, pred),
        "Precision": precision_score(y_true, pred, zero_division=0),
        "Recall": recall_score(y_true, pred),
        "F1": f1_score(y_true, pred),
        "ROC_AUC": roc_auc_score(y_true, prob),
        "PR_AUC": average_precision_score(y_true, prob),
        "threshold": thr,
    }


def fit_xgb(X_tr, y_tr, X_va, y_va, **extra):
    params = {**XGB_PARAMS, **extra}
    model = XGBClassifier(**params)
    model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
    return model


def main():
    X, y = load_data()
    print(f"데이터: {X.shape[0]:,}행 × 더미 {X.shape[1]}개 "
          f"(부상 {y.sum():,}건, {y.mean():.2%})")

    # ------------------------------------------------------------------
    # A. 주 설계: 1:1 언더샘플링 → 5 seeds 반복
    # ------------------------------------------------------------------
    rows = []
    for i in range(N_RESAMPLE):
        seed = SEED + i
        Xb, yb = undersample(X, y, seed)
        X_tr, X_te, y_tr, y_te = train_test_split(
            Xb, yb, test_size=0.2, stratify=yb, random_state=seed)
        X_tr2, X_va, y_tr2, y_va = train_test_split(
            X_tr, y_tr, test_size=0.15, stratify=y_tr, random_state=seed)
        model = fit_xgb(X_tr2, y_tr2, X_va, y_va, random_state=seed)
        prob = model.predict_proba(X_te)[:, 1]
        m = evaluate(y_te, prob)
        m["seed"] = seed
        rows.append(m)
        print(f"  [seed {seed}] AUC={m['ROC_AUC']:.4f} F1={m['F1']:.4f} "
              f"P={m['Precision']:.4f} R={m['Recall']:.4f} "
              f"Acc={m['Accuracy']:.4f}")

    rep = pd.DataFrame(rows)
    summary = rep.drop(columns=["seed", "threshold"]).agg(["mean", "std"]).T
    print("\n[균형 설계 5회 반복 요약]")
    print(summary.round(4).to_string())
    rep.round(4).to_csv(os.path.join(OUT_TAB, "model_balanced_resamples.csv"),
                        index=False, encoding="utf-8-sig")
    summary.round(4).to_csv(os.path.join(OUT_TAB, "model_balanced_summary.csv"),
                            encoding="utf-8-sig")

    # ------------------------------------------------------------------
    # A-1. 대표 모델(seed=42) 재학습 → 그림/저장 (SHAP 분석에 사용)
    # ------------------------------------------------------------------
    Xb, yb = undersample(X, y, SEED)
    X_tr, X_te, y_tr, y_te = train_test_split(
        Xb, yb, test_size=0.2, stratify=yb, random_state=SEED)
    X_tr2, X_va, y_tr2, y_va = train_test_split(
        X_tr, y_tr, test_size=0.15, stratify=y_tr, random_state=SEED)
    model = fit_xgb(X_tr2, y_tr2, X_va, y_va)
    prob = model.predict_proba(X_te)[:, 1]
    final = evaluate(y_te, prob)
    print("\n[대표 모델(seed=42) 테스트 성능]")
    print({k: round(v, 4) for k, v in final.items()})

    # 로지스틱 회귀 베이스라인
    lr = LogisticRegression(max_iter=2000)
    lr.fit(X_tr2.astype(float), y_tr2)
    prob_lr = lr.predict_proba(X_te.astype(float))[:, 1]
    final_lr = evaluate(y_te, prob_lr)

    comp = pd.DataFrame([
        {"model": "Logistic Regression", **final_lr},
        {"model": "XGBoost", **final},
    ])
    comp.round(4).to_csv(os.path.join(OUT_TAB, "model_comparison.csv"),
                         index=False, encoding="utf-8-sig")
    print("\n[모델 비교]")
    print(comp.round(4).to_string(index=False))

    # 모델/데이터 저장 (SHAP 분석에서 재사용)
    model.save_model(os.path.join(OUT_MODEL, "xgb_injury_balanced.json"))
    X_tr.to_parquet(os.path.join(OUT_MODEL, "X_train_balanced.parquet"))
    X_te.to_parquet(os.path.join(OUT_MODEL, "X_test_balanced.parquet"))
    np.save(os.path.join(OUT_MODEL, "y_train_balanced.npy"), y_tr)
    np.save(os.path.join(OUT_MODEL, "y_test_balanced.npy"), y_te)

    # --- 그림: ROC + PR ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    fpr, tpr, _ = roc_curve(y_te, prob)
    fpr_lr, tpr_lr, _ = roc_curve(y_te, prob_lr)
    axes[0].plot(fpr, tpr, label=f"XGBoost (AUC={final['ROC_AUC']:.3f})",
                 color="#C0392B", lw=2)
    axes[0].plot(fpr_lr, tpr_lr, "--",
                 label=f"Logistic (AUC={final_lr['ROC_AUC']:.3f})",
                 color="#7F8C8D", lw=1.5)
    axes[0].plot([0, 1], [0, 1], ":", color="gray", lw=1)
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curve (균형 테스트셋)")
    axes[0].legend(loc="lower right")
    pr_p, pr_r, _ = precision_recall_curve(y_te, prob)
    pr_p_lr, pr_r_lr, _ = precision_recall_curve(y_te, prob_lr)
    axes[1].plot(pr_r, pr_p, label=f"XGBoost (AP={final['PR_AUC']:.3f})",
                 color="#C0392B", lw=2)
    axes[1].plot(pr_r_lr, pr_p_lr, "--",
                 label=f"Logistic (AP={final_lr['PR_AUC']:.3f})",
                 color="#7F8C8D", lw=1.5)
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall Curve")
    axes[1].legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig02_roc_pr_curves.png"), dpi=200)
    plt.close(fig)

    # --- 그림: 혼동행렬 ---
    cm = confusion_matrix(y_te, (prob >= 0.5).astype(int))
    fig, ax = plt.subplots(figsize=(4.6, 4))
    im = ax.imshow(cm, cmap="Reds")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    fontsize=14,
                    color="white" if cm[i, j] > cm.max() * 0.6 else "black")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["미발생(0)", "부상발생(1)"])
    ax.set_yticklabels(["미발생(0)", "부상발생(1)"])
    ax.set_xlabel("예측"); ax.set_ylabel("실제")
    ax.set_title("Confusion Matrix (thr=0.5)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig03_confusion_matrix.png"), dpi=200)
    plt.close(fig)

    # ------------------------------------------------------------------
    # B. 보조 설계: 전체 불균형 데이터 + scale_pos_weight + 임계값 최적화
    # ------------------------------------------------------------------
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)
    X_tr2, X_va, y_tr2, y_va = train_test_split(
        X_tr, y_tr, test_size=0.15, stratify=y_tr, random_state=SEED)
    spw = (y_tr2 == 0).sum() / (y_tr2 == 1).sum()
    model_f = fit_xgb(X_tr2, y_tr2, X_va, y_va, scale_pos_weight=spw)
    prob_f = model_f.predict_proba(X_te)[:, 1]
    thrs = np.arange(0.05, 0.96, 0.01)
    f1s = [f1_score(y_te, (prob_f >= t).astype(int)) for t in thrs]
    best_t = float(thrs[int(np.argmax(f1s))])
    imb = evaluate(y_te, prob_f, thr=best_t)
    pd.DataFrame([imb]).round(4).to_csv(
        os.path.join(OUT_TAB, "model_imbalanced_reference.csv"),
        index=False, encoding="utf-8-sig")
    print(f"\n[보조 설계: 불균형 원데이터, best-F1 thr={best_t:.2f}]")
    print({k: round(v, 4) for k, v in imb.items()})

    with open(os.path.join(OUT_MODEL, "model_config.json"), "w") as f:
        json.dump({"xgb_params": {k: v for k, v in XGB_PARAMS.items()
                                  if k != "n_jobs"},
                   "n_resample": N_RESAMPLE, "seed": SEED,
                   "design": "1:1 random undersampling, stratified 80/20"},
                  f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
