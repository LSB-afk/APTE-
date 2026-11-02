# APTE 자료 정리 안내

2026-11-02 기준으로 로컬 APTE 폴더의 비데이터 자료를 기존 저장소에 통합했다.
분석 결과나 논문 내용을 새로 계산·수정한 작업은 아니며, 기존 버전과 산출물을 보존했다.

## 폴더 대응표

| 기존 로컬 위치 | 저장소 위치 | 처리 |
|---|---|---|
| `APTE-workspace/src/` | [`src/`](../src/) | 기존 코드 유지 |
| `APTE-workspace/outputs/` | [`outputs/`](../outputs/) | 그림·집계표·모델 JSON 유지, 데이터 분할·SHAP 배열 제외 |
| `APTE-workspace/`의 전체 원고·상세 개요·HWPX 3개 | [`docs/paper/manuscripts/`](paper/manuscripts/) | 내용 유지, 폴더로 이동 |
| `APTE-workspace/`의 근거 기반 감사보고서 | [`docs/reviews/`](reviews/) | 내용 유지, 검토 문서와 함께 정리 |
| `APTE_2026_Abstract_sb_sj_final.doc` | [`docs/abstracts/`](abstracts/) | 최종 초록 원본 보존 |
| `초록/` | [`docs/paper/submissions/`](paper/submissions/) | 별도 전체 논문 DOCX 초안 보존 |
| `연구_분석방법론/` | [`notebooks/exploratory/`](../notebooks/exploratory/) | 노트북 5개, 코드·설명 유지 |
| `래퍼런스_논문/` | [`references/papers/`](../references/papers/) | 참고논문·보고서 PDF 11개 보존 |
| `APTE_교통사고_데이터/` | [`projects/traffic-accident-poster/`](../projects/traffic-accident-poster/) | 코드·발표·포스터·그림·집계 결과만 통합 |
| `데이터(CSV)/`, `DATA/`, `data/`의 관측 데이터 | 제외 | 기존 로컬 파일 유지 |

기존 `docs/paper/`의 집필 문서·DOCX 생성 코드·의존성 파일과
`docs/reviews/`의 2026-10-01 검토 기록도 그대로 보존한다.

## 중복과 버전 처리

- SHA-256으로 파일 내용을 비교했다. 파일명이 비슷해도 내용이 다르면 별도로 보존했다.
- 루트의 `APTE_2026_Abstract_sb_sj_final.doc`와 포스터 폴더의
  `APTE_2026_Abstract_sb_sj_final 복사본.doc`는 내용이 완전히 같아
  [`최종 초록`](abstracts/APTE_2026_Abstract_sb_sj_final.doc) 하나로 통합했다.
- HWPX 원본·v2·v3, 기존 논문 DOCX와 별도 전체 논문 초안, 포스터의
  PPTX·PDF·SVG는 서로 다른 버전 또는 형식이므로 모두 보존했다.
- 두 원본 폴더에 있던 `Untitled-1.ipynb`는 서로 다른 파일이다.
  탐색 노트북과 포스터 프로젝트의 노트북 폴더에 각각 보존했다.
- 외부 폴더에서 가져온 파일명은 한글 NFC 표기로 통일했다.
  노트북 외의 가져온 파일은 내용 바이트를 변경하지 않았다.

## 데이터 제외 범위

원본·전처리 CSV/Excel, 학습·평가용 X/y 파일, Parquet 분할 파일,
관측치별 예측 결과 CSV, SHAP 값 NumPy 배열은 포함하지 않는다.
기존에 추적되던 `data/`의 CSV 2개와 `outputs/model/`의 데이터 파일 5개도
현재 Git 파일 목록에서 제외했으며, 로컬 원본은 삭제하지 않았다.
과거 커밋에는 당시 포함된 데이터가 남아 있다. Git 이력은 재작성하지 않았다.

공유하는 CSV는 성능·회귀계수·중요도·상호작용·변수 목록 등의 집계표 또는
분석 메타데이터다. 학습된 XGBoost 모델 JSON과 설정 JSON도 보존한다.
데이터 폴더 안에 있던 결과 그림·집계표와 변수 메타데이터는
포스터 프로젝트의 `outputs/` 아래로 옮겨 데이터와 구분했다.

가져온 노트북 7개는 셀의 코드·Markdown을 유지하고 실행 출력과 실행 횟수를 제거했다.
따라서 저장된 데이터 미리보기·오류 출력·중간 실행 결과는 공유하지 않는다.
별도로 저장된 결과 그림·집계표는 해당 결과 폴더에서 확인할 수 있다.

운영체제 메타데이터(`.DS_Store`), Office 잠금 파일(`~$…`), Python 캐시,
`node_modules/`, `.omc/`, `.omx/`도 제외했다.
이후 생성되는 데이터·배열·관측치별 예측 결과는 [`.gitignore`](../.gitignore)로 제외한다.

## 재실행 범위

이번 업데이트는 파일 정리와 동기화다. 분석 전체 재학습, 노트북 재실행,
논문 재생성은 수행하지 않았다. 데이터가 필요한 분석을 실행하려면 로컬 자료를
준비하고 기존 스크립트의 입력 경로·출력 경로·폰트를 실행 환경에 맞춰 확인해야 한다.
특히 기존 코드에 포함된 `/Users/…` 절대 경로와 상위 폴더 참조는 그대로 보존했다.
