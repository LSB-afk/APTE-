---
title: "APTE Memo 08"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:42.838Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 08

# 메모 8 Fig 2 d의 정의

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 여기 제목에서 (d) 변수의 의미가 뭔가요? tollgate dummy??

## 연결 본문

Fig 2. Distribution of SHAP values for categorical variables: (a) Primary cause, (b) Crash location, (c) Driver age and (d) Tollgate dummy by vehicle type

## 출처

원본 HWPX의 MEMO 번호 8. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T20:19:45Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: Fig. 2(d)의 영업소 더미 일반 SHAP 정의·표본을 본문과 캡션에 명시
- 수정 근거: src/07_paper_figures.py:94~104, 원문 BinData/image2.bmp 직접 확인, [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 3절의 Fig. 2(d) 정의·표본.
- 추적 수정 위치·조치: S0 P38·P69·P72 에서 대표 시드 42 균형자료 17,986 건과 영업소 사고 네 차종별 영업소 더미 SHAP 분포를 구분했다. 평균 표시는 실제 흑백 그림과 맞게 Connected circles 로 설명했다.
- 검증 결과: 실제 제목 Tollgate dummy by vehicle type, y 축 SHAP value of tollgate dummy. 표본 승용 528·화물 450·트레일러 249·승합 90 이 코드·저장 PNG·삽입 BMP 와 일치한다.
- 잔여 확인사항: 학습·검증·평가를 합친 분포이며 순수 평가자료 그림이나 5 시드 평균이 아니다. 전체 SHAP 배열 재계산과 모든 점의 독립 수치 재현은 수행하지 않았다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
