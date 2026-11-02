---
title: "APTE Memo 11"
tags: ["APTE", "논문수정", "근거"]
created: 2026-11-02T10:43:43.168Z
updated: 2026-11-02T11:25:35.428Z
sources: ["../docs/paper/revisions/2026-11-02/evidence/파일식별정보.json", "../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json", "../docs/paper/revisions/2026-11-02/evidence/문서검증결과.json", "../docs/paper/revisions/2026-11-02/수정검토보고서.md", "../docs/paper/revisions/2026-11-02/evidence/원본메모.json", "../docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md", "../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json"]
links: ["apte-professor-memos.md", "apte-source-register.md", "apte-revision-decisions.md", "apte-validation-log.md", "apte-data-evidence.md", "apte-methods-results-map.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# APTE Memo 11

# 메모 11 방법론과 결과 대응

[[apte-professor-memos]] · [[apte-source-register]] · [[apte-revision-decisions]]

## 원문 메모

> (아주 중요) 많이 이상
> 3장 연구방법론과 4장 분석 결과를 전체적으로 비교해 보면, 방법론에 설명되지 않은 분석이 결과에 등장하거나 방법론에서 제시한 분석이 결과에서 충분히 보고되지 않은 부분이 있습니다.
> 현재 논문의 기본 구조?
> - 3.2절 → 4.1절: 변수 선별 및 다중공선성 검토
> - 3.3절 → 4.1~4.2절: XGBoost 예측 성능, SHAP 기여도 및 상호작용 탐색
> - 3.4절 → 4.3절: 카이제곱 검정, 로지스틱 회귀 및 상호작용 유의성 검정
> - ? → 4.4절: 영업소 인접 본선의 거리별 인명피해 발생률 분석(왜 갑자기 나왔는지, 설명 필요)
> - 3.4절 → 4.5절: 음이항 회귀, 분석 방법 간 일치율은 여기서 나오나요?

## 연결 본문

문서 내 빈 문단에 연결되어 있다. 메모 자체가 전체 구조 검토를 지시한다.

## 출처

원본 HWPX의 MEMO 번호 11. 작성자 필드 `skr51`, 저장 시각 `2026-10-20T20:59:52Z`. 원본 해시와 파일 위치는 [[apte-source-register]]에 등록되어 있다.

## 처리와 검증

- 상태: 신규 3.5 절 및 NB 대표 IRR·방향 비교를 반영하고 회귀 재현 검증 완료
- 수정 근거: [수정검토보고서](../docs/paper/revisions/2026-11-02/수정검토보고서.md) 3·4절, [회귀재검증결과](../docs/paper/revisions/2026-11-02/evidence/회귀재검증결과.json), [변경대조목록](../docs/paper/revisions/2026-11-02/evidence/변경대조목록.json).
- 추적 수정 위치·조치: 3.5 TG 거리별 보조 분석 방법을 추가해 4.4 와 대응시켰다. 4.5 P99 에 NB IRR 정차차량 2.93(2.60~3.30), 트레일러 2.60(2.09~3.23), TG.14(.13~.16) 및 47/47 방향 일치를 보고했다.
- 검증 결과: 동일 71 더미+상수 재적합 모두 수렴. LR pseudo R² .1484638717→.148, 고정 α3.4338328130. 주시태만×영업소 -.9345008795→-.935. LR/NB 계수·비·CI·p 는 4 자리 저장 CSV 반올림폭 이내.
- 잔여 확인사항: NB 용 pseudo R²는 저장 근거가 없어 새로 추가하지 않았다. 기존 성토 통합·포트홀 기준코딩·표본 중복의 한계를 유지한다.

관련 상태: [[apte-validation-log]] · [[apte-data-evidence]] · [[apte-methods-results-map]]

### 설계행렬 추가 확인

VIF는 기준범주 제외 후 72개 더미(포트홀 포함), 회귀는 완전분리 포트홀 열 제외 후 71개 더미+상수다. 최신 P33에 구분을 반영했다. VIF와 회귀가 같은 71개 더미를 사용했다고 해석하지 않는다. 근거: `src/01_preprocess.py:443`.
