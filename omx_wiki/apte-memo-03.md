---
title: "APTE Memo 03"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:42.403Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/참고문헌검증표.md"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 03

# 메모 3 참고문헌 전수 확인

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> 절대 틀리면 안됨!
> 중간부터 12번 이후 번호 누락된거 같은데, 논문 내에서 전체적으로 문헌 참조가 제대로 들어갔는지 확인해주세요. 지금 문장과 참고문헌이 일치하는지 애매한 것들이 있어서 이것도 확인 필요.
> 전체 다 꼼꼼하게 확인해주세요.

## 연결 본문

　이에 본 연구에서는 기계학습의 탐색 능력과 통계모형의 검정 기능을 순차적으로 연계한 탐색-확인(Screening-Confirmation) 절차를 적용하여, 고속도로 교통사고에서의 인명피해 발생과 연관된 영향 요인을 밝히고자 하였다. 기존 연구들이 통계모형과 기계학습을 각각 적용한 후 결과를 비교하거나 병렬적으로 제시하는 데 주로 초점을 둔 데 비해15, 본 연구는 기계학습을 통해 사전에 특정하기 어려운 잠재적 위험요인과 변수 간 상호작용을 탐색하고, 이를 통계모형을 통해 검증하는 순차적 분석체계를 적용한다는 점에서 차별성을 가진다. 분석에는 2011년부터 2019년까지 전국 고속도로에서 발생한 교통사고 자료를 활용하였으며, 사고 이전에 관찰 가능한 정보들을 중심으로 독립변수를 구성하였다. 분석에는 XGBoost와 SHAP을 적용하여 인명피해 발생에 기여하는 주요 요인 및 상호작용 후보를 탐색하

## 출처

원본 HWPX의 MEMO 번호 3. 작성자 필드 `user`, 저장 시각 `2026-10-07T19:01:26Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 29 편 서지·인용 연결 검토 및 사용 22 편 재배열 반영; 원문 위치 2 건 보류
- 수정 근거: [참고문헌 검증표](../docs/paper/revisions/2026-11-02/참고문헌검증표.md), [변경대조목록](../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json), [문서검증결과](../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json)의 인용 검증.
- 추적 수정 위치·조치: 인용과 문장 범위를 맞추고 사용 문헌 22 편을 첫 등장 순서 1~22 로 재번호화했다. 원 19·20·21·22·23·24·27 은 추적 삭제했다.
- 검증 결과: 수용 텍스트에서 정의되지 않은 인용 0, 미인용 유지 문헌 0, 첫 인용 순서 1~22. 신 16(원 15)은 No. 49 로 교정했다. 전체 전문을 모두 열람했다는 의미는 아니다.
- 잔여 확인사항: 원 28/신 20 의 alpha 추정식 정확한 출전과 원 29/신 22 의 pseudo R² 정의 원문 위치는 보류다. 수치 재현 완료와 서지 귀속 검증을 구분한다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]
