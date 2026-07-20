# -*- coding: utf-8 -*-
"""
08_tg_distance_gradient.py
TG(영업소) 거리 기울기 분석 — "TG 보호효과 = 감속 효과" 가설의 공간적 검증
- TG 사고의 (노선, 이정)을 1차원 군집화하여 노선별 TG 위치를 역산
- 본선 사고마다 가장 가까운 TG까지의 거리 계산
- 거리 구간별 인명피해율 + 95% Wilson 신뢰구간 곡선
해석 기준: 거리 증가에 따라 인명피해율이 상승 후 평탄화(포화형)되면
           속도 회복 메커니즘을 지지하는 공간 패턴
실행: python3 이파일.py  (필요 패키지: pandas, numpy, matplotlib, scipy)
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"   # 윈도우면 "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# ── 경로 (절대경로) ──────────────────────────────────────────────
RAW = ("/Users/leeseungbo/Desktop/학회/APTE/APTE_교통사고_데이터/DATA/"
       "2011~2019_고속도로 교통사고 데이터/2011~2019 교통사고 통합 데이터.csv")
OUT_FIG = ("/Users/leeseungbo/Desktop/학회/APTE/APTE-workspace/outputs/"
           "figures/fig15_tg_distance_gradient.png")
OUT_TAB = ("/Users/leeseungbo/Desktop/학회/APTE/APTE-workspace/outputs/"
           "tables/tg_distance_gradient.csv")

# ── 설정값 ──────────────────────────────────────────────────────
CLUSTER_GAP = 0.7    # km — TG 사고 이정 간격이 이보다 벌어지면 다른 TG로 판단
MIN_TG_CRASH = 5     # TG로 인정할 최소 사고 수 (오기록 노이즈 제거)
BINS = [0, 0.5, 1, 2, 3, 5, 10, np.inf]
BIN_LABELS = ["0–0.5", "0.5–1", "1–2", "2–3", "3–5", "5–10", "10+"]


def wilson_ci(k, n, z=1.96):
    """이항 비율의 95% Wilson 신뢰구간"""
    if n == 0:
        return np.nan, np.nan
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return center - half, center + half


def cluster_1d(sorted_vals, gap):
    """정렬된 1차원 값들을 gap 기준으로 군집화 → [(중앙값, 개수), ...]"""
    clusters, cur = [], [sorted_vals[0]]
    for v in sorted_vals[1:]:
        if v - cur[-1] <= gap:
            cur.append(v)
        else:
            clusters.append(cur)
            cur = [v]
    clusters.append(cur)
    return [(float(np.median(c)), len(c)) for c in clusters]


def main():
    # ── 1. 로드 및 정제 ────────────────────────────────────────
    df = pd.read_csv(RAW, low_memory=False)
    df["이정"] = pd.to_numeric(df["이정"], errors="coerce")
    # 노선명 표기 통일 (공백·하이픈 제거: '통영대전선'과 '통영-대전선' 통합)
    df["노선"] = (df["노선명"].astype(str).str.strip()
                  .str.replace(" ", "").str.replace("-", ""))
    loc = df["발생지점"].astype(str).str.strip()
    for c in ["사망", "중상", "경상"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["injury"] = ((df["사망"] + df["중상"] + df["경상"]) > 0).astype(int)

    tg_crash = df[loc.str.startswith("TG") & df["이정"].notna()]
    main_crash = df[loc.eq("본선") & df["이정"].notna()].copy()
    print(f"TG 사고 {len(tg_crash):,}건 / 본선 사고 {len(main_crash):,}건")

    # ── 2. 노선별 TG 위치 역산 (1차원 군집화) ─────────────────
    tg_positions = {}
    for route, g in tg_crash.groupby("노선"):
        vals = np.sort(g["이정"].values)
        clusters = cluster_1d(vals, CLUSTER_GAP)
        pos = [c for c, n in clusters if n >= MIN_TG_CRASH]
        if pos:
            tg_positions[route] = np.array(pos)
    n_tg = sum(len(v) for v in tg_positions.values())
    print(f"역산된 TG 위치: {len(tg_positions)}개 노선, 총 {n_tg}개 지점")

    # ── 3. 본선 사고의 최근접 TG 거리 ─────────────────────────
    main_crash = main_crash[main_crash["노선"].isin(tg_positions)].copy()
    main_crash["tg_dist"] = [
        float(np.min(np.abs(tg_positions[r] - m)))
        for r, m in zip(main_crash["노선"], main_crash["이정"])
    ]
    print(f"거리 계산된 본선 사고: {len(main_crash):,}건 "
          f"(중앙값 {main_crash['tg_dist'].median():.1f}km)")

    # ── 4. 거리 구간별 인명피해율 ─────────────────────────────
    main_crash["bin"] = pd.cut(main_crash["tg_dist"], BINS, labels=BIN_LABELS,
                               right=False)
    rows = []
    for b in BIN_LABELS:
        sub = main_crash[main_crash["bin"] == b]
        n, k = len(sub), int(sub["injury"].sum())
        lo, hi = wilson_ci(k, n)
        rows.append({"구간(km)": b, "사고수": n, "인명피해": k,
                     "인명피해율": k / n if n else np.nan,
                     "CI하한": lo, "CI상한": hi})
    tab = pd.DataFrame(rows)
    overall = main_crash["injury"].mean()
    tab.round(4).to_csv(OUT_TAB, index=False, encoding="utf-8-sig")
    print("\n[거리 구간별 인명피해율] (본선 전체 평균 "
          f"{overall:.3f})")
    print(tab.round(4).to_string(index=False))

    # ── 5. 그림: 막대(사고수) + 선(인명피해율·95% CI) 이중축 ──
    xs = np.arange(len(BIN_LABELS))
    fig, ax = plt.subplots(figsize=(9, 5.2))

    # 배경 막대: 구간별 사고 건수 (오른쪽 축)
    ax2 = ax.twinx()
    bars = ax2.bar(xs, tab["사고수"], width=0.62, color="#D6DCE5",
                   edgecolor="#B0B8C4", zorder=1, label="사고 건수(우측 축)")
    for b, n in zip(bars, tab["사고수"]):
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() / 2,
                 f"{n:,}", ha="center", va="center", fontsize=8,
                 color="#5A6270")
    ax2.set_ylabel("사고 건수", color="#7F8794")
    ax2.tick_params(axis="y", colors="#7F8794")
    ax2.set_ylim(0, tab["사고수"].max() * 1.9)  # 막대를 아래쪽에 깔기

    # 전면 선: 인명피해율 + 95% CI (왼쪽 축)
    ax.errorbar(xs, tab["인명피해율"],
                yerr=[tab["인명피해율"] - tab["CI하한"],
                      tab["CI상한"] - tab["인명피해율"]],
                fmt="o-", color="#C00000", lw=2.2, ms=6.5, capsize=3.5,
                zorder=5, label="인명피해율 (95% CI)")
    for x, r in zip(xs, rows):
        ax.annotate(f"{r['인명피해율']:.1%}", (x, r["CI상한"]),
                    textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=9, color="#C00000",
                    fontweight="bold", zorder=6)
    ax.axhline(overall, color="#555555", ls="--", lw=1, zorder=4,
               label=f"본선 전체 평균 ({overall:.1%})")
    ax.set_xticks(xs)
    ax.set_xticklabels(BIN_LABELS)
    ax.set_xlabel("가장 가까운 영업소(TG)까지의 거리 (km)")
    ax.set_ylabel("인명피해 발생률", color="#C00000")
    ax.tick_params(axis="y", colors="#C00000")
    ax.set_ylim(0.10, 0.16)
    ax.set_title("영업소(TG) 인접도에 따른 본선 사고의 인명피해율 변화")
    ax.set_zorder(ax2.get_zorder() + 1)  # 선을 막대 위로
    ax.patch.set_visible(False)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=200)
    print(f"\n그림 저장: {OUT_FIG}")

    # ── 6. 해석 가이드 ─────────────────────────────────────────
    r0, r_far = tab["인명피해율"].iloc[0], tab["인명피해율"].iloc[-2]
    print("\n[해석 기준]")
    print(f"  TG 인접 0–0.5km 구간: {r0:.1%} vs 5–10km 구간: {r_far:.1%}")
    print("  - 거리에 따라 상승 후 평탄화(포화형)면 → 속도 회복 메커니즘 지지")
    print("  - 신뢰구간이 겹치지 않는 구간 차이만 해석할 것")
    print("  - 무패턴이면 논문에는 넣지 말고 후속 과제로만 언급")


if __name__ == "__main__":
    main()
