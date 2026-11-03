# APTE — 고속도로 사고의 인명피해 관련 요인과 상호작용 분석

고속도로 사고 83,297건의 기록된 사고 특성·도로 및 주행 환경과 인명피해 발생의
관련성을 XGBoost·SHAP과 회귀모형으로 분석한 연구 자료다. 인명피해에는 사망·중상·경상이 포함된다.

## 교수 메모 반영본과 LLM 위키

[LLM 위키](omx_wiki/apte-revision-hub.md)를 먼저 구축하여 원고·메모·분석 근거·검증 기록을 연결하였다.
최종 원본의 메모는 총 **13개**이며, [수정 HWPX](docs/paper/revisions/2026-11-02/APTE_메모내용%20반영_변경내용추적.hwpx)에
네이티브 변경내용 추적 **592범위**를 기록하였다. 원본과 메모를 보존했고 한글 출력 17쪽을 검토하였다.
2026-11-03에는 삽입문의 글꼴을 원래 본문·표·참고문헌 서식에 맞춰 복구하고 전체 17쪽을 다시 검토하였다. [글꼴 복구 기록](docs/paper/revisions/2026-11-02/글꼴복구검토기록.md)

- [수정 검토 보고서·제목 후보·메모별 조치](docs/paper/revisions/2026-11-02/수정검토보고서.md)
- [데이터·분석 추가 확인사항](docs/paper/revisions/2026-11-02/데이터_분석_추가확인사항.md)
- [참고문헌 검증표](docs/paper/revisions/2026-11-02/참고문헌검증표.md), [HWPX 구조 검증](docs/paper/revisions/2026-11-02/구조검증기록.md)

SMOTEN 성능값의 생성 근거, 일부 문헌의 특정 원문 구절, 실제 편집기에서의 추적 변경 수용·거부·재저장은
미확인이다. 검토용 수정본이며 투고 전 확인이 필요하다. 원자료·행 단위 분석 자료는 추가하지 않았다.
과거 초안·보고서는 당시의 분석과 문안을 보존한 자료로, 최신 정정 사항은 위 보고서를 우선한다.

## 핵심 결과

| 지표 (균형 설계, 5-seed 평균) | 값 |
|---|---|
| ROC-AUC | **0.785 ± 0.005** |
| AP (저장 열 이름 PR_AUC) | 0.766 ± 0.009 |
| F1-score | **0.724 ± 0.004** |
| Recall | **0.762 ± 0.008** |
| Precision | 0.689 ± 0.005 |
| Accuracy | 0.709 ± 0.004 |

- 인명피해 발생 오즈가 높은 범주: 안전거리미확보(OR 2.07) · 트레일러(2.70) · 승합(1.89) · 졸음(1.57) ·
  주시태만(1.54) · 정차차량(3.45) — 다변량 로지스틱 p<0.001; 주사고원인은 과속·포트홀 통합 기준 코딩
- 인명피해 발생 오즈가 낮은 범주: 단독차량화재(0.05) · 노면잡물(0.10) · 영업소TG(0.12) · 램프(0.30)
- 상호작용(FDR q<0.05): TG×승용 · 주시태만×본선 · 승합×대형(인명피해율 28.3%) ·
  노면잡물×도로환경정상 — SHAP 후보 24쌍 중 회귀에서 13쌍 유의. 계수는 주효과를 통제한 로그오즈의 추가항이다.
- SHAP–로지스틱 방향 46/56(82.1%), 로지스틱 유의 범주 34/41(82.9%) 일치. 방향의 기술적 비교다.

상세 내용: [docs/analysis_report.md](docs/analysis_report.md)

## 방법론·결과·논문 자료

| 자료 | 위치 |
|---|---|
| 논문에 사용한 데이터 설명 | [자료 범위·타겟·14개 변수·분석 표본·논문 수치 대응](docs/data_description.md) |
| 분석 방법과 전체 결과 | [분석 보고서](docs/analysis_report.md) |
| 논문 방법론·결과 초안 | [방법론](docs/paper/04_draft_methods.md), [결과](docs/paper/05_draft_results.md) |
| 집필 계획·분석 근거·초록·서론 | [논문 작업 폴더](docs/paper/) |
| 전체 원고·개요·감사보고서 | [전체 원고](docs/paper/manuscripts/APTE_논문_전체원고_v1.md), [상세 개요](docs/paper/manuscripts/APTE_논문_상세개요.md), [근거 기반 감사보고서](docs/reviews/APTE_논문_근거기반_감사보고서.md) |
| 편집용 논문 파일 | [DOCX 초안](docs/paper/APTE_2026_논문초안.docx), [HWPX 원본](docs/paper/manuscripts/APTE논문.hwpx), [v2](docs/paper/manuscripts/APTE논문_v2.hwpx), [v3](docs/paper/manuscripts/APTE논문_v3.hwpx) |
| 초록·제출용 원고 | [최종 초록](docs/abstracts/APTE_2026_Abstract_sb_sj_final.doc), [별도 전체 논문 초안](docs/paper/submissions/APTE_2026_full_paper_draft.docx) |
| 저장 결과 | [그림 15개](outputs/figures/), [결과표 21개](outputs/tables/), [학습 모델·설정](outputs/model/) |
| 분석 코드·탐색 노트북 | [분석 코드](src/), [탐색 노트북](notebooks/exploratory/) |
| 학회 발표·포스터 | [포스터·발표 파일과 제작 코드](projects/traffic-accident-poster/) |
| 참고문헌 | [참고논문·보고서 PDF](references/papers/) |
| 자료 정리 기준 | [폴더 대응표·중복 처리·데이터 제외 범위](docs/repository_guide.md) |
| 2026-10-01 검토 기록 | [PDF·메모·실제 분석 대조](docs/reviews/APTE_10_01_대조검토.md), [수정 실행안](docs/reviews/APTE_10_01_수정실행안.md) |

현재 수치와 산출물은 기존 분석 결과다. 2026-10-01 검토에서 성토 범주 병합,
포트홀 기준집단, 예측 평가 절차 등의 수정 필요 사항을 기록했다.
수정 실행안은 당시의 작업 계획이다. 2026-11-02에는 문안 수정과 기존 결과의 LR·포아송·고정 α NB·단일 상호작용 재적합 검증을 수행했으며, 전체 파이프라인의 재분석은 수행하지 않았다.
검토 문서가 참조하는 Downloads 등 외부 경로의 자료가 모두 포함된 것은 아니다.
저장소 정리는 로컬 APTE 폴더의 비데이터 자료를 대상으로 하였다. 교수 메모 반영과 검증의 범위는 위 최신 보고서에 구분하여 기록하였다.

원본·전처리 데이터, 학습/평가 분할, 관측치별 예측값과 SHAP 배열은 공개 파일 목록에서
제외했다. 기존 로컬 파일은 유지하며, 집계 결과표·그림·모델 설정과 가중치는 보존한다.
노트북은 코드·설명만 공유하고 저장된 실행 출력과 실행 횟수는 제거했다.
이 제외 기준은 현재 버전에 적용되며, 과거 Git 커밋 이력을 삭제한 것은 아니다.
분석에 사용한 데이터의 범위와 변수 정의는 [데이터 설명서](docs/data_description.md)에
정리했다. 전체 83,297건과 균형 예측 표본 17,986건을 구분하며, 기존 전처리의 검토사항도 명시한다.

## 저장소 구조

```
├── src/
│   ├── 01_preprocess.py         # 전처리 + Cramér's V/VIF 공선성 진단 + 변수 선별
│   ├── 02_model_xgboost.py      # 균형/불균형 설계 XGBoost + LR 베이스라인
│   ├── 03_shap_analysis.py      # SHAP 전역 중요도 + 상호작용 분해
│   ├── 04_confirmatory_stats.py # 카이제곱 + 다변량 로지스틱 OR + 방향 일치율
│   ├── 05_interaction_deep.py   # 상호작용 랭킹 A/B + FDR 검정 + 프로파일
│   ├── 06_regression_tables.py  # 로지스틱·음이항 회귀 결과표
│   ├── 07_paper_figures.py      # 논문용 그림
│   └── 08_tg_distance_gradient.py # TG 거리별 인명피해율
├── outputs/
│   ├── figures/              # fig01~fig15 (히트맵, ROC/PR, SHAP, 회귀·TG 등)
│   ├── tables/               # 성능표, 중요도, 상호작용, 선별 로그
│   └── model/                # 학습된 모델(json)·모델 설정만 공개
├── docs/
│   ├── analysis_report.md    # 분석 리포트 (방법론·결과·기존 분석과의 차이)
│   ├── data_description.md   # 논문 분석 데이터의 범위·변수·표본·결과 대응
│   ├── abstracts/            # 최종 초록
│   ├── paper/                # 논문 초안·DOCX 생성 코드·의존성 파일
│   │   ├── manuscripts/      # 전체 원고·상세 개요·HWPX 버전별 파일
│   │   ├── revisions/        # 교수 메모 반영 HWPX·검토 보고서·집계 검증 기록
│   │   └── submissions/      # 별도로 작성한 전체 논문 초안
│   ├── reviews/              # 감사보고서·대조 검토·수정 실행안
│   └── repository_guide.md   # 자료 정리 및 데이터 제외 기준
├── omx_wiki/                # 출처·교수 메모13개·분석 근거·수정 판단·검증 연결
├── notebooks/exploratory/    # 기존 탐색·방법론 노트북 (실행 출력 제거)
├── references/papers/        # 참고논문·보고서 PDF 11개
└── projects/traffic-accident-poster/
    ├── *.pptx, *.pdf, *.svg  # 학회 발표·포스터와 편집용 파일
    ├── *.py                  # 기존 포스터·표·그림 제작 코드
    ├── notebooks/            # 기존 학습 노트북 (실행 출력 제거)
    ├── charts_en/            # 영문 포스터 그림
    └── outputs/              # 기존 분석의 그림·집계표·변수 메타데이터
```

## 실행

데이터는 포함되어 있지 않으므로 분석 재실행에는 로컬 원자료와 중간 산출물이 필요하다.
집계표·그림·문서 열람은 데이터 없이 가능하다.

```bash
pip install -r requirements.txt
python3 src/01_preprocess.py    # 원본 통합 CSV 경로 필요 (스크립트 상단 RAW 참조)
python3 src/02_model_xgboost.py
python3 src/03_shap_analysis.py
```

`01_preprocess.py`, `06_regression_tables.py`, `08_tg_distance_gradient.py`는
저장소 밖의 통합 원자료를 참조한다. 재실행할 때 각 스크립트의 원자료·출력 경로를
실행 환경에 맞춰 확인해야 한다.

포스터 제작 코드는 [별도 안내](projects/traffic-accident-poster/README.md)를 참고한다.
기존 코드의 분석 방식과 경로 설정은 이번 자료 정리에서 변경하지 않았다.

논문 DOCX 생성:

```bash
cd docs/paper
npm ci
node build_docx.js
```

## 방법론 요약

1. **전처리**: 기록된 사고 특성·환경의 후보 18개 변수 정제 — 표기 통합, 결측률 5% 미만 최빈값 대치,
   희소 범주(0.5% 미만) 통합, 오류 변수(운전시간) 제거, 사고 결과 파생 변수 전면 배제
2. **공선성 진단**: bias-corrected Cramér's V (주야구분 제거, V=0.710) +
   설명력 하위 3개 제거 + 더미 VIF 검증(max 5.46) → **최종 14개 변수**
3. **모델링**: 1:1 언더샘플링 균형 설계(문헌 표준) + 5-seed 반복 + 로지스틱 베이스라인
   + 불균형 보조 설계(임계값 최적화)
4. **해석**: SHAP 전역 중요도·방향(관측 인명피해율 대조), SHAP interaction values
   기반 교차변수 상호작용 랭킹
5. **후속 통계 검토**: SHAP으로 후보를 탐색한 뒤 다변량 로지스틱
   (OR·95% CI·p)과 주효과 통제 상호작용항 검정 + BH 보정을 적용한다. 탐색·검정 관측치가
   중복되므로 독립 표본 재현 검증과 구분한다.
