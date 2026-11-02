---
title: "APTE Methods Results Map"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:42:46.479Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-revision-hub.md", "apte-professor-memos.md", "apte-data-evidence.md", "apte-memo-11.md", "apte-validation-log.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Methods Results Map

# 연구방법론과 결과 대응

[[apte-revision-hub]] · [[apte-professor-memos]] · [[apte-data-evidence]]

## 메모 11의 반영 결과

| 연구방법 | 대응 결과 | 반영·검증 내용 |
|---|---|---|
| 3.2 | 4.1 | 후보 18→14 변수, VIF 최대 5.46·평균 1.48(기준범주 제외 72개 더미, 포트홀 포함) |
| 3.3 | 4.1~4.2 | 5 시드 반복 홀드아웃 성능, 일반 SHAP 과 A/B 상호작용 후보 15+15−6=24 구분 |
| 3.4 | 4.3 | 카이제곱, 71 주효과 더미·상수 로지스틱, 후보별 곱항·24 검정 BH 보정 |
| 신규 3.5 | 4.4 | 노선명 그룹·이정 군집·거리·56,309 본선 사고·Wilson95%CI 의 기술적 보조 분석 |
| 3.4 | 4.5 | NB IRR3 개·CI, SHAP–LR46/56·34/41 및 LR–NB 공통 유의 47/47 |

### 서로 다른 분석 표본

회귀·기술통계 83,297 건, 대표 균형자료 17,986 건, 외부 개발 14,388/평가 3,598 건, 실제 적합 12,229/조기종료검증 2,159 건, interaction 추출 2,000 건, TG 거리 56,309 건을 구분했다. Fig.2 는 전체 균형자료의 일반 SHAP, 방향 비교는 평가자료의 범주별 30 건 이상에서 산출한 SHAP 다.

### 신규 반복 검증

LR/Poisson→고정 αNB 및 단일 주시태만×영업소를 동일 설계로 재적합했다. 모두 수렴하고 저장 CSV 와 반올림폭 이내로 일치했다. pseudo R²원값.1484638717→.148, α3.4338328130, 상호작용 원계수−.9345008795→−.935 를 수정본에 반영했다. NB 용 pseudo R²를 새로 만들지 않았다. [[apte-data-evidence]]와 [[apte-memo-11]] 참조.

### 해석 경계와 상태

거리별 분석은 교통노출 보정 위험이나 인과효과가 아니다. NB IRR 는 사고당 기대 사상자 수의 비다. 변수 선정과 탐색·검정 관측치 중복을 독립 검증으로 설명하지 않는다. 방법–결과 대응과 수용 텍스트의 수치를 확인했으며 최종 지면 검토는 [[apte-validation-log]]에서 진행 상태를 갱신한다. 연구 방향의 최종 판단은 저자에게 남긴다.

### VIF와 회귀 설계의 구분

`src/01_preprocess.py:443`의 VIF는 기준범주만 제외한 **72개 더미(포트홀 열 포함)**에서 계산했다. 이후 회귀에서만 완전분리 포트홀 더미 열을 제외하여 **71개 더미+상수**가 된다. 두 설계행렬이 같다고 쓰지 않는다. 이 구분은 최신 P33에 반영되었으며 현재 추적 수 592개/논리 변경 205개는 변하지 않았다.
