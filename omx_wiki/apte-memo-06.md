---
title: "APTE Memo 06"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:42.621Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 06

# 메모 6 상호작용 후보 24개 선정

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 위 설명을 기반으로 했을 때 값이 24개가 아닌거 같은데, 설명 보완 필요(너무 길게 말고 간결하게)

## 연결 본문

　이러한 결과를 바탕으로 개별 요인의 기여뿐만 아니라 두 요인이 결합할 때 나타나는 상호작용을 파악하기 위해 SHAP 상호작용 값을 분석하였다. 전체 사고를 기준으로 영업소-승용(0.025), 주시태만-승용(0.022), 주시태만-본선(0.019)이 높은 상호작용 기여도를 보였으며, 두 조건이 동시에 관측된 사고를 기준으로는 영업소-승용(0.286), 노면잡물-조명시설 없음(0.193), 주시태만-영업소(0.170) 등이 높게 나타났다. 특히 영업소–승용 조합은 두 기준 모두에서 높은 상호작용 기여도를 보여 주요 상호작용 후보로 확인되었다. 최종적으로 이러한 분석 결과를 바탕으로 24개의 상호작용 후보를 선정하고, 후속 통계적 검정에 활용하였다.

## 출처

원본 HWPX의 MEMO 번호 6. 작성자 필드 `user`, 저장 시각 `2026-10-14T15:42:23Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 15+15−중복 6=24 선정 규칙을 방법·결과에 반영
- 수정 근거: interaction_profile.csv 24 행의 두 top15 플래그 재집계, src/05_interaction_deep.py:101, [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 3절·[데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md) 1절.
- 추적 수정 위치·조치: S0 P39·P70 에 A/B 각 상위 15 쌍의 합집합이며 6 쌍 중복으로 24 쌍임을 간결하게 적었다. 평가자료 3,598 건 중 추출 2,000 건, B 의 동시 관측 최소 30 건, 대칭 성분 2 배 계수도 구분했다.
- 검증 결과: A 만 9, B 만 9, 중복 6, 합집합 24. 24 쌍 모두 후속 회귀 검정, BH q<.05 인 13 쌍과 비유의 11 쌍을 구분했다.
- 잔여 확인사항: 탐색과 검정의 관측치가 중복된다. FDR 보정만으로 독립 검증이나 선택 후 추론 문제가 해결됐다고 쓰지 않는다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
