---
title: "APTE Memo 05"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:42.511Z
updated: 2026-11-03T05:46:34Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 05

> **2026-11-03 전수 재검토 우선 기록:** 현재 판정·파일·인용 매핑은 [[apte-full-rereview]]와 [최신 검토 보고서](../docs/paper/revisions/2026-11-02/전수재검토보고서.md)를 따른다. 아래 이전 날짜의592범위·SMOTEN보존·특정출전보류 기록은 당시 스냅샷이다.


# 메모 5 SHAP 수치와 그림의 대응

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 아래 그림에서 이 값들을 어떻게 확인할 수 있을까요?

## 연결 본문

　이러한 결과를 바탕으로 개별 요인의 기여뿐만 아니라 두 요인이 결합할 때 나타나는 상호작용을 파악하기 위해 SHAP 상호작용 값을 분석하였다. 전체 사고를 기준으로 영업소-승용(0.025), 주시태만-승용(0.022), 주시태만-본선(0.019)이 높은 상호작용 기여도를 보였으며, 두 조건이 동시에 관측된 사고를 기준으로는 영업소-승용(0.286), 노면잡물-조명시설 없음(0.193), 주시태만-영업소(0.170) 등이 높게 나타났다. 특히 영업소–승용 조합은 두 기준 모두에서 높은 상호작용 기여도를 보여 주요 상호작용 후보로 확인되었다. 최종적으로 이러한 분석 결과를 바탕으로 24개의 상호작용 후보를 선정하고, 후속 통계적 검정에 활용하였다.

## 출처

원본 HWPX의 MEMO 번호 5. 작성자 필드 `user`, 저장 시각 `2026-10-14T15:41:36Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 그림에서 읽을 수 없는 여섯 상세 수치 추적 삭제; 근거는 별도 검토표에 유지
- 수정 근거: [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 3절·[데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md) 3절, interaction_profile.csv 및 src/05_interaction_deep.py, src/07_paper_figures.py.
- 추적 수정 위치·조치: S0 P70 의 .025/.022/.019 및 .286/.193/.170 은 Fig. 2 의 일반 SHAP 그림에서 읽을 수 없어 본문에서 추적 삭제했다. 여섯 값은 [데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md) 3절의 별도 검토표에, 24쌍 전체의 집계는 [interaction_profile.csv](../outputs/tables/interaction_profile.csv)에 보관했다.
- 검증 결과: 저장 지표값은 확인했으나 Fig. 2 의 값인 것처럼 인용하지 않는다. 원문 그림은 일반 SHAP 분포, A/B 는 별도의 쌍별 interaction 지표다.
- 잔여 확인사항: 새 본문 부록표를 추가했다고 인용하지 않는다. Fig. 2 전체 17,986 건 SHAP 배열은 재계산하지 않았다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
