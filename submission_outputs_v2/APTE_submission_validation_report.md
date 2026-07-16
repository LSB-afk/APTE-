# APTE 학술논문 투고 가능성 검증 및 보완 결과 보고서

검증일: 2026-07-16
대상 연구: 고속도로 교통사고 인명피해 발생의 예측·설명·상호작용 분석
목표 학술지: *Journal of Korean Society of Transportation* (대한교통학회지)

## 1. 최종 판단

본 연구는 최초 원고 상태에서는 학술논문 투고가 곤란했으나, 분석 설계를 전면 수정하고 모든 핵심 결과를 다시 계산한 현재 상태에서는 **방법론과 결과 측면에서 투고 가능한 원고를 작성할 수 있는 단계**에 도달했다.

판단 근거는 다음과 같다.

1. 전체 83,297건을 학습, 검증, SHAP 탐색, 독립 확인표본으로 분리하여 탐색과 통계적 확인의 표본 중복을 제거했다.
2. 결과변수를 이용한 전체자료 사전 변수선택을 폐기하고, 사전에 정의한 17개 설명변수를 유지했다.
3. 모델 선택, 확률 보정, 분류 임계값 선택을 검증표본에서 완료한 뒤 독립 확인표본에서는 단 한 번 최종 성능을 계산했다.
4. GitHub 저장소만으로 재현할 수 없던 사상자 수 음이항 회귀를 논문 범위에서 제외하고, 재현 가능한 인명피해 발생 여부 분석으로 연구 질문을 정렬했다.
5. 데이터 출처, 분석 코드, 패키지 버전, 무작위 시드, 원자료 해시, 주장–근거 파일의 연결을 명시했다.

다만 이 연구는 교통사고 발생자료만을 분석하므로, 결과는 “사고 발생 위험”이 아니라 **사고가 발생했다는 조건 아래 인명피해가 동반될 조건부 확률**에 관한 것이다. 연도, 교통노출량, 도로구간 식별자, 원시 시스템 사고 ID가 없어 시간·공간적 외부검증과 군집상관 보정은 수행하지 못했다. 따라서 모든 추정치는 인과효과가 아닌 조정된 관찰 연관성으로 표현해야 한다.

## 2. 제출을 막던 핵심 결함 5가지와 보완

### 2.1 탐색표본과 확인표본의 중복

기존 분석은 SHAP으로 상호작용 후보를 찾은 표본이 로지스틱 회귀 확인자료에 다시 포함되어 있었다. 이 구조에서는 사후선택 편향 때문에 p값과 FDR을 확인적 근거로 해석하기 어렵다.

보완 후 설계는 다음과 같다.

| Role | Proportion | n | Casualty n | Prevalence |
|---|---:|---:|---:|---:|
| Training | 50% | 41,648 | 4,496 | 10.80% |
| Validation | 15% | 12,494 | 1,349 | 10.80% |
| SHAP screening | 15% | 12,495 | 1,349 | 10.80% |
| Independent confirmation | 20% | 16,660 | 1,799 | 10.80% |

SHAP 후보 탐색은 screening 표본에서만 수행했고, 주효과와 상호작용의 추정·검정은 독립 confirmation 표본에서만 수행했다. 상호작용 후보 13개 중 확인표본의 안정성 기준을 충족한 6개만 검정했으며, 이 6개 전체에 Benjamini–Hochberg FDR을 적용했다.

근거: `tables/table01_split_summary.csv`, `tables/interaction_candidates_screening_only.csv`, `tables/table07_independent_interaction_confirmation.csv`

### 2.2 결과변수 기반 사전 변수선택 누출

기존 분석은 전체 자료에서 결과변수와의 연관성을 계산해 변수를 고른 뒤 자료를 분할했다. 이는 확인표본의 결과정보가 모델 설계에 간접적으로 들어가는 정보 누출이다.

보완 분석에서는 최종 변수 개수를 결과값으로 결정하지 않았다. 기존 14개 변수와 행 순서·결과벡터 일치 검증을 통과한 주말 여부, 포장구분, 성별을 합쳐 17개 변수를 사전에 유지했다. 주야구분은 조명시설의 `해당없음(주간)` 범주와 구조적으로 중복되므로 결과변수와 무관한 사전 규칙으로 제외했다. 범주 인코더는 학습표본에서만 적합했다.

근거: `reproducibility_manifest.json`, `data/analysis_dataset_v2.csv`, `analysis_v2/submission_analysis.py`

### 2.3 테스트표본 임계값 최적화

기존 F1은 테스트표본에서 직접 최적 임계값을 찾아 계산한 값이어서 독립 성능으로 볼 수 없었다.

보완 분석에서는 각 모델의 Platt 확률보정과 F1 최대 임계값을 validation 표본에서 선택하고 고정했다. 선택된 XGB_natural의 임계값은 0.1528이며, 이 값을 untouched confirmation 표본에 그대로 적용했다. 최종 F1은 0.3532(95% CI 0.3401–0.3659)이다.

근거: `tables/table02_validation_model_selection.csv`, `tables/table03_confirmation_performance_ci.csv`

### 2.4 원자료·코드·분석범위 불일치

저장소의 부분 원자료에는 실제 사상자 수가 없고 사망·중상·경상 발생 플래그만 있다. 따라서 기존 음이항 사상자 수 모형은 저장소만으로 재현할 수 없다. SMOTEN 결과도 생성 코드와 결과 파일이 완결되지 않았다.

보완 분석은 다음과 같이 범위를 정리했다.

- 결과변수: 사망, 중상, 경상 중 하나 이상이 발생한 사고의 이항 지표
- 전체 사고: 83,297건
- 인명피해 사고: 8,993건
- 인명피해 발생률: 10.796%
- 재현 불가능한 사상자 수 음이항 회귀: 삭제
- SMOTEN: 학습표본에만 적용하는 실행 코드를 새로 포함하고 비교모형으로 재계산
- 원자료 정합성: 처리자료와 부분 원자료의 행 수 및 결과벡터 일치율 100% 확인

세 변수는 원시 사고 ID가 아닌 보존된 행 위치로 복원했으므로 이 점은 데이터 계보의 한계로 공개한다. `analysis_id`는 재현을 위한 결정적 ID이며 원 시스템의 사고 ID가 아니다.

공식 데이터 출처: [Public Data Portal – Expressway Traffic Accident Data](https://www.data.go.kr/data/100298914/linkedData.do)

근거: `reproducibility_manifest.json`, `analysis_v2/README.md`, `analysis_v2/submission_analysis.py`

### 2.5 출처·문헌·미완성 문구

기존 PDF의 출처 미기재, 국내 선행연구 부족, `[확인 필요]` 문구를 제거했다. 원고는 데이터 출처와 방법론 문헌을 명시하며, 참고문헌은 목표 학술지 규정에 맞춰 영문·저자 알파벳순으로 작성한다.

목표 학술지 규정: [JKST Instructions for Authors](https://www.jkst.or.kr/journal-information/instructions-for-authors/)

## 3. 재분석 방법의 근거

### 3.1 연구대상과 결과변수

분석자료는 고속도로 교통사고 83,297건이다. 사망 1,968건, 중상 1,635건, 경상 5,390건의 플래그 합은 인명피해 사고 8,993건과 정확히 일치한다. 결과변수는 사고별 인명피해 발생 여부이며, 전체 발생률은 10.796%이다.

### 3.2 후보모형과 불균형 처리

비교모형은 Logistic, XGB_natural, XGB_weighted, XGB_RUS, XGB_SMOTEN이다. 과소표집과 SMOTEN은 학습표본에만 적용했다. 모델 선택의 1차 지표는 양성 비율이 10.8%인 자료의 특성을 반영해 validation PR-AUC로 사전 지정했다.

Validation 결과:

| Model | ROC-AUC | PR-AUC | Recall | F1 | Brier |
|---|---:|---:|---:|---:|---:|
| XGB_natural | 0.7758 | **0.3108** | 0.5738 | 0.3533 | 0.0855 |
| XGB_weighted | 0.7757 | 0.3070 | 0.4974 | 0.3492 | 0.0857 |
| XGB_RUS | 0.7712 | 0.2985 | 0.4618 | 0.3517 | 0.0862 |
| Logistic | 0.7694 | 0.2913 | 0.5552 | 0.3476 | 0.0864 |
| XGB_SMOTEN | 0.7102 | 0.2348 | 0.4559 | 0.2920 | 0.0907 |

XGB_natural이 가장 높은 validation PR-AUC를 보여 최종 모델로 선택되었다. 인위적 균형화가 반드시 성능을 개선하지 않았다는 점도 확인되었다.

### 3.3 독립 확인표본 성능

Confirmation 표본 16,660건에서 XGB_natural의 성능은 다음과 같다.

| Metric | Estimate | 95% bootstrap CI |
|---|---:|---:|
| ROC-AUC | 0.7799 | 0.7694–0.7899 |
| PR-AUC | 0.3146 | 0.2953–0.3350 |
| Accuracy | 0.7745 | 0.7681–0.7804 |
| Balanced accuracy | 0.6848 | 0.6726–0.6969 |
| Precision | 0.2559 | 0.2463–0.2649 |
| Recall | 0.5703 | 0.5464–0.5937 |
| Specificity | 0.7992 | 0.7927–0.8053 |
| F1 | 0.3532 | 0.3401–0.3659 |
| Brier score | 0.0851 | 0.0839–0.0863 |

Calibration intercept는 0.0006, slope는 1.0038로 독립 확인표본에서 평균 수준과 확률 기울기가 이상적 기준에 가까웠다.

동일 confirmation 표본의 paired bootstrap에서 XGB_natural은 Logistic보다 ROC-AUC가 0.0059(95% CI 0.0028–0.0090), PR-AUC가 0.0116(0.0051–0.0189) 높았고 Brier score가 0.00072 낮았다. 세 차이는 bootstrap p<0.001이었다. 반면 F1 차이는 −0.0045(−0.0111–0.0025, p=0.216)로 유의하지 않았다.

따라서 근거에 맞는 결론은 다음과 같다.

> XGBoost는 로지스틱 회귀보다 독립 확인표본의 순위 판별과 확률오차에서 작지만 재현 가능한 개선을 보였으나, 고정 임계값의 F1 우위는 확인되지 않았다.

근거: `tables/table03_confirmation_performance_ci.csv`, `tables/table04_paired_model_differences.csv`

## 4. 주효과 결과의 학술적 의미

독립 confirmation 표본의 HC3 강건 로지스틱 회귀에서 주효과 더미 27개가 BH q<0.05였다. 아래는 표본 수와 해석 가능성을 함께 고려한 핵심 결과다.

| Contrast | Adjusted OR | 95% CI | Observed casualty rate | BH q |
|---|---:|---:|---:|---:|
| Stopped vehicle vs no obstruction | 2.893 | 2.234–3.745 | 35.67% | <0.001 |
| Congestion vs no obstruction | 3.170 | 2.300–4.370 | 38.10% | <0.001 |
| Lane change vs lane keeping | 2.029 | 1.527–2.695 | 25.94% | <0.001 |
| Drowsiness vs speeding | 1.839 | 1.497–2.258 | 20.83% | <0.001 |
| Inattention vs speeding | 1.668 | 1.390–2.002 | 16.03% | <0.001 |
| Insufficient headway vs speeding | 1.682 | 1.219–2.322 | 20.60% | 0.007 |
| Truck vs passenger car | 1.800 | 1.554–2.086 | 15.05% | <0.001 |
| Van vs passenger car | 1.882 | 1.513–2.340 | 14.89% | <0.001 |
| Trailer vs passenger car | 2.444 | 1.401–4.263 | 11.11% | 0.007 |
| Large vs medium vehicle class | 1.280 | 1.083–1.513 | 12.69% | 0.012 |
| Tollgate vs mainline | 0.117 | 0.086–0.159 | 2.79% | <0.001 |
| Ramp vs mainline | 0.304 | 0.245–0.377 | 4.27% | <0.001 |

정차차량과 정체가 동반된 사고의 높은 조정 오즈, 차로변경·졸음·주시태만·안전거리미확보의 양의 연관성은 충돌 회피시간, 속도차, 차량 제어 실패와 관련된 안전관리 우선순위를 제시한다. 화물·승합·트레일러 및 대형 차급의 양의 연관성은 차량 질량과 구조 차이를 고려한 차종 맞춤형 대응의 필요성을 뒷받침한다.

영업소와 램프의 낮은 조정 오즈는 속도·기하구조·교통구성·사고신고체계가 다른 구간의 관찰 연관성이다. 이를 시설 자체의 인과적 “보호효과”로 해석해서는 안 된다. 노면잡물, 포트홀, 낙하물, 단독차량화재 등의 매우 낮은 OR은 확인표본의 사건 수가 적고 사고유형 구성이 다르므로 본문 핵심 정책결론에서 제외하고 부록에만 제시한다.

근거: `tables/table05_confirmation_main_effects.csv`, `figures_en/Figure_6_main_effects.png`

## 5. 독립 상호작용 확인

SHAP screening 표본에서 사전 선별한 13개 후보 중 confirmation 안정성 기준을 충족한 6개를 검정했고, 3개가 BH q<0.05였다.

| Interaction | OR ratio | 95% CI | Joint n | Joint casualty rate | BH q |
|---|---:|---:|---:|---:|---:|
| Van × large class | 3.007 | 1.877–4.815 | 187 | 28.88% | <0.001 |
| Inattention × tollgate | 0.411 | 0.228–0.741 | 866 | 2.42% | 0.008 |
| Tollgate × small class | 2.638 | 1.362–5.112 | 268 | 5.22% | 0.008 |

가장 강하고 해석 가능한 결과는 승합차이면서 대형 차급인 조합이다. 둘 다 아닌 사고의 인명피해율은 10.49%, 승합만 11.11%, 대형만 11.14%였으나 두 조건이 동시에 존재하면 28.88%(54/187)였다. 주효과만으로 설명되는 기대보다 결합 연관성이 약 3.01배 강했다.

`Inattention × tollgate`의 OR ratio 0.411은 주시태만의 조정 연관성이 본선보다 영업소에서 약화되었다는 뜻이지, 주시태만이 영업소에서 안전하다는 뜻이 아니다. `Tollgate × small class`의 OR ratio 2.638은 영업소의 낮은 오즈 연관성이 소형 차급에서는 덜 강하다는 의미다. 두 조합의 관찰 인명피해율은 각각 2.42%, 5.22%로 전체 평균보다 낮다.

영업소×트레일러 후보는 confirmation 결합 셀의 인명피해가 4건뿐이어서 사전 안정성 규칙에 따라 검정에서 제외했다. 따라서 이 조합을 논문의 확인된 결과로 주장해서는 안 된다.

근거: `tables/table07_independent_interaction_confirmation.csv`, `tables/table08_top_confirmed_interaction_rates.csv`, `figures_en/Figure_7_interactions.png`, `figures_en/Figure_8_van_large_rates.png`

## 6. 논문에 사용할 수 있는 핵심 주장과 직접 근거

| ID | Manuscript claim | Evidence |
|---|---|---|
| C01 | 자료는 83,297건이며 인명피해 사고는 8,993건(10.80%)이다. | `data/analysis_dataset_v2.csv` |
| C02 | 학습·검증·SHAP 탐색·독립 확인의 네 표본 역할을 분리했다. | `tables/table01_split_summary.csv` |
| C03 | XGB_natural의 confirmation ROC-AUC는 0.780(95% CI 0.769–0.790)이다. | `tables/table03_confirmation_performance_ci.csv` |
| C04 | confirmation 강건 로지스틱 회귀에서 주효과 27개가 BH q<0.05였다. | `tables/table05_confirmation_main_effects.csv` |
| C05 | SHAP 후보 13개 중 6개가 안정성 기준을 충족했고 3개 상호작용이 독립 확인되었다. | `tables/table07_independent_interaction_confirmation.csv` |

기계 판독용 매핑: `tables/claim_evidence_map.csv`

## 7. 표·그림과 본문 흐름의 일치

| Item | Function in manuscript | Main evidence |
|---|---|---|
| Figure 1 | 네 표본의 역할과 정보 흐름을 설명 | `Figure_1_independent_design.png` |
| Figure 2 | untouched confirmation의 ROC/PR 성능 비교 | `Figure_2_confirmation_roc_pr.png` |
| Figure 3 | 예측확률 보정 상태 확인 | `Figure_3_confirmation_calibration.png` |
| Figure 4 | 모델별 확인표본 성능과 불확실성 비교 | `Figure_4_model_metrics.png` |
| Figure 5 | screening 표본에서만 계산한 SHAP 중요도 | `Figure_5_screening_shap.png` |
| Figure 6 | confirmation 주효과 OR와 95% CI | `Figure_6_main_effects.png` |
| Figure 7 | 검정 가능한 6개 상호작용의 OR ratio와 FDR | `Figure_7_interactions.png` |
| Figure 8 | 최상위 승합×대형 상호작용의 네 셀 관찰률 | `Figure_8_van_large_rates.png` |

논문의 흐름은 “예측모형 선택 → 독립 성능평가 → 탐색표본 SHAP → 독립표본 주효과·상호작용 확인 → 교통안전 해석”으로 고정한다. SHAP은 후보 생성과 모델 설명에만 사용하고, 통계적 확인은 강건 로지스틱 회귀와 BH-FDR에만 근거한다.

## 8. 남은 한계와 투고 시 필수 표현

1. 사고자료만 포함하므로 일반 운행 중 사고발생 위험을 추정하지 않는다.
2. 교통량·주행거리·차량등록대수 등 노출량이 없어 차종·시설별 절대위험을 비교하지 않는다.
3. 연도와 도로구간 ID가 없어 시간·공간적 외부검증을 수행하지 못했다.
4. 무작위 독립표본 확인은 내부 재현성을 강화하지만 미래 연도나 다른 고속도로망에 대한 외부 타당성을 보장하지 않는다.
5. 행 위치로 복원한 세 변수는 원시 사고 ID 결합보다 데이터 계보가 약하다.
6. 범주형 변수의 일부 희소 셀과 완전분리가 있어 소표본 대비는 부록 중심으로 다룬다.
7. 관찰자료이므로 OR, SHAP, 상호작용은 모두 연관성이며 인과효과가 아니다.

## 9. 재현성

- 분석 시드: 20260716
- Bootstrap: 1,000회, 계층화 재표집
- Python: 3.12.13
- pandas: 3.0.1
- numpy: 2.3.5
- scipy: 1.18.0
- scikit-learn: 1.9.0
- xgboost: 3.3.0
- shap: 0.52.0
- statsmodels: 0.14.6
- imbalanced-learn: 0.14.2
- matplotlib: 3.11.0

재현성 manifest: `reproducibility_manifest.json`
분석 코드: `analysis_v2/submission_analysis.py`
영문 그림 코드: `analysis_v2/submission_figures_en.py`

## 10. 최종 투고 준비도

### 학술 내용

**투고 가능.** 분석 질문, 데이터 범위, 모델 성능, 통계적 확인, 시각화, 한계가 서로 일치하며 핵심 수치는 모두 결과 파일에 직접 연결된다.

### 투고 전 행정 단계

다음은 분석 결함이 아니라 저자가 제출 시스템에서 완료해야 하는 행정 항목이다.

- 저자명, 소속, ORCID, 교신저자 정보
- 대한교통학회 회원 요건 확인
- 연구비, 이해상충, 저자기여 진술
- 목표 학술지의 최신 HWP 서식에 최종 편집
- 원자료 공개 가능 범위와 기관 승인 여부 확인

이 항목을 제외하면, 본 재분석 결과는 과장 없이 학술논문 본문에 사용할 수 있다.
