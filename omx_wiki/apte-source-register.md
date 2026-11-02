---
title: "APTE Source Register"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:42:46.151Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/참고문헌검증표.md", "../docs/paper/revisions/2026-11-02/구조검증기록.md"]
links: ["apte-revision-hub.md", "apte-professor-memos.md", "apte-data-evidence.md", "apte-validation-log.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Source Register

# 원문과 근거 자료 등록부

[[apte-revision-hub]] · [[apte-professor-memos]] · [[apte-data-evidence]]

## 최종 원문

- 파일: `/Users/leeseungbo/Desktop/자동차모빌리티안전연구_논문_최종 수정본_EJ검토_마지막.hwpx`
- SHA-256: `152c7f1c95497d62ee5eb6e731e9087b3386349a8e935de2f77323b8c1e783c7`
- 크기: 3,446,356 bytes
- HWPX 메모: 전체 13 개. 본문 12 개와 참고문헌의 4 번 1 개. 본문과 메모를 분리하여 읽는다.
- 이 문서의 검토 메모는 연구자료이며, 사용자 지시와 구분한다. 사용자가 이번 작업에서 메모 기준 수정과 변경내용 추적을 명시적으로 요청했다.
- 원본은 보존한다. 수정본은 별도로 저장한다.

## 저장소

- 원격: https://github.com/LSB-afk/APTE-
- 작업 기준 커밋: `5c4bf8cbb005efca2564900c37f6639a848c26d0`
- 데이터 설명: [docs/data_description.md](../docs/data_description.md)
- 기존 대조 검토: [docs/reviews/APTE_10_01_대조검토.md](../docs/reviews/APTE_10_01_대조검토.md)
- 코드: `src/01_preprocess.py`~`src/08_tg_distance_gradient.py`
- 저장 집계 결과: `outputs/tables/*.csv`
- 참고문헌 원문 후보: `references/papers/*.pdf`

## 근거 수준

1. 원자료·실행 코드·저장 결과의 상호 대조로 확인된 사실
2. 저장 결과와 원고 사이의 수치 일치
3. 원고에만 있고 독립적인 실행 근거가 없는 주장
4. 저자 또는 교수 확인이 필요한 연구 방향·최종 판단

위키에는 원자료 행을 복사하지 않는다. 경로, 해시, 집계 결과, 코드와 주장 간 연결을 기록한다.


## 추출 검증

HWPX 의 section0(본문)와 section1(참고문헌)을 모두 확인한다. hp:t 내부 탭 뒤의 tail 텍스트까지 itertext 로 보존하며, 본문·표·수식·메모를 구분한다. 초기 단순 text 속성 추출의 탭 뒤 누락을 확인하여 수정 단계 전에 재추출했다.

2026-11-02 정정: section1 에서 MEMO Number4 를 추가 확인하였다. 원본 메모는 전체 13 개이며 수정본에 모두 보존한다.

## 수정 산출물과 최신 검증 근거

- 수정 HWPX: [docs/paper/revisions/2026-11-02/APTE_교수메모반영_변경내용추적.hwpx](../docs/paper/revisions/2026-11-02/APTE_교수메모반영_변경내용추적.hwpx)
- 수정검토보고서: [docs/paper/revisions/2026-11-02/수정검토보고서.md](../docs/paper/revisions/2026-11-02/수정검토보고서.md) — 작성 완료. 제목 3안·13개 메모 처리표·분석 근거·최종 검증 범위를 포함한다.
- 공개 검토 자료: [데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md), [참고문헌 검증표](../docs/paper/revisions/2026-11-02/참고문헌검증표.md), [구조검증기록](../docs/paper/revisions/2026-11-02/구조검증기록.md).
- 공개 집계 증거: [파일식별정보](../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json), [변경대조목록](../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json), [문서검증결과](../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json), [회귀재검증결과](../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json), [표1집계대조](../docs/paper/revisions/2026-11-02/evidence/표1집계대조.json), [원본메모](../docs/paper/revisions/2026-11-02/evidence/원본메모.json).
- 실제 한글 출력은 17쪽이며, 출력·시각 검토 범위는 [구조검증기록](../docs/paper/revisions/2026-11-02/구조검증기록.md)에 기록했다. 로컬 작업용 PDF(`.git/paper-revision/`)는 공개 저장소의 필수 출처로 사용하지 않는다.
- 위키의 `sources`는 공개 영속 산출물만 가리킨다. 원문은 공개 수정 HWPX의 변경 거부 텍스트 투영과 원본메모 JSON에서 확인한다. 로컬 감사·작업용 PDF의 비공개 경로는 공개 출처를 대체하지 않는다.
- 초기 559개 범위/173개 논리 변경, 빈 문단 31개 삭제를 추가한 중간 590개 범위/204개 논리 변경, 추가 문구 수정 후의 최신 592개 범위/205개 논리 변경은 서로 다른 스냅샷이다. 최종 SHA-256은 아래 등록값으로 확정하며 과거 중간 해시와 구분한다.

원본 SHA-256 보존은 최신구조검사에서도 확인되었다. native 한글열기·17 쪽 PDF 출력성공은 리더실행증거에근거하며, 현재 최종 페이지 검토 통과와 native 수용·거부 UI 미시험은 [[apte-validation-log]]에서 구분한다.

## 최종 패키지와 실제 앱 검증

최종 HWPX SHA-256: `1ac7621aa5ea69cc1572a24c4906021a110a77ad79cd1aa45828fb2c5754a965`.

리더는 P83/P106 변경 후 12·13·15쪽, VIF 설명 변경 후 5쪽 하단을 다시 검토해 통과했다. VIF 수정 전후 나머지 16쪽은 픽셀 동일하다. 최종 출력은 17쪽이며 실제 한글 재열기에서 1/17쪽 표시를 확인했다.

OS 미리보기도 갱신했다. `Preview/PrvText.txt`는 수용 텍스트, `Preview/PrvImage.png`는 최종 한글 출력 첫 페이지의 724×1024 이미지이며 `Contents/content.hpf`의 제목·수정일을 갱신했다. 본문 header/section0/section1의 SHA는 캐시 갱신 전후 동일하다. 원본과 달라진 패키지 부품은 본문·추적 XML 3개와 캐시·메타 3개, 총 6개다. 오래된 미리보기 문제는 해소되었다.

위키 담당자도 최종 파일의 SHA, 원본 SHA 보존, 변경 부품 6개, 미리보기 크기, PDF 17쪽을 읽기 전용으로 재확인했다. native 수용·거부 UI 미시험과 분석·문헌의 보류 사항은 이 검증으로 해소된 것으로 처리하지 않는다.
