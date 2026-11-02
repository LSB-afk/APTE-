---
title: "APTE Reference Audit"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:42:46.586Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/참고문헌검증표.md"]
links: ["apte-revision-hub.md", "apte-professor-memos.md", "apte-source-register.md", "apte-memo-03.md", "apte-memo-04.md", "apte-data-evidence.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Reference Audit

# 참고문헌 대조

[[apte-revision-hub]] · [[apte-professor-memos]] · [[apte-source-register]]

대상: 메모 3·4. 본문 인용 번호 전체와 참고문헌 목록의 대응, 12 번 이후 누락 여부, 문장과 문헌의 실질적 관련성을 검토한다.

## 검증 기준

- 본문 인용 번호와 참고문헌 번호를 기계적으로 대조한다.
- 서지 정보와 DOI 는 출판사·학회·원문 등 1 차 자료로 검증한다.
- 제목·초록으로 확인 가능한 범위와 원문을 확인한 범위를 구분한다.
- 인용을 뒷받침하지 않는 문장은 근거에 맞춰 축소하거나 수정한다.
- 접근 불가 문헌과 해석을 확정할 수 없는 인용은 별도 확인 목록에 남긴다.

## 현재 반영 결과

원문29편의 서지와 본문 인용 연결을 검토했고, 실제 사용22편을 첫 인용 순서1~22로 재번호화했다. 수용 텍스트에서 미정의 인용0, 미인용 유지 문헌0이다. 원19·20·21·22·23·24·27의 미사용7편을 추적 삭제했다. [참고문헌 검증표](../docs/paper/revisions/2026-11-02/참고문헌검증표.md)의 매핑과 [문서검증결과](../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json)의 인용 검증이 일치한다.

- 원 9 의 구조방정식, 로지스틱 관련 원 6·8, BH 방법 원 17, 음이항 근거 원 28 의 인용 위치를 내용에 맞췄다. 기존 연구 전체를 일반화하는 주장도 구체적 연구 범위로 축소했다.
- 신 16(원 15)의 서지는 Vol.49 대신 No.49 로 교정했다. 원 10 의 785~794 쪽은 출판사 서지 검색, 원 13 의 4765~4774 쪽은 NeurIPS 공식 Metadata 로 확인했다. 출판사 403 이나 전문 미열람 범위를 전부 확인한 것으로 확대하지 않는다.
- 원 28/신 20 의 **alpha 추정식 정확한 출전**과 원 29/신 22 의 **McFadden pseudo R² 정의의 원문 위치**는 여전히 보류다. α와 pseudo R²의 코드 재현 자체는 완료되어 별도 사실로 구분한다.
- section1 첫 문단의 “내용에 맞춰서 전반적으로 확인 및 정확하게 수정”은 일반 본문이 아니라 **메모 4**다. 초기 삭제 권고를 철회했고 메모 원문을 보존했다.

공개 근거는 [참고문헌 검증표](../docs/paper/revisions/2026-11-02/참고문헌검증표.md)와 [문서검증결과](../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json)이다. 첫 감사의 미사용6편이라는 원문 상태와 수정 후 미사용7편 정리는 시점·수정 문맥이 다르다. 전체29편을 전문까지 모두 읽었다는 뜻은 아니다. [[apte-memo-03]] · [[apte-memo-04]] · [[apte-data-evidence]] 참조.
