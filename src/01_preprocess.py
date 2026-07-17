# -*- coding: utf-8 -*-
"""
01_preprocess.py
2011~2019 고속도로 교통사고 통합 데이터 → 분석용 데이터셋 구축
- 사고 전(pre-accident) 예측변수만 사용 (사고 결과 변수 누수 차단)
- 범주 정제(오기/중복 표기 통합, 결측 → '미상')
- 공선성 진단: bias-corrected Cramér's V + 원-핫 VIF
- 설명력(타겟 연관성) 기준 변수 선별 → 최종 14개 변수
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
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
OUT_DATA = os.path.join(BASE, "data", "processed")
OUT_TAB = os.path.join(BASE, "outputs", "tables")
OUT_FIG = os.path.join(BASE, "outputs", "figures")
for d in (OUT_DATA, OUT_TAB, OUT_FIG):
    os.makedirs(d, exist_ok=True)

N_FINAL_VARS = 14
CRAMERS_V_THRESHOLD = 0.6  # 이 값 이상이면 강한 연관(공선성)으로 판단


# ----------------------------------------------------------------------
# 1. 로드 및 타겟 정의
# ----------------------------------------------------------------------
def load_raw():
    df = pd.read_csv(RAW, low_memory=False)
    for c in ["사망", "중상", "경상"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["injury"] = ((df["사망"] + df["중상"] + df["경상"]) > 0).astype(int)
    return df


# ----------------------------------------------------------------------
# 2. 범주 정제 규칙
# ----------------------------------------------------------------------
def _strip(s):
    return s.astype(str).str.strip().replace({"nan": np.nan, "": np.nan})


def clean_weather(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if "눈" in v:
            return "눈"
        if "비" in v:
            return "비"
        if "안개" in v:
            return "안개"
        if "흐림" in v:
            return "흐림"
        if "맑음" in v:
            return "맑음"
        return "기타"

    return s.map(f)


def clean_cause(s):
    s = _strip(s)
    etc = {"운전자기타", "운전자요인기타", "운전요인기타", "기타"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in etc:
            return "기타"
        if "주시태만" in v:
            return "주시태만"
        return v

    return s.map(f)


def clean_maneuver(s):
    s = _strip(s)
    keep = {"운행차로주행", "핸들과대조작", "차로변경"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in keep:
            return v
        return "기타"

    return s.map(f)


def clean_driver_state(s):
    s = _strip(s)
    keep = {"정상", "피로", "음주"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in keep:
            return v
        return "기타"

    return s.map(f)


def clean_road_env(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if "미끄러운" in v:
            return "미끄러운노면"
        if "낙하물" in v:
            return "낙하물"
        if "포트홀" in v:
            return "포트홀"
        if "시거장애" in v:
            return "시거장애"
        if v == "정상":
            return "정상"
        return "기타"

    return s.map(f)


def clean_obstacle(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if v == "장애없음":
            return "장애없음"
        if "정차차량" in v:
            return "정차차량"
        if "정체" in v:
            return "정체"
        if "작업장" in v:
            return "작업장"
        return "기타"

    return s.map(f)


def clean_alignment(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if "직선" in v:
            return "직선"
        if "좌커브" in v:
            return "좌커브"
        if "우커브" in v:
            return "우커브"
        return "미상"

    return s.map(f)


def clean_location(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if v == "본선":
            return "본선"
        if v == "램프":
            return "램프"
        if v.startswith("TG"):
            return "영업소(TG)"
        if v == "터널":
            return "터널"
        if v == "휴게소":
            return "휴게소"
        return "기타"

    return s.map(f)


def clean_cutfill(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if v == "평지":
            return "평지"
        if "절토부" in v:
            return v  # 절토부 10M 미만 / 이상
        if "성토고" in v:
            if "2M 미만" in v:
                return "성토고 2M 미만"
            if "15M" in v and "이상" in v:
                return "성토고 15M 이상"
            return v
        return "미상"

    return s.map(f)


def clean_vehicle_type(s):
    s = _strip(s)
    m = {"승용차": "승용", "화물차": "화물", "승합차": "승합", "특수차량": "특수"}

    def f(v):
        if pd.isna(v):
            return "미상"
        v = m.get(v, v)
        if v in {"승용", "화물", "승합", "트레일러", "특수"}:
            return v
        return "기타"

    return s.map(f)


def clean_vehicle_class(s):
    s = _strip(s)
    keep = {"소형", "중형", "대형", "SUV형", "경형", "일반화물", "탑차"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in keep:
            return v
        if v.startswith("대형"):
            return "대형"
        return "기타"

    return s.map(f)


def clean_gender(s):
    s = _strip(s)
    m = {"남자": "남", "남성": "남", "여자": "여", "여성": "여"}

    def f(v):
        if pd.isna(v):
            return "미상"
        return m.get(v, "미상")

    return s.map(f)


def clean_age(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        v = v.replace(" ", "")
        if v in {"0.0", "0"}:
            return "미상"
        if "미만" in v:  # 20세 미만
            return "20세미만"
        if "이상" in v:  # 60세 이상
            return "60세이상"
        # 'A~B' 구간 표기 → 하한 연령대
        if "~" in v:
            try:
                lo = int(float(v.split("~")[0]))
            except ValueError:
                return "미상"
        else:
            try:
                lo = int(float(v))
            except ValueError:
                return "미상"
        if lo < 20:
            return "20세미만"
        if lo >= 60:
            return "60세이상"
        return f"{lo // 10 * 10}대"

    return s.map(f)


def clean_daynight(df):
    s = _strip(df["주야구분"])
    hour = pd.to_datetime(df["사고시간"], format="%H:%M:%S", errors="coerce").dt.hour
    derived = np.where((hour >= 6) & (hour < 18), "주간", "야간")
    out = s.where(s.isin(["주간", "야간"]), pd.Series(derived, index=df.index))
    return out.fillna("미상")


def clean_lighting(s):
    s = _strip(s)
    keep = {"해당없음(주간)", "작동", "없음", "미작동"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in keep:
            return v
        return "미상"

    return s.map(f)


def clean_surface(s):
    s = _strip(s)
    keep = {"건조", "습기", "적설"}

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in keep:
            return v
        return "기타"

    return s.map(f)


def clean_pavement(s):
    s = _strip(s)

    def f(v):
        if pd.isna(v):
            return "미상"
        if v in {"콘크리트", "아스팔트"}:
            return v
        return "미상"

    return s.map(f)


def derive_weekend(df):
    d = pd.to_datetime(df["사고일자"], errors="coerce")
    return np.where(d.dt.dayofweek >= 5, "주말", "평일")


# ----------------------------------------------------------------------
# 3. 데이터셋 구축
# ----------------------------------------------------------------------
def build_dataset(df):
    out = pd.DataFrame(index=df.index)
    out["주사고원인"] = clean_cause(df["주 사고원인"])
    out["사고직전차량조작"] = clean_maneuver(df["사고직전차량조작"])
    out["운전자상태"] = clean_driver_state(df["운전자상태"])
    out["사고시도로환경"] = clean_road_env(df["사고시도로환경"])
    out["교통장애요인"] = clean_obstacle(df["교통장애요인"])
    out["날씨"] = clean_weather(df["날씨"])
    out["주야구분"] = clean_daynight(df)
    out["주말여부"] = derive_weekend(df)
    out["포장구분"] = clean_pavement(df["포장구분"])
    out["노면상태"] = clean_surface(df["노면상태"])
    out["조명시설"] = clean_lighting(df["조명시설"])
    out["평면선형"] = clean_alignment(df["평면선형"])
    out["발생지점"] = clean_location(df["발생지점"])
    out["절성토구분"] = clean_cutfill(df["절성토구분"])
    out["원인차차종"] = clean_vehicle_type(df["원인차차종"])
    out["차종구분"] = clean_vehicle_class(df["차종구분1"])
    out["성별"] = clean_gender(df["성별"])
    out["연령구분"] = clean_age(df["원인차운전자연령구분"])

    # 결측('미상') 처리: 결측률 5% 미만 → 최빈값 대치 / 5% 이상 → '미상' 범주 유지
    n = len(out)
    impute_log = []
    for c in out.columns:
        miss = (out[c] == "미상").mean()
        if 0 < miss < 0.05:
            mode = out.loc[out[c] != "미상", c].value_counts().idxmax()
            out[c] = out[c].replace({"미상": mode})
            impute_log.append({"variable": c, "missing_rate": round(miss, 4),
                               "action": f"최빈값 대치({mode})"})
        elif miss >= 0.05:
            impute_log.append({"variable": c, "missing_rate": round(miss, 4),
                               "action": "'미상' 범주 유지"})
    pd.DataFrame(impute_log).to_csv(
        os.path.join(OUT_TAB, "missing_handling_log.csv"),
        index=False, encoding="utf-8-sig")

    # 희소 범주(0.5% 미만) → 기타 (미상은 유지)
    for c in out.columns:
        vc = out[c].value_counts()
        rare = vc[vc / n < 0.005].index.difference(["미상"])
        if len(rare) > 0:
            out[c] = out[c].replace(dict.fromkeys(rare, "기타"))

    out["injury"] = df["injury"].values
    return out


# ----------------------------------------------------------------------
# 4. 공선성 진단
# ----------------------------------------------------------------------
def cramers_v(x, y):
    """bias-corrected Cramér's V (Bergsma 2013)"""
    tab = pd.crosstab(x, y)
    chi2 = chi2_contingency(tab, correction=False)[0]
    n = tab.values.sum()
    phi2 = chi2 / n
    r, k = tab.shape
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc = r - (r - 1) ** 2 / (n - 1)
    kc = k - (k - 1) ** 2 / (n - 1)
    denom = min(rc - 1, kc - 1)
    return np.sqrt(phi2c / denom) if denom > 0 else 0.0


def cramers_matrix(df, cols):
    m = pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            v = cramers_v(df[a], df[b])
            m.loc[a, b] = m.loc[b, a] = v
    return m


def target_association(df, cols, target="injury"):
    return pd.Series({c: cramers_v(df[c], df[target]) for c in cols}).sort_values(
        ascending=False
    )


def onehot_mode_reference(df, cols):
    """최빈범주를 기준범주로 제거한 원-핫 인코딩"""
    parts = []
    for c in cols:
        mode = df[c].value_counts().idxmax()
        d = pd.get_dummies(df[c], prefix=c)
        d = d.drop(columns=f"{c}_{mode}")
        parts.append(d)
    return pd.concat(parts, axis=1).astype(float)


def vif_table(df, cols):
    """원-핫 인코딩(최빈 기준범주 제거) 행렬에 대한 VIF"""
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    X = onehot_mode_reference(df, cols)
    Xc = X.assign(const=1.0)
    rows = []
    for i, col in enumerate(X.columns):
        rows.append({"dummy": col, "VIF": variance_inflation_factor(Xc.values, i)})
    return pd.DataFrame(rows).sort_values("VIF", ascending=False)


# ----------------------------------------------------------------------
# 5. 실행
# ----------------------------------------------------------------------
def main():
    df = load_raw()
    print(f"원본: {len(df):,}행 / 부상발생 {df['injury'].sum():,}건 "
          f"({df['injury'].mean():.2%})")

    data = build_dataset(df)
    predictors = [c for c in data.columns if c != "injury"]
    print(f"후보 예측변수 {len(predictors)}개: {predictors}")

    # --- Cramér's V 행렬 ---
    cm = cramers_matrix(data, predictors)
    cm.round(4).to_csv(os.path.join(OUT_TAB, "cramers_v_matrix.csv"),
                       encoding="utf-8-sig")

    # 히트맵
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(cm.values, cmap="Reds", vmin=0, vmax=1)
    ax.set_xticks(range(len(predictors)))
    ax.set_yticks(range(len(predictors)))
    ax.set_xticklabels(predictors, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(predictors, fontsize=9)
    for i in range(len(predictors)):
        for j in range(len(predictors)):
            v = cm.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if v > 0.6 else "black")
    ax.set_title("예측변수 간 Cramer's V (bias-corrected)")
    fig.colorbar(im, shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_FIG, "fig01_cramers_v_heatmap.png"), dpi=200)
    plt.close(fig)

    # --- 타겟 연관성 ---
    assoc = target_association(data, predictors)
    assoc.round(4).to_csv(os.path.join(OUT_TAB, "target_association.csv"),
                          encoding="utf-8-sig", header=["cramers_v_with_injury"])
    print("\n[타겟(injury) 연관성 Cramér's V]")
    print(assoc.round(4).to_string())

    # --- 고연관 쌍 → 타겟 연관성 낮은 쪽 제거 ---
    log = []
    dropped = set()
    pairs = [
        (a, b, cm.loc[a, b])
        for i, a in enumerate(predictors)
        for b in predictors[i + 1:]
        if cm.loc[a, b] >= CRAMERS_V_THRESHOLD
    ]
    for a, b, v in sorted(pairs, key=lambda t: -t[2]):
        if a in dropped or b in dropped:
            continue
        drop = a if assoc[a] < assoc[b] else b
        keep = b if drop == a else a
        dropped.add(drop)
        log.append({"step": "collinearity", "dropped": drop, "kept": keep,
                    "cramers_v_pair": round(v, 4),
                    "reason": f"V={v:.3f} ≥ {CRAMERS_V_THRESHOLD}, "
                              f"타겟 연관성 낮은 쪽 제거"})
        print(f"  공선성 제거: {drop} (kept {keep}, V={v:.3f})")

    remaining = [c for c in predictors if c not in dropped]

    # --- 더미 수준 VIF 반복 진단: 구조적 종속 변수 제거 ---
    while True:
        vif = vif_table(data, remaining)
        worst = vif.iloc[0]
        if worst["VIF"] <= 10:
            break
        d1 = worst["dummy"]
        var1 = next(v for v in remaining if d1.startswith(v + "_"))
        # 다른 변수의 더미 중 d1과 상관 최대인 더미 탐색
        X = onehot_mode_reference(data, remaining)
        others = [c for c in X.columns if not c.startswith(var1 + "_")]
        corr = X[others].corrwith(X[d1]).abs()
        d2 = corr.idxmax()
        var2 = next(v for v in remaining if d2.startswith(v + "_"))
        drop = var1 if assoc[var1] < assoc[var2] else var2
        keep = var2 if drop == var1 else var1
        remaining = [c for c in remaining if c != drop]
        log.append({"step": "vif_structural", "dropped": drop, "kept": keep,
                    "cramers_v_pair": round(float(worst["VIF"]), 2),
                    "reason": f"더미 VIF>10 ({d1}↔{d2}, VIF={worst['VIF']:.1f}), "
                              f"타겟 연관성 낮은 쪽 제거"})
        print(f"  VIF 구조적 제거: {drop} ({d1}↔{d2}, VIF={worst['VIF']:.1f})")

    # --- 설명력 하위 변수 제거 → 14개 ---
    if len(remaining) > N_FINAL_VARS:
        ranked = assoc[remaining].sort_values(ascending=False)
        for c in ranked.index[N_FINAL_VARS:]:
            log.append({"step": "low_explanatory", "dropped": c, "kept": "",
                        "cramers_v_pair": round(assoc[c], 4),
                        "reason": f"타겟 연관성 하위 (V={assoc[c]:.4f})"})
            print(f"  설명력 하위 제거: {c} (V={assoc[c]:.4f})")
        remaining = list(ranked.index[:N_FINAL_VARS])

    pd.DataFrame(log).to_csv(os.path.join(OUT_TAB, "variable_selection_log.csv"),
                             index=False, encoding="utf-8-sig")

    # --- VIF 검증 ---
    vif = vif_table(data, remaining)
    vif.round(3).to_csv(os.path.join(OUT_TAB, "vif_final.csv"),
                        index=False, encoding="utf-8-sig")
    print(f"\n[VIF] max={vif['VIF'].max():.2f}, mean={vif['VIF'].mean():.2f}, "
          f"VIF>10 더미 수={int((vif['VIF'] > 10).sum())}")

    # --- 저장 ---
    final = data[remaining + ["injury"]]
    final.to_csv(os.path.join(OUT_DATA, "analysis_dataset.csv"),
                 index=False, encoding="utf-8-sig")

    summary = pd.DataFrame({
        "variable": remaining,
        "n_categories": [final[c].nunique() for c in remaining],
        "categories": [", ".join(map(str, final[c].value_counts().index[:12]))
                       for c in remaining],
        "cramers_v_with_injury": [round(assoc[c], 4) for c in remaining],
    })
    summary.to_csv(os.path.join(OUT_TAB, "final_variable_summary.csv"),
                   index=False, encoding="utf-8-sig")
    print(f"\n최종 변수 {len(remaining)}개 → analysis_dataset.csv 저장")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
