# APTE — 고속도로 교통사고 인명피해 발생의 독립 탐색–확인 분석

> An Independent-Sample Screening–Confirmation Analysis of Casualty
> Occurrence in Expressway Crashes

고속도로 교통사고 83,297건에서 인명피해 발생 여부를 분석한다. 최종 투고용 분석은
학습·검증·SHAP 탐색·독립 확인의 네 표본 역할을 분리하여, 후보 탐색과 통계적 확인의
표본 중복, 전체자료 결과변수 기반 변수선택, 테스트표본 임계값 최적화를 제거했다.

최종 익명 심사용 원고와 재현 결과는
[`submission_outputs_v2/`](submission_outputs_v2/)에 있다. 기존 `src/`, `outputs/`,
`docs/`는 초기 탐색분석 기록이며 최종 학술 주장에는 사용하지 않는다.

## 핵심 결과

| 독립 확인표본 지표 | XGB_natural | Logistic |
|---|---:|---:|
| ROC-AUC | **0.7799** | 0.7740 |
| PR-AUC | **0.3146** | 0.3030 |
| F1 | 0.3532 | 0.3577 |
| Brier score | **0.0851** | 0.0858 |

- 전체 사고: 83,297건, 인명피해 사고 8,993건(10.80%)
- 자료분할: 학습 50%, 검증 15%, SHAP 탐색 15%, 독립 확인 20%
- XGBoost–Logistic paired bootstrap:
  ROC-AUC +0.0059, PR-AUC +0.0116, F1 차이는 유의하지 않음
- 독립 확인 주효과: HC3 강건 로지스틱 회귀에서 BH q<0.05인 27개
- 상호작용: SHAP 후보 13개 중 안정성 기준을 충족한 6개를 검정하여 3개 확인
- 승합차×대형 차급: interaction OR ratio 3.007, 동시 조건 관찰 인명피해율 28.88%

모든 결과는 **사고가 이미 발생한 사례에서의 조건부 연관성**이다. 사고발생 위험,
주행거리당 위험 또는 인과효과로 해석하지 않는다.

상세 근거:

- [투고 가능성 검증·보완 보고서](submission_outputs_v2/APTE_submission_validation_report.md)
- [최종 QA](submission_outputs_v2/manuscript/FINAL_SUBMISSION_QA.md)
- [익명 심사용 PDF](submission_outputs_v2/manuscript/APTE_JKST_anonymous_manuscript.pdf)
- [영문 부록 PDF](submission_outputs_v2/manuscript/APTE_JKST_supplementary_material.pdf)

## 저장소 구조

```
├── analysis_v2/
│   ├── submission_analysis.py          # 독립 탐색–확인 재분석
│   ├── submission_figures_en.py        # 투고용 영문 그림
│   ├── build_submission_manuscript.py  # DOCX·부록 생성
│   └── finalize_submission_package.py  # 제출 패키지 자동 QA
├── submission_outputs_v2/
│   ├── data/                 # 분석자료, 분할, 확인표본 예측
│   ├── models/               # 학습된 XGBoost JSON
│   ├── tables/               # 성능·주효과·상호작용·근거 매핑
│   ├── figures_en/           # 영문 투고용 Figure 1–8
│   └── manuscript/           # 본문·부록 DOCX/PDF와 QA manifest
├── data/, src/, outputs/     # 초기 탐색분석 기록
└── docs/                     # 초기 원고와 분석 기록
```

## 실행

```powershell
uv run --no-project `
  --with pandas --with numpy --with scipy --with scikit-learn `
  --with xgboost --with shap --with statsmodels `
  --with imbalanced-learn --with matplotlib --with pyarrow `
  python analysis_v2/submission_analysis.py

python analysis_v2/submission_figures_en.py
python analysis_v2/build_submission_manuscript.py
python analysis_v2/finalize_submission_package.py
```

## 방법론 요약

1. **사전 변수집합**: 결과변수 기반 전체자료 변수선택을 폐기하고 17개 범주형 변수를 고정
2. **독립 역할 분리**: train / validation / SHAP screening / confirmation
3. **모형 선택**: validation PR-AUC로 Logistic, 자연분포·가중치·RUS·SMOTEN XGBoost 비교
4. **최종 평가**: validation에서 확률보정과 임계값을 고정하고 자연 유병률 confirmation에서 평가
5. **통계확인**: confirmation HC3 강건 GLM, 1,000회 bootstrap, BH-FDR
6. **상호작용**: screening SHAP 후보만 confirmation의 사전 셀 안정성 규칙을 통과하면 검정

사상자 수 음이항 회귀는 저장소에 사고별 실제 사상자 수 원자료가 없어 최종 분석에서
제외했다.
