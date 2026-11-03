---
title: "APTE Revision Hub"
tags: ["APTE", "논문수정", "교수메모", "검증"]
created: 2026-11-02T10:41:46.112Z
updated: 2026-11-03T05:46:34Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/구조검증기록.md"]
links: ["apte-source-register.md", "apte-professor-memos.md", "apte-data-evidence.md", "apte-methods-results-map.md", "apte-reference-audit.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-font-repair.md", "apte-full-rereview.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Revision Hub

> **2026-11-03 전수 재검토 우선 기록:** 현재 판정·파일·인용 매핑은 [[apte-full-rereview]]와 [최신 검토 보고서](../docs/paper/revisions/2026-11-02/전수재검토보고서.md)를 따른다. 아래 이전 날짜의592범위·SMOTEN보존·특정출전보류 기록은 당시 스냅샷이다.


# APTE 논문 수정 위키

이 위키는 최종 HWPX 원고의 교수 검토 메모 13 개에 대한 수정 근거, 분석자료 확인 상태, 변경내용 추적, 검증 결과를 관리한다.

## 작업 원칙

- 원본을 보존하고 별도 수정본을 작성한다.
- 논문 본문에는 논문 문체를 사용한다.
- 수정은 실제 변경내용 추적 기능으로 기록한다.
- 관측자료, 추정치, 인용문헌은 근거를 확인한 경우에만 확정한다.
- 검증이 끝나지 않은 항목은 별도 확인 목록에 남긴다.

## 지식 지도

- [[apte-font-repair]] · [2026-11-03 글꼴 복구](apte-font-repair.md)

- [[apte-source-register]] · [원문·근거 등록부](apte-source-register.md)
- [[apte-professor-memos]] · [교수 메모 13개](apte-professor-memos.md)
- [[apte-data-evidence]] · [데이터·결과 근거](apte-data-evidence.md)
- [[apte-methods-results-map]] · [방법–결과 대응](apte-methods-results-map.md)
- [[apte-reference-audit]] · [참고문헌 검증](apte-reference-audit.md)
- [[apte-revision-decisions]] · [수정 결정](apte-revision-decisions.md)
- [[apte-validation-log]] · [검증 기록](apte-validation-log.md)

## 2026-11-03 전수 재검토 전의 상태

2026-11-02 구축 기록: **지식 페이지 21 개+index/log**, 교수메모 13 개를 연결했다. 메모 4 는 section1 에서 추가 확인했으며 초기 12 개 기록을 정정했다. 원문·근거를 보존한 채 메모별 처리·검증·잔여 한계를 갱신했다.

- 현재 HWPX: [docs/paper/revisions/2026-11-02/APTE_메모내용 반영_변경내용추적.hwpx](../docs/paper/revisions/2026-11-02/APTE_메모내용%20반영_변경내용추적.hwpx)
- 수정검토보고서: [docs/paper/revisions/2026-11-02/수정검토보고서.md](../docs/paper/revisions/2026-11-02/수정검토보고서.md) — 작성 완료. 제목 3안·13개 메모 처리표·방향 비교·최종 검증 범위를 담았다. 여섯 SHAP 값의 별도 표와 24쌍 집계 CSV는 [데이터·분석 추가 확인사항](../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md)에 연결했으며 새 본문 부록표로 인용하지 않는다.
- 추적 수정: 본문·표·인용 174 개+빈 문단 31 개 native 삭제=**205 개 논리 변경·592 개 범위**.
- 보존: 원본 SHA, 메모 13 개, 수식 24 개, 그림 5 개, 표격자 6 개, Table1 의 88 개 항목·176 개숫자. 문헌은 29 편을 검토하고 사용 22 편을 첫 인용 순서로 재배열했다.
- 기존 설계 회귀 재적합: pseudo R².1484638717→**.148**, 주시태만×영업소−.9345008795→**−.935**, 고정α3.4338328130. 저장 CSV 와의차이는 반올림폭 이내다.
- native 한글 열기 및 **17 쪽 PDF 출력 성공**. 마지막 section1 문단끝 삭제 paraend=1 의 Mac 멈춤은 그 끝만 0 으로 보존하여 해결했다.
- **최종 17쪽 페이지 검토 통과**. 읽기전용 앱에서 native 수용·거부 UI 는 미시험이며 파서 수준 수용/거부검증과 구별한다.

## 남겨 둔 확인 한계

SMOTEN6 개 성능값 생성 근거 없음, Fig.2 전체 17,986 건 SHAP 배열 미재계산, 원 28/신 20 의 alpha 식 출전과 원 29/신 22 의정의 원문 위치 보류. 메모 1 의 제목 최종선택, 메모 7의 실제 위치 유지, 메모 9·13 의저자 최종 판단을 임의로 완료처리하지 않는다. 상세는 [[apte-validation-log]], [[apte-reference-audit]], [[apte-data-evidence]]를 따른다.

## 2026-11-02 패키지와 실제 앱 검증

2026-11-02 HWPX SHA-256: `1ac7621aa5ea69cc1572a24c4906021a110a77ad79cd1aa45828fb2c5754a965`.

리더는 P83/P106 변경 후 12·13·15쪽, VIF 설명 변경 후 5쪽 하단을 다시 검토해 통과했다. VIF 수정 전후 나머지 16쪽은 픽셀 동일하다. 최종 출력은 17쪽이며 실제 한글 재열기에서 1/17쪽 표시를 확인했다.

OS 미리보기도 갱신했다. `Preview/PrvText.txt`는 수용 텍스트, `Preview/PrvImage.png`는 최종 한글 출력 첫 페이지의 724×1024 이미지이며 `Contents/content.hpf`의 제목·수정일을 갱신했다. 본문 header/section0/section1의 SHA는 캐시 갱신 전후 동일하다. 원본과 달라진 패키지 부품은 본문·추적 XML 3개와 캐시·메타 3개, 총 6개다. 오래된 미리보기 문제는 해소되었다.

위키 담당자도 최종 파일의 SHA, 원본 SHA 보존, 변경 부품 6개, 미리보기 크기, PDF 17쪽을 읽기 전용으로 재확인했다. native 수용·거부 UI 미시험과 분석·문헌의 보류 사항은 이 검증으로 해소된 것으로 처리하지 않는다.


## 2026-11-03 글꼴 복구 최종본

글꼴 복구 당시 파일은 [APTE_메모내용 반영_변경내용추적.hwpx](../docs/paper/revisions/2026-11-02/APTE_메모내용%20반영_변경내용추적.hwpx)이며 SHA-256은 `ddfb68efe353ab2bcb8a03f575656c97b18c3d49d759b753e9e9147d85c0f133`이다. 공백의 글꼴을 상속한 삽입문을 원래 본문 #신명조·Times New Roman으로 복구하고, 국문 참고문헌의 혼합 글꼴과 새 표 주석을 정리하였다. 문안·기존/삭제 문자 서식·메모 13개·추적 592범위를 보존하였다. 한글 17쪽을 새로 출력해 전체 지면을 검토하고 최종 파일을 재열기하였다. 상세 정책·검증·앱 편집 미시험 한계는 [[apte-font-repair]]와 [글꼴 복구 기록](../docs/paper/revisions/2026-11-02/글꼴복구검토기록.md)을 따른다. 위의 2026-11-02 해시와 픽셀 비교 기록은 이전 스냅샷이다.
