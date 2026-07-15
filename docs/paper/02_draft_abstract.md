# 제목 후보 · 초록 초안

## 제목 후보

1. **XGBoost-SHAP 탐색과 확인적 통계 검정을 결합한 고속도로 교통사고 인명피해
   발생 요인 분석** (권장)
   - EN: *A Screening–Confirmation Framework Combining XGBoost-SHAP and
     Confirmatory Statistical Testing for Casualty Occurrence in Expressway Crashes*
2. 고속도로 교통사고 인명피해 발생의 비선형·상호작용 위험구조 분석: 설명가능
   기계학습과 통계적 검정의 2단계 접근
3. 사고 전 정보 기반 고속도로 인명피해 발생 예측과 위험요인의 조건부 구조 해석

## 국문 초록 (초안, 약 600자)

고속도로 교통사고의 인명피해 발생 요인을 규명하기 위해 2011~2019년 전국 고속도로
사고 83,297건을 분석하였다. 사고 결과로부터 파생되는 변수를 배제한 사고 전
(pre-accident) 변수 18개 후보에 대해 Cramér's V와 분산팽창계수(VIF) 기반 공선성
진단을 수행하여 최종 14개 변수를 선정하였고, 인명피해 발생(사망·중상·경상 1명
이상)을 이진 타겟으로 정의하였다(발생률 10.8%). 클래스 불균형은 1:1 랜덤
언더샘플링으로 처리하였으며, XGBoost 모형은 5회 반복 샘플링에서 ROC-AUC
0.785±0.005, F1-score 0.724±0.004의 안정적 성능을 보였다. 본 연구는 SHAP으로
탐색한 위험요인과 상호작용 후보를 다변량 로지스틱 회귀(오즈비)와 음이항
회귀(사상자 수)로 확인하는 탐색-확인 2단계 프레임워크를 제안한다. 세 모형의 효과
방향은 높은 일치율을 보였고(SHAP-로지스틱 82%, 로지스틱-음이항 공통 유의 더미
100%), FDR 보정 후 영업소(TG)×승용차(보호효과 이질성), 주시태만×본선(위험 증폭),
승합×대형(인명피해율 28.3%) 등의 상호작용이 통계적으로 확인되었다. 반면 SHAP
강도 상위였던 졸음×승용차 상호작용은 검정을 통과하지 못해, 기계학습 상호작용
지표의 단독 보고가 갖는 위험을 실증하였다. 분석 결과는 본선·터널 구간의 인적요인
관리와 화물·트레일러 중심의 감속 유도가 인명피해 저감에 우선순위가 높음을 시사한다.

**주요어**: 고속도로 교통사고, 인명피해 발생, XGBoost, SHAP, 상호작용효과,
클래스 불균형

## English Abstract (draft)

This study investigates factors associated with casualty occurrence in expressway
crashes using 83,297 nationwide crash records in South Korea (2011–2019). To
prevent target leakage, only pre-accident variables were considered; collinearity
diagnostics based on bias-corrected Cramér's V and variance inflation factors
reduced 18 candidates to 14 predictors. Casualty occurrence (at least one death
or injury; prevalence 10.8%) was modeled with XGBoost under 1:1 random
undersampling, yielding stable performance across five resampling seeds (ROC-AUC
0.785±0.005, F1-score 0.724±0.004). We propose a two-stage screening–confirmation
framework in which SHAP-based risk factors and interaction candidates are
subsequently verified by multivariable logistic regression (odds ratios) and
negative binomial regression (casualty counts). Effect directions were highly
consistent across the three models (82% between SHAP and logistic regression;
100% among dummies significant in both regressions). After FDR correction,
interactions such as tollgate×passenger-car (heterogeneous protective effect),
inattention×mainline (risk amplification), and van×large-class (28.3% casualty
rate) were statistically confirmed, whereas the drowsiness×passenger-car pair
— highly ranked by SHAP interaction strength — failed confirmation, demonstrating
the risk of reporting machine-learning interaction rankings alone. Findings
prioritize human-factor management on mainline and tunnel segments and speed
management for freight vehicles.

**Keywords**: expressway crash, casualty occurrence, XGBoost, SHAP, interaction
effect, class imbalance

---
`[확인 필요]` ① "인명피해 발생/casualty occurrence" 용어 확정 (APTE 초록은 injury
occurrence) ② 분량 규정에 따른 초록 축약 ③ 공저자·소속 표기
