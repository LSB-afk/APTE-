# APTE 유사 연구 2편 딥서치 및 방법론적 차별성 검토

- 검토일: 2026-07-16
- 검토 대상: 고속도로 교통사고의 사고조건부 인명피해 발생을 예측·설명·확인하는 APTE 연구
- APTE 근거 문서: `APTE_submission_validation_report.md`, `tables/`, `reproducibility_manifest.json`

## 1. 선정 기준

후보 논문은 단순한 키워드 유사성이 아니라 다음 조건을 기준으로 원문 방법론을 대조하였다.

1. 교통사고 심각도 또는 인명피해를 분석하는가
2. XGBoost와 SHAP을 사용하는가
3. 비선형 관계나 변수 간 상호작용을 분석하는가
4. 기계학습 결과를 Bayesian network 또는 통계모형과 연결하는가
5. SHAP 탐색과 통계적 확인에 독립된 표본을 사용하는가
6. 불균형 평가, 확률보정, 임계값 고정, 다중검정 및 희소 셀 안정성을 통제하는가

검토 결과, Yang et al. (2022)은 **고속도로 사고라는 연구주제**가 가장 가까웠고, Scarano et al. (2025)은 **XGBoost–SHAP과 통계모형을 결합한 방법론**이 가장 가까웠다.

## 2. Yang et al. (2022): 고속도로 사고 주제가 가장 가까운 연구

Yang, Y., Wang, K., Yuan, Z., and Liu, D. (2022), “Predicting Freeway Traffic Crash Severity Using XGBoost–Bayesian Network Model with Consideration of Features Interaction,” *Journal of Advanced Transportation*, 2022, Article 4257865.

- DOI: https://doi.org/10.1155/2022/4257865
- 출판사 원문: https://onlinelibrary.wiley.com/doi/10.1155/2022/4257865
- 교통연구 데이터베이스 기록: https://trid.trb.org/View/1946629

### 2.1 APTE와 유사한 부분

- 고속도로 교통사고의 심각도를 직접 분석한다.
- 도로·환경 요인을 XGBoost로 학습하고 SHAP으로 중요도와 영향 방향을 해석한다.
- SHAP 결과를 Bayesian network에 연결하여 도로와 환경 조건의 결합에 따른 사고 심각도 확률을 분석한다.
- 재산피해, 부상 및 사망사고를 구분하며, 최종 예측 정확도 89.05%를 보고한다.

### 2.2 원문에서 확인되는 한계

- 설명변수는 도로·환경 중심 11개로 구성되어 운전자·차량·사고기제의 동시 조정 범위가 제한적이다.
- 저자들은 표본 수가 작고 도로조건 변수가 충분하지 않다는 한계를 직접 제시한다.
- Grid Search CV로 XGBoost를 최적화하지만, 학습·모형선택·SHAP 탐색·최종 확인을 상호 배타적인 네 표본으로 분리한 절차는 보고하지 않는다.
- 상호작용 결과는 Bayesian network의 조건부 확률 시나리오로 제시되며, 조정 교호작용 OR, 강건 95% 신뢰구간, 독립 p값 및 FDR은 제공되지 않는다.
- 불균형 결과에 대한 PR-AUC 중심 선택, 확률보정, 검증표본에서 선택한 임계값의 고정 적용 및 bootstrap 불확실성 평가는 보고되지 않는다.

### 2.3 APTE가 추가한 방법론

APTE는 고속도로 사고 83,297건에서 운전자·차량·시설·사고기제를 포함한 17개 사전고정 범주형 변수를 사용하였다. 전체 표본을 다음 역할로 분리하였다.

| 표본 역할 | 비율 | n |
|---|---:|---:|
| 학습 | 50% | 41,648 |
| 모형선택·보정 | 15% | 12,494 |
| SHAP 후보 탐색 | 15% | 12,495 |
| 독립 통계확인 | 20% | 16,660 |

따라서 Yang et al.의 XGBoost–SHAP–Bayesian network 분석과 달리, APTE는 SHAP 상호작용을 확정 결과가 아닌 가설 후보로 취급하고 독립 확인표본의 HC3 강건 이항 GLM으로 다시 검정하였다. 또한 검정 가능한 후보군 전체에 Benjamini–Hochberg FDR을 적용하고, 결합 셀의 전체 표본·사건·비사건 최소기준을 사전에 적용하였다.

## 3. Scarano et al. (2025): 방법론적으로 가장 가까운 연구

Scarano, A., Sadeghi, M., Mauriello, F., Rella Riccardi, M., Aghabayk, K., and Montella, A. (2025), “Cyclist Crash Severity Modeling: A Hybrid Approach of XGBoost-SHAP and Random Parameters Logit with Heterogeneity in Means and Variances,” *Journal of Safety Research*, 93, 373–398.

- DOI: https://doi.org/10.1016/j.jsr.2025.04.003
- ScienceDirect 원문: https://www.sciencedirect.com/science/article/pii/S0022437525000611
- 저자 소속기관 원문 기록: https://www.iris.unina.it/handle/11588/1002918

### 3.1 APTE와 유사한 부분

- 영국 교통부의 2016–2019년 자전거 사고 72,363건과 39개 설명변수를 사용한다.
- XGBoost–SHAP으로 사고심각도 관련 변수를 선별한다.
- Random-parameters logit with heterogeneity in means and variances(RPLHMV)를 이용해 통계적 효과와 미관측 이질성을 분석한다.
- SHAP interaction plot으로 고정모수와 랜덤모수 변수 사이의 조건부 관계를 해석한다.

이 논문이 존재하므로 APTE는 “XGBoost–SHAP과 통계모형을 최초로 결합했다”고 주장할 수 없다.

### 3.2 원문에서 확인되는 한계

- 원문은 XGBoost를 전체 자료에 적용하고 normalized SHAP가 10%를 초과한 변수를 후속 RPLHMV에 투입한다고 설명한다.
- 즉, SHAP을 이용한 결과변수 기반 선별과 통계모형 적합이 동일 관측자료에서 연속적으로 이루어진다.
- SHAP 후보 탐색표본과 독립 통계확인표본의 분리는 보고되지 않는다.
- SHAP interaction plot에서 관찰된 조건부 패턴을 별도 표본의 교호작용 계수·OR·95% CI로 재검정하는 절차는 보고되지 않는다.
- 다수의 주효과·상호작용 검정에 대한 BH-FDR 등 다중검정 보정은 보고되지 않는다.
- 검증자료에서만 확률보정과 분류 임계값을 결정한 뒤 untouched 자료에 고정 적용하는 절차는 확인되지 않는다.
- 사망 범주의 F-measure가 0.07로 보고되어 희귀 결과 예측이 어렵지만, APTE와 같은 natural·weighted·RUS·SMOTEN 전략의 동일 validation 비교는 보고되지 않는다.

Scarano et al.의 강점은 다범주 사고심각도와 미관측 이질성을 RPLHMV로 직접 다룬다는 것이다. APTE가 전반적으로 우월하다고 주장해서는 안 되며, 독립 탐색–확인과 선택 후 추론 통제 측면의 확장으로 표현해야 한다.

### 3.3 APTE가 추가한 방법론

- 결과변수를 이용한 전체자료 사전 선별을 폐지하고 17개 설명변수를 사전에 고정하였다.
- 학습, 모형선택·보정, SHAP screening 및 confirmation의 표본 역할을 상호 배타적으로 분리하였다.
- Validation PR-AUC를 1차 모형선택 지표로 지정하였다.
- Validation에서만 Platt calibration과 F1 임계값 0.1528을 선택하고 confirmation에 고정 적용하였다.
- SHAP 후보 13개 중 사전 셀 안정성 기준을 충족한 6개를 검정하고, BH-FDR 후 3개 상호작용을 확인하였다.
- 최종 confirmation 표본에서 ROC-AUC 0.7799, PR-AUC 0.3146, F1 0.3532, Brier score 0.0851 및 calibration slope 1.0038을 보고하였다.
- Logistic 기준모형과의 차이를 1,000회 paired bootstrap으로 평가하였다.

## 4. 최종 비교

| 비교항목 | Yang et al. (2022) | Scarano et al. (2025) | APTE |
|---|---|---|---|
| 핵심 연구대상 | 고속도로 사고심각도 | 자전거 사고심각도 | 고속도로 사고조건부 인명피해 |
| XGBoost–SHAP | 적용 | 적용 | 적용 |
| 후속 분석 | Bayesian network | RPLHMV | HC3 강건 이항 GLM |
| SHAP screening 전용표본 | 보고되지 않음 | 없음: 전체자료 적용 | 독립 15% |
| 독립 confirmation | 보고되지 않음 | 보고되지 않음 | untouched 20% |
| 상호작용 통계확인 | 조건부 확률 시나리오 | SHAP plot 중심 | 조정 OR·95% CI·p값 |
| 다중검정 통제 | 보고되지 않음 | 보고되지 않음 | BH-FDR |
| 희소 결합셀 통제 | 보고되지 않음 | 보고되지 않음 | 사전 n·사건·비사건 기준 |
| 불균형 모형선택 | 정확도 중심 | 희귀 사망 F1 보고 | Validation PR-AUC |
| 확률보정·임계값 고정 | 보고되지 않음 | 보고되지 않음 | Validation-only 결정 |
| 최종 불확실성 | 정확도 보고 | 모형계수·적합도 | Bootstrap CI·paired 차이 |

## 5. 논문에 사용할 수 있는 차별성 문장

> 기존 고속도로 사고 연구는 XGBoost–SHAP과 Bayesian network를 이용하여 도로·환경 요인의 비선형성과 상호작용을 탐색하였으며(Yang et al., 2022), 최근 연구는 XGBoost–SHAP과 random-parameters logit을 결합하여 기계학습과 통계모형을 연계하였다(Scarano et al., 2025). 그러나 전자는 SHAP 상호작용에 대한 독립적인 통계적 확인을 제공하지 않았고, 후자는 전체 관측자료에서 SHAP 변수선별과 통계모형 적합을 연속적으로 수행하였다. 본 연구는 학습, 모형선택·확률보정, SHAP 후보 탐색 및 통계적 확인에 상호 배타적인 표본을 할당하고, 독립 확인표본에서 HC3 강건 로지스틱 회귀, 사전 셀 안정성 기준 및 Benjamini–Hochberg FDR을 적용했다는 점에서 차별화된다.

가장 보수적이고 방어 가능한 핵심 표현은 다음과 같다.

> 본 연구의 방법론적 차별성은 XGBoost, SHAP 또는 통계모형의 개별적 최초 적용이 아니라, 사고단위 인명피해 연구에서 예측–모형선택–설명–통계적 확인의 표본 역할을 분리하고 SHAP 탐색 결과를 독립 강건 추론과 다중검정 통제로 연결한 확인적 분석체계에 있다.

## 6. 사용하면 안 되는 주장

- “세계 최초” 또는 “국내 최초”
- “XGBoost–SHAP과 통계모형을 최초로 결합”
- “교통사고 상호작용을 최초로 분석”
- 무작위 confirmation 표본을 “외부 검증”으로 표현
- 관찰된 조정 연관성을 인과효과나 사고예방 효과로 확정
- 결과변수·분석단위·기저율이 다른 선행연구와 성능 수치를 직접 비교

현재 근거로는 “본 검토 범위에서 확인된 선행연구와 비교할 때, 독립적인 screening–confirmation 역할분리와 FDR·셀 안정성 통제를 결합했다”는 수준의 주장이 가장 타당하다.
