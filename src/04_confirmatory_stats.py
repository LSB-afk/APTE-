# -*- coding: utf-8 -*-
"""
04_confirmatory_stats.py
확인적 통계 분석 (Phase 1)
- 변수 수준: 카이제곱 검정 p-value + bias-corrected Cramér's V
- 범주 수준: 다변량 로지스틱 회귀 — 오즈비(OR) + 95% CI + p-value
  (기준범주 = 최빈범주, 완전분리 더미는 제외 후 각주 처리)
- XGBoost SHAP 방향 vs 로지스틱 OR 방향 일치율 (견고성 근거)
- OR forest plot
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2_contingency
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TAB = os.path.join(BASE, "outputs", "tables")
OUT_FIG = os.path.join(BASE, "outputs", "figures")


def cramers_v_stat(x, y):
    tab = pd.crosstab(x, y)
    chi2, p, dof, _ = chi2_contingency(tab, correction=False)
    n = tab.values.sum()
    phi2 = chi2 / n
    r, k = tab.shape
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc = r - (r - 1) ** 2 / (n - 1)
    kc = k - (k - 1) ** 2 / (n - 1)
    denom = min(rc - 1, kc - 1)
    v = np.sqrt(phi2c / denom) if denom > 0 else 0.0
    return chi2, dof, p, v


def onehot_mode_reference(df, cols):
    """최빈범주를 기준범주로 제거한 원-핫 인코딩 (+기준범주 기록)"""
    parts, refs = [], {}
    for c in cols:
        mode = df[c].value_counts().idxmax()
        refs[c] = mode
        d = pd.get_dummies(df[c], prefix=c)
        d = d.drop(columns=f"{c}_{mode}")
        parts.append(d)
    return pd.concat(parts, axis=1).astype(float), refs


def main():
    df = pd.read_csv(os.path.join(BASE, "data", "processed",
                                  "analysis_dataset.csv"))
    y = df["injury"].values
    predictors = [c for c in df.columns if c != "injury"]

    # ------------------------------------------------------------------
    # 1. 변수 수준: 카이제곱 + Cramér's V
    # ------------------------------------------------------------------
    rows = []
    for c in predictors:
        chi2, dof, p, v = cramers_v_stat(df[c], df["injury"])
        rows.append({"variable": c, "n_categories": df[c].nunique(),
                     "chi2": chi2, "dof": dof, "p_value": p, "cramers_v": v})
    var_sig = pd.DataFrame(rows).sort_values("cramers_v", ascending=False)
    var_sig.to_csv(os.path.join(OUT_TAB, "variable_significance.csv"),
                   index=False, encoding="utf-8-sig")
    print("[변수 수준 유의성]")
    with pd.option_context("display.float_format", "{:.4g}".format):
        print(var_sig.to_string(index=False))

    # ------------------------------------------------------------------
    # 2. 다변량 로지스틱 회귀 (전체 83,297건 — 추론용이므로 균형화 불필요)
    # ------------------------------------------------------------------
    X, refs = onehot_mode_reference(df, predictors)

    # 완전분리 더미 탐지: 해당 조건에서 부상이 0건(또는 전건)이면 MLE 발산
    separated = []
    for c in X.columns:
        on = X[c].values == 1
        pos = y[on].sum()
        if pos == 0 or pos == on.sum():
            separated.append({"dummy": c, "n": int(on.sum()),
                              "n_injury": int(pos),
                              "note": "완전분리 — OR 추정 불가(사실상 위험 0)"})
    sep_cols = [s["dummy"] for s in separated]
    if separated:
        pd.DataFrame(separated).to_csv(
            os.path.join(OUT_TAB, "logistic_separated_dummies.csv"),
            index=False, encoding="utf-8-sig")
        print(f"\n완전분리 더미 {len(sep_cols)}개 제외: {sep_cols}")
    Xm = X.drop(columns=sep_cols)

    model = sm.Logit(y, sm.add_constant(Xm)).fit(disp=0, method="lbfgs",
                                                 maxiter=500)
    print(f"\n[로지스틱 모형] n={int(model.nobs):,}, "
          f"pseudo R²={model.prsquared:.4f}, LLR p={model.llr_pvalue:.3g}")

    or_tab = pd.DataFrame({
        "dummy": model.params.index,
        "coef": model.params.values,
        "OR": np.exp(model.params.values),
        "OR_CI_low": np.exp(model.conf_int()[0].values),
        "OR_CI_high": np.exp(model.conf_int()[1].values),
        "p_value": model.pvalues.values,
    })
    or_tab = or_tab[or_tab["dummy"] != "const"]
    or_tab["variable"] = [next(v for v in predictors
                               if d.startswith(v + "_"))
                          for d in or_tab["dummy"]]
    or_tab["reference"] = or_tab["variable"].map(refs)
    or_tab["sig"] = np.select(
        [or_tab.p_value < 0.001, or_tab.p_value < 0.01, or_tab.p_value < 0.05],
        ["***", "**", "*"], default="")
    or_tab = or_tab.sort_values("p_value")
    or_tab.round(4).to_csv(os.path.join(OUT_TAB, "logistic_or_table.csv"),
                           index=False, encoding="utf-8-sig")
    print("\n[다변량 로지스틱 OR — 유의 상위 20]")
    print(or_tab.head(20)[["dummy", "OR", "OR_CI_low", "OR_CI_high",
                           "p_value", "sig", "reference"]]
          .round(4).to_string(index=False))

    # ------------------------------------------------------------------
    # 3. SHAP 방향 vs LR 방향 일치율
    # ------------------------------------------------------------------
    shap_imp = pd.read_csv(os.path.join(OUT_TAB, "shap_importance.csv"))
    merged = or_tab.merge(shap_imp, left_on="dummy", right_on="feature",
                          how="inner").dropna(subset=["shap_when_present"])
    merged["lr_dir"] = np.sign(merged["coef"])
    merged["shap_dir"] = np.sign(merged["shap_when_present"])
    merged["agree"] = merged["lr_dir"] == merged["shap_dir"]
    sig = merged[merged["p_value"] < 0.05]
    print(f"\n[방향 일치율] 전체 더미: {merged['agree'].mean():.1%} "
          f"({merged['agree'].sum()}/{len(merged)}) | "
          f"LR 유의(p<0.05) 더미: {sig['agree'].mean():.1%} "
          f"({sig['agree'].sum()}/{len(sig)})")
    merged[["dummy", "OR", "p_value", "shap_when_present",
            "mean_abs_shap", "agree"]].round(4).to_csv(
        os.path.join(OUT_TAB, "shap_lr_direction_agreement.csv"),
        index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------
    # 4. OR forest plot (유의 더미 중 효과크기 상위 20)
    # ------------------------------------------------------------------
    top = (or_tab[or_tab["p_value"] < 0.05]
           .assign(abslog=lambda t: np.abs(np.log(t["OR"])))
           .sort_values("abslog", ascending=False).head(20)
           .sort_values("OR"))
    fig, ax = plt.subplots(figsize=(8.5, 8))
    ypos = np.arange(len(top))
    colors = ["#C0392B" if o > 1 else "#2471A3" for o in top["OR"]]
    ax.errorbar(top["OR"], ypos,
                xerr=[top["OR"] - top["OR_CI_low"],
                      top["OR_CI_high"] - top["OR"]],
                fmt="none", ecolor="#7F8C8D", capsize=2.5, lw=1)
    ax.scatter(top["OR"], ypos, c=colors, s=45, zorder=3)
    ax.axvline(1, color="black", lw=0.8, ls="--")
    ax.set_yticks(ypos)
    ax.set_yticklabels(top["dummy"], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("오즈비 (log scale, 기준범주 대비)")
    ax.set_title("다변량 로지스틱 오즈비 — 유의(p<0.05) 상위 20 (95% CI)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig09_or_forest.png"), dpi=200)
    plt.close(fig)
    print("\n완료 → outputs/tables, fig09_or_forest.png")


if __name__ == "__main__":
    main()
