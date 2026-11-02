# APTE 2026 학회 발표·포스터 자료

기존 `APTE_교통사고_데이터/` 폴더에서 데이터 이외의 자료를 모았다.
기존 논문 분석의 [`src/`](../../src/)와 이 폴더의 과거 분석 코드는 서로 다른 작업 버전이다.
결과 수치를 한 분석의 결과로 합치지 않고 각 폴더에 보존했다.

| 자료 | 위치 |
|---|---|
| 학회 발표와 포스터 | 이 폴더의 PPTX·PDF·SVG 파일 |
| 포스터·표·그림 제작 코드 | 이 폴더의 Python 파일 6개 |
| 영문 포스터 그림 | [`charts_en/`](charts_en/) |
| 기존 학습 노트북 2개 | [`notebooks/`](notebooks/) |
| 부상발생 요인 분석 그림·집계표·보고서 | [`outputs/injury_severity_shap_analysis/`](outputs/injury_severity_shap_analysis/) |
| Method B 결과 그림·집계표·변수 목록 | [`outputs/method_B_pre_accident_xgboost_results/`](outputs/method_B_pre_accident_xgboost_results/) |
| 전처리 변수 목록·클래스 가중치 정보 | [`outputs/preprocessing_metadata/`](outputs/preprocessing_metadata/) |
| 최종 초록 | [`docs/abstracts/`](../../docs/abstracts/) |

원본 `DATA/`의 관측 데이터, 학습·평가 분할, 관측치별 예측 결과,
SHAP 배열은 포함하지 않는다. 노트북의 저장된 실행 출력도 제거했다.
초록 복사본은 원본과 내용이 동일하여 문서 폴더의 한 파일로 통합했다.

## 실행 시 경로

Python 코드는 원래 내용을 보존했다. `build_poster_en.py`는 현재 작업 폴더의
발표 템플릿과 `charts_en/`을 읽으므로 이 폴더에서 실행한다.
필요한 라이브러리는 기존 코드의 import에 따라 별도로 준비해야 한다.

`analyze_severity_shap.py`, `make_charts_en.py`는 기존 컴퓨터의 절대 경로를 사용한다.
`make_charts.py`는 원래 `DATA/…/method_B_pre_accident_xgboost_results/`를 참조한다.
이번 정리에서 해당 결과는 `outputs/method_B_pre_accident_xgboost_results/`로 모았으므로,
재실행할 때 스크립트 상단의 입력·출력 경로와 폰트 설정을 확인해야 한다.
원자료에 의존하는 과정은 별도의 로컬 데이터가 필요하다.

전체 정리 기준은 [`자료 정리 안내`](../../docs/repository_guide.md)를 참고한다.
