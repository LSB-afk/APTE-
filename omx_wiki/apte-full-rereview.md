---
title: "APTE Full Rereview"
tags: ["APTE", "논문수정", "인용검증", "전수검토"]
created: 2026-11-03T05:41:35Z
updated: 2026-11-03T17:07:07Z
sources: ["../docs/paper/revisions/2026-11-02/전수재검토보고서.md", "../docs/paper/revisions/2026-11-02/참고문헌검증표.md", "../docs/paper/revisions/2026-11-02/evidence/전수재검토_구조검증.json"]
links: ["apte-intro-restoration.md", "apte-revision-hub.md", "apte-reference-audit.md", "apte-data-evidence.md", "apte-validation-log.md", "apte-font-repair.md"]
category: session-log
confidence: high
schemaVersion: 1
---

# APTE Full Rereview

> **2026-11-04 서론 원문 복원 우선 기록:** 서론6문단과 현재24편 인용번호·파일 식별은 [[apte-intro-restoration]] 및 [복원 기록](../docs/paper/revisions/2026-11-02/서론원문복원_인용조정기록.md)을 따른다. 아래22편·664범위·17쪽은 직전본 기록이다. 서론 밖 분석 결과는 유지하였다.


2026-11-03 글꼴복구본을 기준으로 메모13개·비공백103단위·최종22편 인용을 다시 읽고 교정과 독립 재검토를 반복하였다. 현재 HWPX SHA-256은 `895e3c4e3b9847512115e9079f747f89581575816b756e627f7006a4648ec8ef`이다. 한글 native17쪽, 추적664범위(삭제357/삽입307), 원본메모13/수용수식24/원본그림5/표격자6개 보존을 확인하였다.

SMOTEN 미재현 여섯값은 원고에서 제외하고 대표 균형 XGBoost 재추론값으로 교체하였다. NB2일반 정의는 Cameron·Trivedi2001(신19), BH는신20, Wilson1927은신21, McFadden1974는신22로 연결한다. 구체 α모멘트식은 본연구 구현 절차로 기술하고 특정 원문에 귀속하지 않는다. 이전의 ‘alpha식 출전 미확인·McFadden1980 정의 보류’는 현재 원고의 미해결 인용 문제로 이어지지 않는다.

q기준·조건부분산/평균 정의·비규제 추론과 규제 예측모형 구분·후속검정 명칭·변수선정규칙·직접반올림·문법을 교정하였다. 원전의 접근수준(초록/전문)을 구분했고 유의한 후속검정도 선택 후 추론의 한계를 유지한다.

일반 SHAP17,986건을 재계산하여 Fig2의 23개 집단을 대조했고, 평가3,598건은 기존 SHAP 배열과 최대차이0.0이었다. 평가2,000건·시드42의 상호작용 재계산에서도 A15+B15−중복6=24 후보와 저장 집계가 일치하였다. 24개 후속 회귀의 Wald p값과 BH 보정도 재계산하여 유의13개를 확인하였다. 관측치별 재계산 배열은 공개하거나 새로 저장하지 않았다.

공식 데이터 제공 자료명·URL·취득일·재배포 조건, 실제 편집기에서 변경 수용·거부·재저장은 여전히 확인이 필요하다. 전체 파이프라인 재분석이나 독립 검정표본의 검증을 수행했다고 기록하지 않는다. 상세 근거와 검증 범위는 sources의 공개 보고서를 따른다.

[[apte-revision-hub]] · [[apte-reference-audit]] · [[apte-data-evidence]] · [[apte-validation-log]] · [[apte-font-repair]]
