# APTE 2026 — 고속도로 교통사고 부상발생 요인 분석 (XGBoost·SHAP)

> Analysis of factors associated with injury severity in freeway crashes
> based on XGBoost–SHAP algorithm
> (The 15th Asia-Pacific Conference on Transportation and the Environment)

2011~2019 전국 고속도로 교통사고 데이터(83,297건)에서 **사고 전(pre-accident) 조건
14개 변수**만으로 부상발생 여부를 예측하고, SHAP으로 비선형·상호작용 위험구조를
해석한다.

## 핵심 결과

| 지표 (균형 설계, 5-seed 평균) | 값 |
|---|---|
| ROC-AUC | **0.785 ± 0.005** |
| PR-AUC | 0.766 ± 0.009 |
| F1-score | **0.724 ± 0.004** |
| Recall | **0.762 ± 0.008** |
| Precision | 0.689 ± 0.005 |
| Accuracy | 0.709 ± 0.004 |

- 부상위험 ↑: 안전거리미확보(OR 2.07) · 트레일러(2.70) · 승합(1.89) · 졸음(1.57) ·
  주시태만(1.54) · 정차차량(3.45) — 다변량 로지스틱 p<0.001
- 부상위험 ↓: 단독차량화재(0.05) · 노면잡물(0.10) · 영업소TG(0.12) · 램프(0.30)
- 상호작용(FDR q<0.05): TG×승용(보호효과 이질성) · 주시태만×본선(위험 증폭) ·
  승합×대형(부상률 28.3%) · 노면잡물×도로환경정상 — SHAP 탐색 후 로지스틱 검정 통과
- SHAP–로지스틱 방향 일치율 82% (2단계 프레임워크의 견고성 근거)

상세 내용: [docs/analysis_report.md](docs/analysis_report.md)

## 저장소 구조

```
├── data/
│   ├── raw/                  # 5차 전처리 데이터 (팀 공유 원본)
│   └── processed/            # analysis_dataset.csv (최종 14개 변수 + injury)
├── src/
│   ├── 01_preprocess.py         # 전처리 + Cramér's V/VIF 공선성 진단 + 변수 선별
│   ├── 02_model_xgboost.py      # 균형/불균형 설계 XGBoost + LR 베이스라인
│   ├── 03_shap_analysis.py      # SHAP 전역 중요도 + 상호작용 분해
│   ├── 04_confirmatory_stats.py # 카이제곱 + 다변량 로지스틱 OR + 방향 일치율
│   └── 05_interaction_deep.py   # 상호작용 랭킹 A/B + FDR 검정 + 프로파일
├── outputs/
│   ├── figures/              # fig01~fig08 (히트맵, ROC/PR, SHAP 등)
│   ├── tables/               # 성능표, 중요도, 상호작용, 선별 로그
│   └── model/                # 학습된 모델(json), 데이터 분할, SHAP 값
└── docs/
    └── analysis_report.md    # 분석 리포트 (방법론·결과·기존 분석과의 차이)
```

## 실행

```bash
pip install -r requirements.txt
python3 src/01_preprocess.py    # 원본 통합 CSV 경로 필요 (스크립트 상단 RAW 참조)
python3 src/02_model_xgboost.py
python3 src/03_shap_analysis.py
```

## 방법론 요약

1. **전처리**: 후보 18개 사고 전 변수 정제 — 표기 통합, 결측률 5% 미만 최빈값 대치,
   희소 범주(0.5% 미만) 통합, 오류 변수(운전시간) 제거, 사고 결과 파생 변수 전면 배제
2. **공선성 진단**: bias-corrected Cramér's V (주야구분 제거, V=0.710) +
   설명력 하위 3개 제거 + 더미 VIF 검증(max 5.46) → **최종 14개 변수**
3. **모델링**: 1:1 언더샘플링 균형 설계(문헌 표준) + 5-seed 반복 + 로지스틱 베이스라인
   + 불균형 보조 설계(임계값 최적화)
4. **해석**: SHAP 전역 중요도·방향(실증 부상률 교차검증), SHAP interaction values
   기반 교차변수 상호작용 랭킹
5. **확인적 검정(2단계 프레임워크)**: SHAP으로 후보를 *탐색*하고, 다변량 로지스틱
   (OR·95% CI·p)과 주효과 통제 상호작용항 검정 + BH-FDR로 *확인* — SHAP 랭킹만
   보고하는 기존 연구와의 방법론적 차별점
