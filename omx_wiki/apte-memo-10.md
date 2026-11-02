---
title: "APTE Memo 10"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:43.058Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 10

# 메모 10 거리별 분석 그림 제목

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 위 제목이 해석이 애매한데...
> Mainline casualty occurrence rates and crash counts by distance to the nearest tollgate 이걸 의미하는 걸까요? 아님 다른??

## 연결 본문

Fig 5.  Casualty occurrence rate and number of mainline crashes by distance to the nearest tollgate

## 출처

원본 HWPX의 MEMO 번호 10. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T20:38:00Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: Fig. 5 제목·거리 정의·분모 한정 반영
- 수정 근거: src/08_tg_distance_gradient.py, tg_distance_gradient.csv, [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 3·4절의 거리 분석 정의·표본.
- 추적 수정 위치·조치: S0 P95 캡션을 Mainline casualty occurrence rates and crash counts by distance to the nearest estimated tollgate 로 정리했다. P87·P88 에서 동일 노선명 그룹의 추정 영업소 이정과의 최소 절대 차이로 정의했다.
- 검증 결과: 46 개 노선명 그룹, 추정 위치 331 개, 분석 본선 56,309 건·양성 7,472 건. 7 개 비율·7 개 사고수·평균 13.3%는 그림·CSV 와 일치한다.
- 잔여 확인사항: 실제 주행 경로·방향 거리나 교통노출 보정 위험이 아니다. 1km 이내가 아니라 1km 미만이며 평균은 포함 표본의 평균이다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
