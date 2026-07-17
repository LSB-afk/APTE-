# -*- coding: utf-8 -*-
"""
05_interaction_deep.py
상호작용 심층 분석 (Phase 2)
- 랭킹 A: mean |SHAP interaction| (전체 기여 — 등장 빈도에 가중됨)
- 랭킹 B: 두 조건 동시 존재 표본에서의 mean |SHAP interaction| (건당 강도)
- 상위 쌍별: 실증 2×2 부상률 + 조정 로지스틱 상호작용항 Wald 검정 + BH-FDR
- 부호 조합 해석 라벨(증폭/완충/이질성/보호시너지) → 상호작용 프로파일
- 사례연구: 영업소(TG) × 차종별 부상률 (보호효과 이질성)
"""
import os
import numpy as np
import pandas as pd
import shap
import statsmodels.api as sm
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

SEED = 42
N_SAMPLE = 2000        # interaction 계산 표본
MIN_CO_SAMPLE = 30     # 랭킹 B 최소 동시발생 수(표본 내)
MIN_CO_FULL = 100      # 검정 최소 동시발생 수(전체 데이터)
TOP_K = 15             # 랭킹 A/B 각 상위 K → 후보 합집합


def onehot_mode_reference(df, cols):
    parts = []
    for c in cols:
        mode = df[c].value_counts().idxmax()
        d = pd.get_dummies(df[c], prefix=c).drop(columns=f"{c}_{mode}")
        parts.append(d)
    return pd.concat(parts, axis=1).astype(float)


def main():
    # ------------------------------------------------------------------
    # 0. 데이터/모델 로드
    # ------------------------------------------------------------------
    df = pd.read_csv(os.path.join(BASE, "data", "processed",
                                  "analysis_dataset.csv"))
    y = df["injury"].values
    predictors = [c for c in df.columns if c != "injury"]
    X_full = pd.get_dummies(df[predictors]).astype(np.int8)

    model = XGBClassifier()
    model.load_model(os.path.join(OUT_MODEL, "xgb_injury_balanced.json"))
    X_te = pd.read_parquet(os.path.join(OUT_MODEL, "X_test_balanced.parquet"))
    cols = X_te.columns

    def parent(dummy):
        return max((v for v in predictors if dummy.startswith(v + "_")),
                   key=len)

    shap_imp = pd.read_csv(os.path.join(OUT_TAB, "shap_importance.csv"))
    shap_dir = shap_imp.set_index("feature")["shap_when_present"]

    # ------------------------------------------------------------------
    # 1. SHAP interaction values (테스트셋 표본)
    # ------------------------------------------------------------------
    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(X_te), size=min(N_SAMPLE, len(X_te)), replace=False)
    Xs = X_te.iloc[idx]
    print(f"interaction values 계산 중... (표본 {len(Xs):,}행)")
    iv = shap.TreeExplainer(model).shap_interaction_values(Xs)

    inter_abs = np.abs(iv).mean(axis=0)
    np.fill_diagonal(inter_abs, 0.0)

    # ------------------------------------------------------------------
    # 2. 랭킹 A(전체 기여) / 랭킹 B(건당 강도)
    # ------------------------------------------------------------------
    rows = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            d1, d2 = cols[i], cols[j]
            if parent(d1) == parent(d2):
                continue
            both = (Xs[d1].values == 1) & (Xs[d2].values == 1)
            n_co = int(both.sum())
            r = {"feature_1": d1, "feature_2": d2,
                 "rankA_mean_abs": inter_abs[i, j],
                 "n_co_sample": n_co,
                 "rankB_per_occurrence": np.nan,
                 "joint_signed": np.nan}
            if n_co >= MIN_CO_SAMPLE:
                r["rankB_per_occurrence"] = np.abs(iv[both, i, j]).mean() * 2
                r["joint_signed"] = iv[both, i, j].mean() * 2
            rows.append(r)
    allp = pd.DataFrame(rows)

    topA = allp.nlargest(TOP_K, "rankA_mean_abs")
    topB = allp.dropna(subset=["rankB_per_occurrence"]).nlargest(
        TOP_K, "rankB_per_occurrence")
    cand = pd.concat([topA, topB]).drop_duplicates(
        subset=["feature_1", "feature_2"]).copy()
    cand["in_rankA_top"] = cand.index.isin(topA.index)
    cand["in_rankB_top"] = cand.index.isin(topB.index)
    print(f"후보 쌍: 랭킹A {len(topA)} ∪ 랭킹B {len(topB)} → {len(cand)}쌍")

    # ------------------------------------------------------------------
    # 3. 실증 2×2 부상률 (전체 데이터)
    # ------------------------------------------------------------------
    def cell_rates(d1, d2):
        a = X_full[d1].values == 1
        b = X_full[d2].values == 1
        return {
            "n_both_full": int((a & b).sum()),
            "rate_both": y[a & b].mean() if (a & b).any() else np.nan,
            "rate_f1_only": y[a & ~b].mean() if (a & ~b).any() else np.nan,
            "rate_f2_only": y[~a & b].mean() if (~a & b).any() else np.nan,
            "rate_neither": y[~a & ~b].mean(),
        }

    emp = pd.DataFrame([cell_rates(r.feature_1, r.feature_2)
                        for r in cand.itertuples()], index=cand.index)
    cand = pd.concat([cand, emp], axis=1)

    # ------------------------------------------------------------------
    # 4. 조정 로지스틱 상호작용항 검정 (주효과 14개 전부 통제)
    # ------------------------------------------------------------------
    Xm = onehot_mode_reference(df, predictors)
    # 완전분리 더미 제외 (04와 동일 기준)
    sep = [c for c in Xm.columns
           if y[Xm[c].values == 1].sum() in (0, (Xm[c].values == 1).sum())]
    Xm = Xm.drop(columns=sep)
    Xm_c = sm.add_constant(Xm)

    def interaction_test(d1, d2, n_both):
        if n_both < MIN_CO_FULL or d1 in sep or d2 in sep:
            return np.nan, np.nan, "검정 제외(표본부족/완전분리)"
        prod = (X_full[d1] * X_full[d2]).astype(float).rename("INT")
        if y[prod.values == 1].sum() in (0, int(prod.sum())):
            return np.nan, np.nan, "검정 제외(상호작용 셀 완전분리)"
        Xt = pd.concat([Xm_c, prod], axis=1)
        try:
            fit = sm.Logit(y, Xt).fit(disp=0, method="lbfgs", maxiter=500)
            return float(fit.params["INT"]), float(fit.pvalues["INT"]), ""
        except Exception as e:
            return np.nan, np.nan, f"수렴실패({type(e).__name__})"

    coefs, ps, notes = [], [], []
    for r in cand.itertuples():
        c_, p_, n_ = interaction_test(r.feature_1, r.feature_2, r.n_both_full)
        coefs.append(c_); ps.append(p_); notes.append(n_)
        tag = f"p={p_:.2e}" if np.isfinite(p_) else n_
        print(f"  {r.feature_1} × {r.feature_2}: {tag}")
    cand["int_coef_logodds"] = coefs
    cand["int_p_value"] = ps
    cand["note"] = notes

    # BH-FDR 보정
    tested = cand["int_p_value"].notna()
    m = int(tested.sum())
    q = pd.Series(np.nan, index=cand.index)
    if m:
        pv = cand.loc[tested, "int_p_value"].sort_values()
        qv = (pv * m / np.arange(1, m + 1))[::-1].cummin()[::-1]
        q.loc[qv.index] = qv
    cand["int_q_value_FDR"] = q

    # ------------------------------------------------------------------
    # 5. 부호 조합 해석 라벨
    # ------------------------------------------------------------------
    def label(r):
        s1 = shap_dir.get(r.feature_1, np.nan)
        s2 = shap_dir.get(r.feature_2, np.nan)
        it = r.int_coef_logodds if np.isfinite(r.int_coef_logodds) \
            else r.joint_signed
        if not (np.isfinite(s1) and np.isfinite(s2) and np.isfinite(it)):
            return "판정불가"
        if s1 > 0 and s2 > 0:
            return "위험 증폭(시너지)" if it > 0 else "중복(완충)"
        if s1 < 0 and s2 < 0:
            return "보호효과 약화(이질성)" if it > 0 else "보호 시너지"
        return "조건부 우세(혼합)"

    cand["main_dir_1"] = cand["feature_1"].map(shap_dir)
    cand["main_dir_2"] = cand["feature_2"].map(shap_dir)
    cand["interpretation"] = [label(r) for r in cand.itertuples()]

    prof = cand.sort_values("rankA_mean_abs", ascending=False)
    prof.round(4).to_csv(os.path.join(OUT_TAB, "interaction_profile.csv"),
                         index=False, encoding="utf-8-sig")
    show_cols = ["feature_1", "feature_2", "rankA_mean_abs",
                 "rankB_per_occurrence", "n_both_full", "rate_both",
                 "int_coef_logodds", "int_p_value", "int_q_value_FDR",
                 "interpretation"]
    print("\n[상호작용 프로파일]")
    print(prof[show_cols].round(4).to_string(index=False))

    # ------------------------------------------------------------------
    # 6. 그림: 랭킹 B 상위 + TG×차종 사례연구
    # ------------------------------------------------------------------
    tb = (prof.dropna(subset=["rankB_per_occurrence"])
          .nlargest(12, "rankB_per_occurrence").iloc[::-1])
    names = [f"{r.feature_1} × {r.feature_2}" for r in tb.itertuples()]
    colors = ["#C0392B" if v > 0 else "#2471A3" for v in tb["joint_signed"]]
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    ax.barh(names, tb["rankB_per_occurrence"], color=colors)
    ax.set_xlabel("건당 상호작용 강도 (동시발생 표본 mean |SHAP interaction|)")
    ax.set_title("SHAP 상호작용 랭킹 B — 건당 강도 상위 (빨강=동시발생 시 위험 가중)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig10_interaction_rankB.png"), dpi=200)
    plt.close(fig)

    vehs = ["승용", "화물", "트레일러", "승합"]
    tg = df["발생지점"] == "영업소(TG)"
    r_tg = [df.loc[tg & (df["원인차차종"] == v), "injury"].mean() for v in vehs]
    r_no = [df.loc[~tg & (df["원인차차종"] == v), "injury"].mean() for v in vehs]
    xp = np.arange(len(vehs))
    fig, ax = plt.subplots(figsize=(7.5, 5))
    b1 = ax.bar(xp - 0.2, r_no, width=0.4, label="TG 외 구간", color="#C0392B")
    b2 = ax.bar(xp + 0.2, r_tg, width=0.4, label="영업소(TG)", color="#2471A3")
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.003,
                f"{b.get_height():.1%}", ha="center", fontsize=9)
    ax.set_xticks(xp)
    ax.set_xticklabels(vehs)
    ax.set_ylabel("부상발생률")
    ax.set_title("사례연구: 영업소(TG)의 보호효과는 차종별로 다르다\n"
                 "(화물·트레일러에서 감소폭이 훨씬 큼 — 상호작용의 실체)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig11_tg_vehicle_casestudy.png"),
                dpi=200)
    plt.close(fig)
    print("\n완료 → interaction_profile.csv, fig10, fig11")


if __name__ == "__main__":
    main()
