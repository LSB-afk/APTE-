---
title: "APTE Memo 13"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:43.385Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 13

# 메모 13 결론과 연구 방향 확인

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 제가 여기를 다시 썼는데, 승보가 생각하는 위 연구 방향성 및 연구 결과가 맞는지 확인 필요합니다.

## 연결 본문

5. 결 론

## 출처

원본 HWPX의 MEMO 번호 13. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T21:16:25Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 결론을 조건부 연관·기술적 비교로 한정; 연구 방향 최종 판단은 저자에게 유지
- 수정 근거: S0 P103~107, [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 및 [데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md), 저장 성능·회귀 결과.
- 추적 수정 위치·조치: 트레일러·승합을 대형 차종과 혼동한 표현을 정리하고, 인명피해 조건부 연관·상호작용·일치율의 분모를 명시했다. TG 결과를 감속의 인과적 보호효과로 단정하지 않도록 수정했다.
- 검증 결과: 24 후보/13 유의, 46/56·47/47, 균형 5 회 평균 AUC.785/F1.724, 승합×대형의 28.3%가 저장 결과와 부합한다.
- 잔여 확인사항: 교수의 재작성 방향이 저자의 의도와 일치하는지에 대한 최종 판단은 대체하지 않는다. P106 은 “추론 문제가 해소되거나 독립 표본에서의 재현 가능성이 확보되는 것은 아니다”로 명확히 했다. 관측자료, 교통노출 부재, 변수 선정·탐색/검정 표본 중복, 범주 코딩 한계를 보존한다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
