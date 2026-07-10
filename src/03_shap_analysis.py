# -*- coding: utf-8 -*-
"""
03_shap_analysis.py
최종 XGBoost 모델 SHAP 해석
- 전역 중요도: beeswarm / bar (mean|SHAP|)
- 요인별 위험 방향(부상위험 증가/감소) 테이블
- SHAP interaction values 기반 상호작용 쌍 분석 (초록의 조건부 위험구조 재현)
"""
import os
import numpy as np
import pandas as pd
import shap
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

N_INTERACTION_SAMPLE = 2000
SEED = 42


def main():
    model = XGBClassifier()
    model.load_model(os.path.join(OUT_MODEL, "xgb_injury_balanced.json"))
    X_te = pd.read_parquet(os.path.join(OUT_MODEL, "X_test_balanced.parquet"))
    print(f"테스트셋 {X_te.shape[0]:,}행 × {X_te.shape[1]}개 더미")

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X_te)
    print("SHAP values:", sv.shape)

    # ------------------------------------------------------------------
    # 1. 전역 중요도 + 방향
    # ------------------------------------------------------------------
    mean_abs = np.abs(sv).mean(axis=0)
    # 방향: 해당 더미=1일 때 SHAP 평균 (범주 존재가 위험을 올리는지/내리는지)
    direction = []
    for j, c in enumerate(X_te.columns):
        on = X_te[c].values.astype(bool)
        d = sv[on, j].mean() if on.sum() >= 30 else np.nan
        direction.append(d)
    imp = pd.DataFrame({
        "feature": X_te.columns,
        "mean_abs_shap": mean_abs,
        "shap_when_present": direction,
    }).sort_values("mean_abs_shap", ascending=False)
    imp["risk_direction"] = np.where(
        imp["shap_when_present"].isna(), "표본부족",
        np.where(imp["shap_when_present"] > 0, "부상위험 증가(↑)", "부상위험 감소(↓)"))
    imp.round(4).to_csv(os.path.join(OUT_TAB, "shap_importance.csv"),
                        index=False, encoding="utf-8-sig")
    print("\n[SHAP 전역 중요도 top15]")
    print(imp.head(15).round(4).to_string(index=False))

    # beeswarm
    fig = plt.figure(figsize=(9, 8))
    shap.summary_plot(sv, X_te, max_display=20, show=False)
    plt.title("SHAP Summary (beeswarm) — 부상발생 위험요인", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, "fig04_shap_beeswarm.png"), dpi=200,
                bbox_inches="tight")
    plt.close("all")

    # bar
    fig = plt.figure(figsize=(8, 7))
    shap.summary_plot(sv, X_te, plot_type="bar", max_display=20, show=False)
    plt.title("SHAP 전역 중요도 (mean |SHAP|)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, "fig05_shap_bar.png"), dpi=200,
                bbox_inches="tight")
    plt.close("all")

    # 방향성 다이버징 바 (top20)
    top = imp.dropna(subset=["shap_when_present"]).head(20).iloc[::-1]
    colors = ["#C0392B" if v > 0 else "#2471A3"
              for v in top["shap_when_present"]]
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    ax.barh(top["feature"], top["shap_when_present"], color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("해당 조건 존재 시 평균 SHAP (log-odds)")
    ax.set_title("요인별 부상위험 방향 (빨강=증가, 파랑=감소)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig06_shap_direction.png"), dpi=200)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 2. SHAP interaction values
    # ------------------------------------------------------------------
    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(X_te), size=min(N_INTERACTION_SAMPLE, len(X_te)),
                     replace=False)
    Xs = X_te.iloc[idx]
    print(f"\ninteraction values 계산 중... (표본 {len(Xs):,}행)")
    iv = explainer.shap_interaction_values(Xs)
    print("interaction shape:", iv.shape)

    inter = np.abs(iv).mean(axis=0)
    np.fill_diagonal(inter, 0.0)
    cols = X_te.columns

    # 더미 → 원변수 매핑 (동일 변수 내 더미쌍은 상호배타 구조 아티팩트 → 제외)
    variables = pd.read_csv(
        os.path.join(BASE, "data", "processed", "analysis_dataset.csv"),
        nrows=1).columns.drop("injury")
    def parent(dummy):
        return max((v for v in variables if dummy.startswith(v + "_")),
                   key=len)

    pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if parent(cols[i]) == parent(cols[j]):
                continue
            pairs.append({"feature_1": cols[i], "feature_2": cols[j],
                          "mean_abs_interaction": inter[i, j]})
    pairs = pd.DataFrame(pairs).sort_values("mean_abs_interaction",
                                            ascending=False)

    # 상호작용 방향: 두 조건이 동시에 존재할 때 평균 상호작용 SHAP
    def joint_dir(f1, f2):
        i, j = cols.get_loc(f1), cols.get_loc(f2)
        both = (Xs[f1].values.astype(bool)) & (Xs[f2].values.astype(bool))
        if both.sum() < 20:
            return np.nan
        return iv[both, i, j].mean() * 2  # 대칭 성분 합산

    top_pairs = pairs.head(20).copy()
    top_pairs["joint_shap_when_both"] = [
        joint_dir(r.feature_1, r.feature_2) for r in top_pairs.itertuples()]
    top_pairs.round(4).to_csv(
        os.path.join(OUT_TAB, "shap_top_interactions.csv"),
        index=False, encoding="utf-8-sig")
    print("\n[SHAP 상호작용 top15]")
    print(top_pairs.head(15).round(4).to_string(index=False))

    # 상호작용 히트맵 (전역 중요도 top15 더미 기준)
    top_feats = list(imp["feature"].head(15))
    ti = [cols.get_loc(f) for f in top_feats]
    sub = inter[np.ix_(ti, ti)]
    fig, ax = plt.subplots(figsize=(10, 8.5))
    im = ax.imshow(sub, cmap="Reds")
    ax.set_xticks(range(len(top_feats)))
    ax.set_yticks(range(len(top_feats)))
    ax.set_xticklabels(top_feats, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(top_feats, fontsize=8)
    for a in range(len(top_feats)):
        for b in range(len(top_feats)):
            ax.text(b, a, f"{sub[a, b]:.3f}", ha="center", va="center",
                    fontsize=6,
                    color="white" if sub[a, b] > sub.max() * 0.6 else "black")
    ax.set_title("SHAP 상호작용 강도 (mean |interaction|, top15 요인)")
    fig.colorbar(im, shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig07_interaction_heatmap.png"), dpi=200)
    plt.close(fig)

    # 상위 상호작용 쌍 dependence (top4)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, r in zip(axes.ravel(), top_pairs.head(4).itertuples()):
        i, j = cols.get_loc(r.feature_1), cols.get_loc(r.feature_2)
        jitter1 = Xs[r.feature_1].values + rng.normal(0, 0.05, len(Xs))
        val = iv[:, i, j] * 2
        c = Xs[r.feature_2].values
        sc = ax.scatter(jitter1, val, c=c, cmap="coolwarm", s=8, alpha=0.6)
        ax.set_xlabel(r.feature_1, fontsize=9)
        ax.set_ylabel("SHAP interaction", fontsize=9)
        ax.set_title(f"{r.feature_1} × {r.feature_2}", fontsize=10)
        ax.set_xticks([0, 1])
        cb = fig.colorbar(sc, ax=ax, ticks=[0, 1])
        cb.set_label(r.feature_2, fontsize=8)
    fig.suptitle("상위 SHAP 상호작용 쌍", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig08_interaction_pairs.png"), dpi=200)
    plt.close(fig)

    # SHAP 값 저장
    np.save(os.path.join(OUT_MODEL, "shap_values_test.npy"), sv)
    print("\nSHAP 분석 완료 → outputs/figures, outputs/tables 저장")


if __name__ == "__main__":
    main()
