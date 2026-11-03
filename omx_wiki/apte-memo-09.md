---
title: "APTE Memo 09"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:42.949Z
updated: 2026-11-03T05:46:34Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 09

> **2026-11-03 전수 재검토 우선 기록:** 현재 판정·파일·인용 매핑은 [[apte-full-rereview]]와 [최신 검토 보고서](../docs/paper/revisions/2026-11-02/전수재검토보고서.md)를 따른다. 아래 이전 날짜의592범위·SMOTEN보존·특정출전보류 기록은 당시 스냅샷이다.


# 메모 9 효과 방향 일치율의 근거

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 이 내용들은 어디서 확인할 수 있을까요?
> 여기 아직 못고친 파트라 메모 남겨두세요.

## 연결 본문

　SHAP의 기여 방향과 로지스틱 회귀계수의 부호를 비교한 결과, 56개 더미변수 중 46개(82.1%)에서 방향이 일치하였다. 로지스틱 회귀에서 통계적으로 유의한 41개 더미변수로 한정한 경우에는 34개(82.9%)가 일치하였다. 방향의 불일치는 대부분 효과의 크기가 작은 변수에서 나타났다. 이는 SHAP이 모형의 기준 예측값을, 오즈비가 변수별 기준범주를 비교 기준으로 사용한다는 차이에서 비롯되었을 가능성이 있다. 다만 이러한 일치 여부는 방향에 관한 것으로, 효과의 크기나 관계의 형태까지 동일함을 의미하지는 않는다.

## 출처

원본 HWPX의 MEMO 번호 9. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T20:34:57Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 분모·근거 명시 및 과장 해석 수정; 원문 메모 보존, 저자 최종 판단 유지
- 수정 근거: shap_lr_direction_agreement.csv 직접 집계, src/04_confirmatory_stats.py:129~143, [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 4절의 방향 비교 표.
- 추적 수정 위치·조치: S0 P98 에 비교 가능한 56 개 중 46 개, LR 유의 41 개 중 34 개를 명시했다. 작은 효과에서만 불일치한다는 일반화와 모형 타당성 입증 해석을 제거했다.
- 검증 결과: 46/56=82.1%, 34/41=82.9%. 터널 등 큰 SHAP 기여도에서도 불일치하므로 단순한 작은 효과 설명은 충분하지 않다.
- 잔여 확인사항: “여기 아직 못고친 파트라 메모 남겨두세요”를 포함한 메모 원문을 그대로 보존했다. 근거 확인을 작성자의 최종 검토 완료로 대체하지 않는다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
