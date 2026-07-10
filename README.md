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

- 부상위험 ↑: 안전거리미확보 · 졸음 · 주시태만 · 터널/본선 구간 · 피로 · 60세 이상
- 부상위험 ↓: 단독차량화재 · 노면잡물 · 포트홀 · 영업소(TG)/램프 · 습윤 노면
- 상호작용: 주시태만×본선(위험 증폭), 졸음×승용, 노면잡물×도로환경(정상) 등
  조건부 위험구조 확인

상세 내용: [docs/analysis_report.md](docs/analysis_report.md)

## 저장소 구조

```
├── data/
│   ├── raw/                  # 5차 전처리 데이터 (팀 공유 원본)
│   └── processed/            # analysis_dataset.csv (최종 14개 변수 + injury)
├── src/
│   ├── 01_preprocess.py      # 전처리 + Cramér's V/VIF 공선성 진단 + 변수 선별
│   ├── 02_model_xgboost.py   # 균형/불균형 설계 XGBoost + LR 베이스라인
│   └── 03_shap_analysis.py   # SHAP 전역 중요도 + 상호작용 분해
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
