# -*- coding: utf-8 -*-
"""
07_paper_figures.py
논문용 SHAP 의존성 시각화 (범주형 아날로그)
- (a) 주사고원인 범주별 SHAP 분포  (b) 발생지점 범주별
- (c) 연령구분 순서형 SHAP 추세    (d) TG 보호효과의 차종별 이질성
스타일: 개별 표본 산점(남색) + 범주 평균(빨간 선·마커), 0 기준선
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
OUT_FIG = os.path.join(BASE, "outputs", "figures")
OUT_MODEL = os.path.join(BASE, "outputs", "model")
SEED = 42

DOT = dict(s=6, alpha=0.25, color="#1F4E79", linewidths=0)
RED = dict(color="#C00000", lw=2, marker="o", ms=6, zorder=5,
           label="범주 평균 SHAP")


def jitter(n, center, width=0.16, rng=None):
    return center + rng.uniform(-width, width, n)


def main():
    model = XGBClassifier()
    model.load_model(os.path.join(OUT_MODEL, "xgb_injury_balanced.json"))
    X_tr = pd.read_parquet(os.path.join(OUT_MODEL, "X_train_balanced.parquet"))
    X_te = pd.read_parquet(os.path.join(OUT_MODEL, "X_test_balanced.parquet"))
    X = pd.concat([X_tr, X_te])          # 균형 데이터 전체 17,986행
    sv = shap.TreeExplainer(model).shap_values(X)
    sv = pd.DataFrame(sv, columns=X.columns, index=X.index)
    rng = np.random.default_rng(SEED)
    print(f"SHAP 계산 완료: {X.shape[0]:,}행")

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))

    def category_panel(ax, var, cats, title, min_n=40, sort_by_mean=True):
        """범주별: 해당 더미=1 표본의 그 더미 SHAP 분포 + 평균"""
        stats = []
        for c in cats:
            col = f"{var}_{c}"
            if col not in X.columns:
                continue
            on = X[col].values == 1
            if on.sum() < min_n:
                continue
            stats.append((c, sv.loc[on, col].values))
        if sort_by_mean:  # 순서형 변수는 주어진 순서 유지
            stats.sort(key=lambda t: t[1].mean())
        means = []
        for k, (c, vals) in enumerate(stats):
            show = vals if len(vals) <= 1500 else rng.choice(vals, 1500,
                                                             replace=False)
            ax.scatter(jitter(len(show), k, rng=rng), show, **DOT)
            means.append(vals.mean())
        ax.plot(range(len(stats)), means, **RED)
        ax.axhline(0, color="gray", ls="--", lw=0.8)
        ax.set_xticks(range(len(stats)))
        ax.set_xticklabels([c for c, _ in stats], fontsize=9)
        ax.set_ylabel("SHAP (인명피해 기여)", fontsize=9)
        ax.set_title(title, fontsize=11)
        return stats

    # (a) 주사고원인
    category_panel(axes[0, 0], "주사고원인",
                   ["단독차량화재", "노면잡물", "타이어파손", "과속", "주시태만",
                    "졸음", "추월불량", "안전거리미확보"],
                   "(a) 주사고원인별 SHAP 기여 — 인적요인일수록 위험 증가")

    # (b) 발생지점
    category_panel(axes[0, 1], "발생지점",
                   ["영업소(TG)", "램프", "휴게소", "본선", "터널"],
                   "(b) 발생지점별 SHAP 기여 — 고속 구간일수록 위험 증가")

    # (c) 연령구분 (순서형)
    category_panel(axes[1, 0], "연령구분",
                   ["20세미만", "20대", "30대", "40대", "50대", "60세이상"],
                   "(c) 연령구분 SHAP 추세 — 고연령 구간에서 위험 상승",
                   sort_by_mean=False)

    # (d) TG 보호효과의 차종별 이질성
    ax = axes[1, 1]
    tg_col = "발생지점_영업소(TG)"
    on_tg = X[tg_col].values == 1
    vehs = ["승용", "화물", "트레일러", "승합"]
    means = []
    kept = []
    for k, v in enumerate(vehs):
        col = f"원인차차종_{v}"
        m = on_tg & (X[col].values == 1)
        if m.sum() < 20:
            continue
        vals = sv.loc[m, tg_col].values
        ax.scatter(jitter(len(vals), len(kept), rng=rng), vals, **DOT)
        means.append(vals.mean())
        kept.append(f"{v}\n(n={m.sum():,})")
    ax.plot(range(len(kept)), means, **RED)
    ax.axhline(0, color="gray", ls="--", lw=0.8)
    ax.set_xticks(range(len(kept)))
    ax.set_xticklabels(kept, fontsize=9)
    ax.set_ylabel("영업소(TG) 더미의 SHAP", fontsize=9)
    ax.set_title("(d) TG 보호효과의 차종별 이질성 — 승용에서 가장 약함",
                 fontsize=11)

    for ax in axes.ravel():
        ax.legend(loc="lower right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)

    fig.suptitle("범주형 SHAP 의존성 — 인명피해 발생 기여의 범주별 구조 "
                 "(균형 데이터 17,986건)", fontsize=13.5, y=0.995)
    fig.text(0.01, 0.006,
             "※ 점: 개별 사고 표본의 SHAP값(log-odds) / 빨간 선: 범주 평균 · "
             "(d)는 TG 사고 표본에서 TG 더미의 SHAP을 차종별로 비교(상호작용 이질성)",
             fontsize=8.5)
    fig.tight_layout(rect=[0, 0.02, 1, 0.98])
    fig.savefig(os.path.join(OUT_FIG, "fig14_shap_categorical_dependence.png"),
                dpi=200)
    plt.close(fig)
    print("저장: fig14_shap_categorical_dependence.png")


if __name__ == "__main__":
    main()
