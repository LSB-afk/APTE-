# -*- coding: utf-8 -*-
"""
06_regression_tables.py
포스터/논문용 회귀 결과표 생성
- 이항 로지스틱 회귀: 부상 발생 여부(0/1) → β, z, OR, 95% CI, p, 유의, 방향
- 음이항 회귀(NB2): 사고당 부상자 수(사망+중상+경상 인원) → β, z, IRR, 95% CI, p, 유의, 방향
- CSV(엑셀/PPT 복사용) + 색상 표 이미지(증가=연빨강, 감소=연파랑, 비유의=흰색)
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(
    BASE, "..", "APTE_교통사고_데이터", "DATA",
    "2011~2019_고속도로 교통사고 데이터", "2011~2019 교통사고 통합 데이터.csv",
)
OUT_TAB = os.path.join(BASE, "outputs", "tables")
OUT_FIG = os.path.join(BASE, "outputs", "figures")

COL_UP = "#FBE2D5"    # 증가(연빨강)
COL_DOWN = "#DEEAF6"  # 감소(연파랑)
COL_NONE = "#FFFFFF"  # 비유의


def onehot_mode_reference(df, cols):
    parts, refs = [], {}
    for c in cols:
        mode = df[c].value_counts().idxmax()
        refs[c] = mode
        d = pd.get_dummies(df[c], prefix=c).drop(columns=f"{c}_{mode}")
        parts.append(d)
    return pd.concat(parts, axis=1).astype(float), refs


def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def build_table(fit, ratio_name):
    ci = fit.conf_int()
    t = pd.DataFrame({
        "변수": fit.params.index,
        "β": fit.params.values,
        "z": fit.tvalues.values,
        ratio_name: np.exp(fit.params.values),
        "CI하한": np.exp(ci[0].values),
        "CI상한": np.exp(ci[1].values),
        "p값": fit.pvalues.values,
    })
    t = t[~t["변수"].isin(["const", "alpha"])]
    t["유의"] = t["p값"].map(stars)
    t["방향"] = np.where(t["p값"] >= 0.05, "비유의",
                       np.where(t["β"] > 0, "증가", "감소"))
    return t


def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def save_table_png(t, ratio_name, title, path):
    disp = t.copy()
    for c in ["β", "z", ratio_name, "CI하한", "CI상한"]:
        disp[c] = disp[c].map(lambda v: f"{v:.3f}")
    disp["p값"] = t["p값"].map(fmt_p)
    cols = ["변수", "β", "z", ratio_name, "CI하한", "CI상한", "p값", "유의", "방향"]
    disp = disp[cols]
    colors = {"증가": COL_UP, "감소": COL_DOWN, "비유의": COL_NONE}
    cell_colors = [[colors[r]] * len(cols) for r in t["방향"]]

    fig, ax = plt.subplots(figsize=(11, 0.34 * len(disp) + 1.4))
    ax.axis("off")
    tab = ax.table(cellText=disp.values, colLabels=cols,
                   cellColours=cell_colors,
                   colColours=["#F2F2F2"] * len(cols),
                   cellLoc="center", loc="center",
                   colWidths=[0.30, 0.08, 0.09, 0.08, 0.09, 0.09,
                              0.09, 0.07, 0.08])
    tab.auto_set_font_size(False)
    tab.set_fontsize(9)
    tab.scale(1, 1.45)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#666666")
        if r == 0:
            cell.set_text_props(weight="bold")
    ax.set_title(title, fontsize=15, weight="bold", loc="left", pad=18)
    fig.text(0.06, 0.012,
             "*** : p < 0.001 / ** : p < 0.01 / * : p < 0.05 / 비유의 : p ≥ 0.05"
             "   (기준범주: 각 변수의 최빈범주)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv(os.path.join(BASE, "data", "processed",
                                  "analysis_dataset.csv"))
    predictors = [c for c in df.columns if c != "injury"]
    y_bin = df["injury"].values

    # 부상자 수(count) 타겟: 원본에서 재계산 (행 순서 동일 — 검증 포함)
    raw = pd.read_csv(RAW, low_memory=False)
    for c in ["사망", "중상", "경상"]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce").fillna(0)
    y_cnt = (raw["사망"] + raw["중상"] + raw["경상"]).astype(int).values
    assert len(y_cnt) == len(df)
    assert ((y_cnt > 0).astype(int) == y_bin).all(), "행 정렬 불일치"
    print(f"부상자 수 분포: 0명 {np.mean(y_cnt==0):.1%}, 1명 {np.mean(y_cnt==1):.1%}, "
          f"2명+ {np.mean(y_cnt>=2):.1%}, 최대 {y_cnt.max()}명")

    X, refs = onehot_mode_reference(df, predictors)
    # 완전분리/전무(all-zero count) 더미 제외
    sep = [c for c in X.columns
           if y_cnt[X[c].values == 1].sum() == 0
           or y_bin[X[c].values == 1].sum() in (0, int((X[c] == 1).sum()))]
    if sep:
        print(f"제외 더미(완전분리/부상자 0): {sep}")
    Xm = sm.add_constant(X.drop(columns=sep))

    # ------------------------------------------------------------------
    # 1. 이항 로지스틱 (부상 발생 여부 → OR)
    # ------------------------------------------------------------------
    logit = sm.Logit(y_bin, Xm).fit(disp=0, method="lbfgs", maxiter=500)
    t_log = build_table(logit, "OR")
    t_log.round(4).to_csv(os.path.join(OUT_TAB, "table_logistic_formatted.csv"),
                          index=False, encoding="utf-8-sig")
    save_table_png(t_log, "OR",
                   "부상 발생 여부 — 이항 로지스틱 회귀 β 검정 결과값",
                   os.path.join(OUT_FIG, "fig12_logistic_table.png"))
    print(f"\n[이항 로지스틱] pseudo R²={logit.prsquared:.4f}  "
          f"유의 더미 {(t_log['p값']<0.05).sum()}/{len(t_log)}")

    # ------------------------------------------------------------------
    # 2. 음이항 회귀 NB2 (사고당 부상자 수 → IRR)
    # ------------------------------------------------------------------
    nb = None
    try:
        cand = sm.NegativeBinomial(y_cnt, Xm).fit(disp=0, method="lbfgs",
                                                  maxiter=2000)
        alpha = float(cand.params.get("alpha", np.nan))
        # 적합 품질 검사: 표준오차 유한 + alpha 정상 범위일 때만 채택
        if np.isfinite(cand.bse.values).all() and alpha > 1e-3:
            nb = cand
    except Exception:
        pass
    if nb is None:
        # 폴백: Poisson 적합 → 모멘트 추정 alpha 고정 GLM-NB (안정적)
        pois = sm.GLM(y_cnt, Xm, family=sm.families.Poisson()).fit()
        mu = pois.fittedvalues
        alpha = max(0.01, float(((y_cnt - mu) ** 2 - mu).sum() / (mu ** 2).sum()))
        nb = sm.GLM(y_cnt, Xm,
                    family=sm.families.NegativeBinomial(alpha=alpha)).fit()
        print(f"NB2 MLE 수렴 실패 → GLM-NB(모멘트 alpha={alpha:.3f}) 사용")
    t_nb = build_table(nb, "IRR")
    t_nb.round(4).to_csv(os.path.join(OUT_TAB, "table_negbin_formatted.csv"),
                         index=False, encoding="utf-8-sig")
    save_table_png(t_nb, "IRR",
                   "사고당 부상자 수 — 음이항 회귀 β 검정 결과값",
                   os.path.join(OUT_FIG, "fig13_negbin_table.png"))
    print(f"[음이항 NB2] alpha={alpha:.3f}  "
          f"유의 더미 {(t_nb['p값']<0.05).sum()}/{len(t_nb)}")

    # 방향 비교 요약
    m = t_log.merge(t_nb, on="변수", suffixes=("_logit", "_nb"))
    both_sig = m[(m["p값_logit"] < 0.05) & (m["p값_nb"] < 0.05)]
    agree = (np.sign(both_sig["β_logit"]) == np.sign(both_sig["β_nb"])).mean()
    print(f"[두 모형 방향 일치] 양쪽 유의 {len(both_sig)}개 더미 중 "
          f"{agree:.1%} 일치")
    print("\n완료 → table_logistic_formatted.csv / table_negbin_formatted.csv, "
          "fig12 / fig13")


if __name__ == "__main__":
    main()
