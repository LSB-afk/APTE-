---
title: "APTE Memo 12"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:43.276Z
updated: 2026-11-03T05:21:51Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/구조검증기록.md"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md", "apte-font-repair.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 12

# 메모 12 변경내용 추적

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 승보가 수정하는 모든 부분들은 변경내용 추적으로 작업해주세요.

## 연결 본문

고속도로 교통사고 인명피해 발생 관련 요인 분석: XGBoost-SHAP과 통계적 검정을 기반으로

## 출처

원본 HWPX의 MEMO 번호 12. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T21:08:39Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: native 추적 205 개 논리 변경·592 범위, 한글 열기·17 쪽 PDF 출력 성공
- 수정 근거: [파일식별정보](../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json), [문서검증결과](../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json), [구조검증기록](../docs/paper/revisions/2026-11-02/구조검증기록.md) 및 리더 native 실행 결과.
- 추적 수정 위치·조치: 본문·표·인용의 174 개 논리 변경에 빈 문단 31 개 native 삭제를 더해 205 개, 총 592 개 추적 범위를 작성했다. 별도 수정 HWPX 이며 원본 SHA 는 보존했다.
- 검증 결과: 메모 13·수식 24·그림 5·표격자 6, Table1 의 88 행/176 숫자 보존. section1 마지막 필수 문단끝 삭제의 paraend=1 이 Mac 한글 멈춤 원인으로 격리되어 그 끝만 0 으로 보존하자 정상 열렸다. 17 쪽 PDF 출력 성공.
- 잔여 확인사항: 앱이 읽기전용이어서 native 변경 수용·거부 UI 는 미시험이다. XML 파서의 수용/거부 텍스트 검증과 UI 검증을 구별한다. 최종 17쪽 페이지 검토 통과.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]

### 최종 앱·패키지 확인

최신 592개 범위/205개 논리 변경 파일의 17쪽 시각 검토를 통과했다. OS 미리보기 텍스트·첫 페이지 이미지(724×1024)·문서 메타를 갱신해 오래된 미리보기 문제를 해소했고, 최종 한글 재열기에서 1/17쪽 표시를 확인했다. 캐시 갱신 전후 header/section0/section1의 SHA는 동일하며 원본 대비 총 6개 패키지 부품이 달라졌다. 최종 SHA는 [[apte-source-register]]에 등록했다. native 수용·거부 UI는 여전히 미시험이다.


## 2026-11-03 글꼴 복구

추적 삽입문 56개 범위의 글꼴을 교정하면서 기존 592개 추적 범위와 마커를 보존하였다. 기존·삭제 글자의 문자별 서식도 유지하였다. 현재 파일·해시와 교차 run 검증은 [[apte-font-repair]]를 따른다. 실제 앱의 수용·거부·재저장은 계속 미시험이다.
