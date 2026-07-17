// 대한교통학회지 양식 기반 논문 초안 .docx 생성
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, HeadingLevel, ShadingType, BorderStyle,
} = require("docx");

const FIG = (f) => path.join(__dirname, "..", "..", "outputs", "figures", f);
const BODY_FONT = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "Batang" };
const HEAD_FONT = { ascii: "Arial", hAnsi: "Arial", eastAsia: "Malgun Gothic" };

const p = (text, opts = {}) =>
  new Paragraph({
    alignment: opts.align || AlignmentType.BOTH,
    spacing: { after: opts.after ?? 120, line: 276 },
    children: splitRuns(text, opts),
  });

// [확인 필요...] 구간을 빨간색으로 표시
function splitRuns(text, opts = {}) {
  const runs = [];
  const re = /(\[확인 필요[^\]]*\])/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) runs.push(mkRun(text.slice(last, m.index), opts));
    runs.push(mkRun(m[1], { ...opts, color: "C00000", bold: true }));
    last = m.index + m[1].length;
  }
  if (last < text.length) runs.push(mkRun(text.slice(last), opts));
  return runs;
}
const mkRun = (t, o = {}) =>
  new TextRun({
    text: t, font: o.head ? HEAD_FONT : BODY_FONT,
    size: o.size ?? 20, bold: o.bold ?? false, italics: o.italic ?? false,
    color: o.color,
  });

const h1 = (t) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 140 },
    children: [mkRun(t, { head: true, bold: true, size: 24 })],
  });
const h2 = (t) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 },
    children: [mkRun(t, { head: true, bold: true, size: 21 })],
  });

const caption = (t) =>
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
    children: [mkRun(t, { size: 18, bold: true })],
  });

function img(file, w, h) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 160, after: 40 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(FIG(file)), transformation: { width: w, height: h } })],
  });
}

function mkTable(header, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, isHead, w) =>
    new TableCell({
      width: { size: w, type: WidthType.DXA },
      shading: isHead ? { type: ShadingType.CLEAR, fill: "F2F2F2" } : undefined,
      margins: { top: 40, bottom: 40, left: 80, right: 80 },
      children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: [mkRun(String(t), { size: 17, bold: isHead })],
      })],
    });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ children: header.map((t, i) => cell(t, true, widths[i])) }),
      ...rows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, false, widths[i])) })),
    ],
  });
}

// ---------------------------------------------------------------- 내용
const children = [];

children.push(
  p("ARTICLE", { align: AlignmentType.LEFT, size: 18, after: 240 }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [mkRun("XGBoost-SHAP 탐색과 확인적 통계 검정을 결합한 고속도로 교통사고 인명피해 발생 요인 분석", { head: true, bold: true, size: 30 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [mkRun("A Screening–Confirmation Framework Combining XGBoost-SHAP and Confirmatory Statistical Testing for Casualty Occurrence in Expressway Crashes", { size: 21, italic: true })],
  }),
  p("이승보¹ · 이성재¹ · 고은정²* [확인 필요: 저자 구성·순서 확정]", { align: AlignmentType.CENTER, after: 60 }),
  p("¹한남대학교 경영정보학과 학사과정, ²한남대학교 빅데이터응용학과 조교수", { align: AlignmentType.CENTER, after: 60, size: 18 }),
  p("*Corresponding author: eunjeong.ko@hnu.kr [확인 필요]", { align: AlignmentType.CENTER, after: 240, size: 18 })
);

children.push(h1("Abstract"));
children.push(p(
  "This study investigates factors associated with casualty occurrence in expressway crashes using 83,297 nationwide crash records in South Korea (2011–2019). To prevent target leakage, only pre-accident variables were considered; collinearity diagnostics based on bias-corrected Cramér's V and variance inflation factors reduced 18 candidates to 14 predictors. Casualty occurrence (at least one death or injury; prevalence 10.8%) was modeled with XGBoost under 1:1 random undersampling, yielding stable performance across five resampling seeds (ROC-AUC 0.785±0.005, F1-score 0.724±0.004). We propose a two-stage screening–confirmation framework in which SHAP-based risk factors and interaction candidates are subsequently verified by multivariable logistic regression (odds ratios) and negative binomial regression (casualty counts). Effect directions were highly consistent across the three models (82% between SHAP and logistic regression; 100% among dummies significant in both regressions). After FDR correction, interactions such as tollgate×passenger-car (heterogeneous protective effect), inattention×mainline (risk amplification), and van×large-class (28.3% casualty rate) were statistically confirmed, whereas the drowsiness×passenger-car pair — highly ranked by SHAP interaction strength — failed confirmation, demonstrating the risk of reporting machine-learning interaction rankings alone."
));
children.push(p("Keywords: expressway crash, casualty occurrence, XGBoost, SHAP, interaction effect, class imbalance", { italic: true, after: 240 }));

children.push(h1("초록"));
children.push(p(
  "고속도로 교통사고의 인명피해 발생 요인을 규명하기 위해 2011~2019년 전국 고속도로 사고 83,297건을 분석하였다. 사고 결과로부터 파생되는 변수를 배제한 사고 전(pre-accident) 변수 18개 후보에 대해 Cramér's V와 분산팽창계수(VIF) 기반 공선성 진단을 수행하여 최종 14개 변수를 선정하였고, 인명피해 발생(사망·중상·경상 1명 이상)을 이진 타겟으로 정의하였다(발생률 10.8%). 클래스 불균형은 1:1 랜덤 언더샘플링으로 처리하였으며, XGBoost 모형은 5회 반복 샘플링에서 ROC-AUC 0.785±0.005, F1-score 0.724±0.004의 안정적 성능을 보였다. 본 연구는 SHAP으로 탐색한 위험요인과 상호작용 후보를 다변량 로지스틱 회귀(오즈비)와 음이항 회귀(사상자 수)로 확인하는 탐색-확인 2단계 프레임워크를 제안한다. 세 모형의 효과 방향은 높은 일치율을 보였고(SHAP-로지스틱 82%, 로지스틱-음이항 공통 유의 더미 100%), FDR 보정 후 영업소(TG)×승용차(보호효과 이질성), 주시태만×본선(위험 증폭), 승합×대형(인명피해율 28.3%) 등의 상호작용이 통계적으로 확인되었다. 반면 SHAP 강도 상위였던 졸음×승용차 상호작용은 검정을 통과하지 못해, 기계학습 상호작용 지표의 단독 보고가 갖는 위험을 실증하였다."
));
children.push(p("주요어: 고속도로 교통사고, 인명피해 발생, XGBoost, SHAP, 상호작용효과, 클래스 불균형", { italic: true, after: 240 }));

// 1. 서론
children.push(h1("1. 서론"));
[
  "고속도로는 주행 속도가 높아 사고 발생 시 인명피해로 이어질 개연성이 크며, 인명피해 사고는 사회경제적 손실의 대부분을 차지한다. 그러나 어떤 사고 전 조건에서 사고가 인명피해로 귀결되는지는 요인 간 비선형성과 상호작용으로 인해 단순한 구조로 설명되지 않는다. 예컨대 동일한 사고 원인이라도 발생 지점의 주행 속도 환경이나 차종에 따라 인명피해 위험이 달라질 수 있다.",
  "인명피해 요인 분석에는 두 가지 방법론적 과제가 있다. 첫째, 로지스틱 회귀 등 전통적 통계모형은 가법성·독립성 가정으로 인해 비선형 경계와 고차 상호작용을 포착하기 어렵다. 둘째, 이를 보완하는 트리 앙상블 기계학습은 예측력이 높지만, 변수중요도나 SHAP 값의 순위를 나열하는 방식의 보고는 통계적 유의성이라는 추론적 근거를 결여한다. 특히 SHAP 상호작용 강도는 표본 내 등장 빈도에 가중되므로, 강도 순위가 높다는 것이 그 상호작용이 통계적으로 존재함을 보장하지 않는다.",
  "본 연구는 이 간극을 메우기 위해 탐색-확인(screening–confirmation) 2단계 프레임워크를 제안한다. 1단계에서 XGBoost-SHAP으로 위험요인과 상호작용 후보를 탐색하고, 2단계에서 주효과를 통제한 다변량 로지스틱 회귀의 상호작용항 검정과 다중검정 보정(Benjamini and Hochberg, 1995)으로 후보를 확인한다. 아울러 인명피해 발생 여부(이항 로지스틱)와 사상자 수(음이항 회귀)라는 상이한 결과 척도에서 효과 방향의 일치를 검증하여 견고성을 확보한다.",
  "자료 설계 측면에서는 사고유형·사고차량수 등 사고 결과로부터 파생되는 변수를 타겟 누수 차단을 위해 전면 배제하고, 사고 전 시점에 관측 가능한 변수만으로 분석하였다. 이 과정에서 오입력 변수(운전시간)를 식별·제거하였으며, 누수 변수를 포함할 경우 노면잡물 등 일부 요인의 효과 방향이 실증 인명피해율과 반대로 추정됨을 확인하였다. 이는 '사고를 일으키는 요인'과 '인명피해를 심화시키는 요인'을 구분해야 함을 시사한다.",
  "본 연구의 질문은 다음과 같다. (1) 사고 전 정보만으로 인명피해 발생을 어느 수준까지 판별할 수 있는가? (2) 어떤 요인이 인명피해 위험을 증가/감소시키며, 세 가지 모형의 결론은 일치하는가? (3) 요인 간 상호작용 중 통계적으로 확인되는 것은 무엇이며, 어떤 조건부 위험구조를 갖는가?",
].forEach((t) => children.push(p(t)));

// 2. 선행연구
children.push(h1("2. 선행연구"));
[
  "교통사고 심각도·인명피해 요인 연구는 방법론에 따라 세 부류로 정리된다.",
  "첫째, 순서형 로지스틱, 이항 로지스틱, 음이항 회귀 등 전통 통계모형으로 유의 요인과 오즈비를 보고하는 연구들이다 [확인 필요: 국내 문헌 서지사항]. 계수의 해석 가능성과 추론적 근거가 장점이나, 가법성 가정으로 비선형·상호작용 구조를 명시적으로 다루지 못하며 상호작용항은 연구자가 사전에 지정해야 한다.",
  "둘째, Random Forest, XGBoost(Chen and Guestrin, 2016) 등으로 심각도를 예측하고 변수중요도 순위를 보고하는 연구들이다 [확인 필요: 국내 문헌 서지사항]. 예측 성능과 비선형 포착이 장점이나, 중요도는 효과의 방향과 유의성을 제공하지 않는다.",
  "셋째, SHAP(Lundberg and Lee, 2017; Lundberg et al., 2020)을 적용해 요인별 기여 방향과 상호작용까지 보고하는 최근 연구들로, Moon et al.(2025)은 서울시 고령운전자 사망사고에 대해 비선형 관계와 상호작용 효과를 분석하였다. 그러나 이들 연구에서 상호작용은 SHAP 강도 순위의 나열에 그치며, 주효과를 통제한 상태에서 해당 상호작용이 통계적으로 유의한지는 검정되지 않는다.",
  "본 연구는 셋째 부류의 확장으로서, SHAP 탐색 결과를 전통 통계의 추론 도구로 확인하는 절차를 결합한다. 아울러 상호작용 강도를 전체 기여(빈도 가중)와 건당 강도로 분리하여 보고함으로써, 빈도가 낮지만 강한 조건부 위험을 식별한다.",
].forEach((t) => children.push(p(t)));

// 3. 자료 및 전처리
children.push(h1("3. 자료 및 전처리"));
children.push(h2("3.1 자료 개요와 타겟 정의"));
children.push(p("한국도로공사 고속도로 교통사고 자료(2011~2019) 83,297건을 분석하였다 [확인 필요: 자료 출처 공식 표기]. 인명피해 발생은 사고별 사망·중상·경상 인원수의 합이 1명 이상이면 1, 아니면 0으로 정의하였다. 인명피해 사고는 8,993건(10.80%)으로 대물피해 사고 74,304건(89.20%)과 약 8.3:1의 불균형을 이루며, 인명피해 사고의 내부 구성은 최고 심각도 기준 사망사고 1,968건(2.36%), 중상사고 1,635건(1.96%), 경상사고 5,390건(6.47%)이다."));
children.push(h2("3.2 사고 전 변수와 누수 차단"));
children.push(p("입력변수는 사고 전 시점에 관측 가능한 정보로 한정하였다. 사고유형, 사고차량수, 피해 규모, 사고처리 시간 등 사고 결과로부터 파생되는 변수는 배제하였고, 자료 검증 과정에서 전체의 99.9%가 0이고 나머지가 타임스탬프 오입력으로 확인된 운전시간 변수를 제거하였다. 18개 후보 변수에 대해 표기 정규화, 결측 처리(결측률 5% 미만 최빈값 대치, 5% 이상 '미상' 범주 유지), 희소 범주 통합(0.5% 미만 → '기타')을 수행하였다."));
children.push(h2("3.3 공선성 진단과 변수 선별"));
children.push(p("변수 수준에서 bias-corrected Cramér's V를 산출하여 V≥0.6인 쌍 중 타겟 연관성이 낮은 변수를 제거하였다(주야구분: 조명시설과 V=0.710). 이어 타겟 연관성 하위 변수(주말여부, 포장구분, 성별)를 제외하여 14개 변수를 확정하였다(표 1). 최빈범주 기준 원-핫 인코딩 후 더미 수준 VIF는 최대 5.46(평균 1.48)으로 다중공선성 기준(VIF>10)을 초과하는 더미는 없었다."));
children.push(mkTable(
  ["변수", "범주 수", "타겟 연관성(V)", "변수", "범주 수", "타겟 연관성(V)"],
  [
    ["주사고원인", "16", "0.206", "날씨", "5", "0.061"],
    ["교통장애요인", "4", "0.167", "조명시설", "4", "0.061"],
    ["발생지점", "6", "0.136", "노면상태", "4", "0.060"],
    ["운전자상태", "4", "0.107", "연령구분", "7", "0.056"],
    ["사고시도로환경", "6", "0.085", "사고직전차량조작", "4", "0.056"],
    ["원인차차종", "6", "0.082", "차종구분", "9", "0.046"],
    ["절성토구분", "7", "0.040", "평면선형", "4", "0.023"],
  ],
  [1900, 900, 1500, 1900, 900, 1500]
));
children.push(caption("표 1. 최종 14개 사고 전 예측변수와 타겟 연관성(Cramér's V)"));

// 4. 방법론
children.push(h1("4. 분석 방법론"));
children.push(h2("4.1 클래스 불균형 처리와 XGBoost 학습"));
children.push(p("다수 클래스(대물피해)를 소수 클래스 크기에 맞춰 무작위 추출하는 1:1 랜덤 언더샘플링(8,993:8,993)을 적용한 뒤 층화 80/20으로 학습·평가 자료를 분할하였고, 학습 자료의 15%를 검증용으로 분리하여 조기종료에 사용하였다. 언더샘플링의 표본 의존성을 통제하기 위해 서로 다른 시드로 5회 반복하여 평균과 표준편차를 보고한다. XGBoost 초매개변수는 max_depth=6, learning_rate=0.05, subsample=colsample_bytree=0.8, min_child_weight=5이며 격자 탐색으로 적정성을 확인하였다. 비교 기준으로 동일 분할의 로지스틱 회귀, 전체 불균형 자료+scale_pos_weight+임계값 최적화 설계, 범주형 전용 SMOTEN 오버샘플링 설계(Chawla et al., 2002의 명목형 확장)를 함께 평가하였다."));
children.push(h2("4.2 SHAP 기반 탐색 (1단계)"));
children.push(p("TreeExplainer로 SHAP 값을 산출하여 전역 중요도(mean |SHAP|)와 방향을 구하고, SHAP interaction values로 상호작용 후보를 탐색하였다. 상호작용 강도는 (A) 전체 표본 평균 |상호작용|(전체 기여, 빈도 가중)과 (B) 두 조건 동시발생 표본에서의 평균 |상호작용|(건당 강도)으로 분리 산출하였으며, 동일 변수에서 파생된 더미 쌍은 상호배타 구조의 인공물이므로 제외하였다."));
children.push(h2("4.3 확인적 통계 검정 (2단계)"));
children.push(p("변수 수준에서는 카이제곱 검정과 Cramér's V를, 범주 수준에서는 전체 83,297건에 대한 다변량 로지스틱 회귀로 오즈비(OR)·95% 신뢰구간·p값을 추정하였다(기준범주=최빈범주, 완전분리 더미 1개는 추정 제외). 사상자 수(0~26명)에 대해서는 음이항 회귀로 발생률비(IRR)를 추정하였다(과산포 α=3.43 [확인 필요: GLM-NB 대체 각주 수위]). 상호작용 확인은 후보 쌍마다 주효과 14개 변수를 모두 통제한 로지스틱 모형에 상호작용항을 추가하고 Wald 검정 후 Benjamini-Hochberg FDR을 보정하였다(동시발생 100건 미만 쌍 제외). 마지막으로 SHAP 방향 ↔ 로지스틱 부호, 로지스틱 ↔ 음이항 부호의 일치율로 세 모형의 수렴을 확인하였다."));

// 5. 결과
children.push(h1("5. 분석 결과"));
children.push(h2("5.1 예측 성능"));
children.push(p("균형 설계에서 XGBoost는 5회 반복 평균 ROC-AUC 0.785(±0.005), F1-score 0.724(±0.004), Recall 0.762(±0.008)를 기록하였다(표 2, 그림 1). 표준편차가 전 지표에서 0.01 미만으로 표본 의존성은 제한적이었다. SMOTEN 오버샘플링은 F1 0.617, ROC-AUC 0.724로 언더샘플링보다 낮았는데, 범주형 자료에서 합성 표본이 실제 분포에 없는 조합을 생성하기 때문으로 해석된다. 전체 불균형 설계는 ROC-AUC 0.777로 판별력은 유사했으나 기저율 10.8% 환경의 정밀도 붕괴로 F1은 0.352에 그쳤다."));
children.push(mkTable(
  ["설계", "Acc", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"],
  [
    ["XGBoost (균형, 5-seed 평균)", "0.709", "0.689", "0.762", "0.724", "0.785", "0.766"],
    ["Logistic (균형, 대표 분할)", "0.710", "0.687", "0.772", "0.727", "0.783", "0.762"],
    ["XGBoost (SMOTEN, 5-seed)", "0.650", "0.682", "0.563", "0.617", "0.724", "0.706"],
    ["XGBoost (불균형+가중, thr 0.61)", "0.787", "0.262", "0.535", "0.352", "0.777", "0.310"],
  ],
  [2900, 950, 1050, 950, 950, 1100, 1100]
));
children.push(caption("표 2. 클래스 불균형 처리 설계별 성능 비교"));
children.push(img("fig02_roc_pr_curves.png", 580, 238));
children.push(caption("그림 1. ROC 및 Precision-Recall 곡선 (균형 테스트셋)"));

children.push(h2("5.2 확인적 요인 분석: 세 모형의 수렴"));
children.push(p("14개 변수 전부 카이제곱 검정에서 p<0.001이었다. 다변량 로지스틱(표 3)에서 인명피해 오즈를 유의하게 높이는 요인은 정차차량 존재(OR 3.45), 트레일러(2.70), 안전거리미확보(2.07), 승합(1.89), 차로변경(1.63), 졸음(1.57), 주시태만(1.54), 조명시설 없음(1.24) 등이었고, 낮추는 요인은 단독차량화재(0.05), 노면잡물(0.10), 영업소 TG(0.12), 램프(0.30) 등이었다. 사상자 수에 대한 음이항 회귀의 IRR은 공통 유의 47개 더미에서 로지스틱과 방향이 100% 일치하였고, SHAP 방향과 로지스틱 부호의 일치율은 82%였다."));
children.push(mkTable(
  ["요인 (기준범주)", "OR", "95% CI", "요인 (기준범주)", "OR", "95% CI"],
  [
    ["정차차량 (장애없음)", "3.45", "3.08–3.87", "영업소TG (본선)", "0.12", "0.11–0.14"],
    ["트레일러 (승용)", "2.70", "2.18–3.34", "램프 (본선)", "0.30", "0.27–0.33"],
    ["안전거리미확보 (과속)", "2.07", "1.82–2.36", "노면잡물 (과속)", "0.10", "0.08–0.12"],
    ["승합 (승용)", "1.89", "1.72–2.09", "단독차량화재 (과속)", "0.05", "0.03–0.08"],
    ["차로변경 (운행차로주행)", "1.63", "1.43–1.85", "눈 (맑음)", "0.51", "0.42–0.63"],
    ["졸음 (과속)", "1.57", "1.43–1.72", "습기 (건조)", "0.82", "0.72–0.94"],
    ["주시태만 (과속)", "1.54", "1.42–1.66", "조명 없음 (주간)", "1.24", "1.16–1.32"],
  ],
  [2350, 700, 1450, 2350, 700, 1450]
));
children.push(caption("표 3. 다변량 이항 로지스틱 주요 오즈비 (전부 p<0.01; 전체 표는 부록)"));
children.push(img("fig14_shap_categorical_dependence.png", 580, 408));
children.push(caption("그림 2. 범주형 SHAP 의존성 — (a) 주사고원인 (b) 발생지점 (c) 연령 추세 (d) TG 보호효과의 차종별 이질성"));
children.push(img("fig09_or_forest.png", 460, 433));
children.push(caption("그림 3. 다변량 로지스틱 오즈비 forest plot (유의 상위 20)"));

children.push(h2("5.3 상호작용: 탐색과 확인"));
children.push(p("SHAP 상호작용 후보 24쌍 중 FDR q<0.05에서 확인된 주요 쌍은 표 4와 같다. 영업소(TG)×승용(+1.36)은 TG 보호효과가 승용차에서 유의하게 약화됨을 의미하며, 실증적으로 TG 진입 시 인명피해 오즈 감소는 승용 59%, 승합 75%, 화물 90%, 트레일러 95%로 차종 간 이질성이 컸다(그림 4). 주시태만×본선(+0.44)은 본선 고속 구간에서 주시태만의 위험 증폭을, 승합×대형(+0.96)은 대형 승합 사고의 인명피해율(28.3%, 전체 평균의 2.6배)을 반영한다. 반면 SHAP 강도 상위였던 졸음×승용(p=0.304)과 본선×승용(p=0.167)은 주효과 통제 후 유의하지 않아, SHAP 상호작용 순위의 단독 보고가 갖는 허위 발견 위험을 자료로 확인하였다."));
children.push(mkTable(
  ["상호작용 쌍", "계수(log-odds)", "FDR q", "해석"],
  [
    ["영업소(TG) × 승용", "+1.361", "<0.001", "보호효과 약화(이질성)"],
    ["승합 × 차종구분 대형", "+0.964", "<0.001", "위험 증폭(인명피해율 28.3%)"],
    ["주시태만 × 본선", "+0.439", "<0.001", "위험 증폭"],
    ["노면잡물 × 운행차로주행", "−1.640", "<0.001", "보호 시너지"],
    ["노면잡물 × 도로환경 정상", "−1.522", "<0.001", "보호 시너지"],
    ["주시태만 × 영업소(TG)", "−0.935", "<0.001", "저속 구간 완화"],
    ["램프 × 승용", "−0.468", "<0.001", "보호 시너지"],
    ["주시태만 × 핸들과대조작", "−0.328", "<0.001", "중복(완충)"],
    ["과속 × 본선", "−0.256", "0.002", "중복(완충)"],
    ["졸음 × 승용 (검정 미통과)", "−0.060", "0.332", "탐색적 결과로 강등"],
  ],
  [2900, 1600, 1200, 3300]
));
children.push(caption("표 4. SHAP 탐색 → 로지스틱 확인 상호작용 프로파일 (주효과 14개 통제, BH-FDR)"));
children.push(img("fig11_tg_vehicle_casestudy.png", 480, 320));
children.push(caption("그림 4. 사례연구 — 영업소(TG) 보호효과의 차종별 이질성"));

// 6. 논의
children.push(h1("6. 논의"));
[
  "정책적 함의는 세 가지다. 첫째, 인명피해 위험의 중심은 인적요인(주시·거리·졸음)이며 그 효과는 본선·터널 등 고속 구간에서 증폭되므로, 구간 특성과 결합한 인적요인 관리가 우선순위를 갖는다. 둘째, TG 보호효과의 차종별 이질성은 요금소 진입부 감속 체계가 화물·트레일러에 특히 효과적임을 시사하며, 반대로 본선 구간 화물차 관리의 필요성을 부각한다. 셋째, 대형 승합 관련 상호작용은 다인승 차량 사고의 인명피해 규모를 고려한 별도 관리 근거가 된다.",
  "방법론적으로, 누수 변수를 포함한 분석에서는 노면잡물이 위험 증가 요인으로 추정되었으나 실증 인명피해율(1.1% vs 전체 10.8%)과 본 연구의 세 모형 모두 반대 방향을 지지한다. 노면잡물은 사고 '발생' 빈도의 요인일 수 있으나 인명피해 '심화' 요인은 아니며, 두 층위를 구분하지 않으면 상반된 정책 결론에 이를 수 있다. 아울러 SHAP 상호작용 순위의 단독 보고가 갖는 위험(졸음×승용 사례)은 설명가능 기계학습 연구 일반에 적용되는 시사점이다.",
].forEach((t) => children.push(p(t)));

// 7. 결론
children.push(h1("7. 결론 및 한계"));
[
  "본 연구는 전국 고속도로 사고 83,297건에 대해 사고 전 변수 14개만으로 인명피해 발생을 판별하는 XGBoost 모형(ROC-AUC 0.785, F1 0.724)을 구축하고, SHAP 탐색 결과를 다변량 로지스틱·음이항 회귀로 확인하는 2단계 프레임워크를 제안·검증하였다. 세 모형의 효과 방향 수렴과 FDR 보정 상호작용 검정을 통해, 기계학습의 발견을 통계적 추론의 언어로 번역하는 재현 가능한 절차를 제시하였다.",
  "한계는 다음과 같다. 균형 설계의 성능 지표는 50:50 기저율 기준으로 실제 유병률 환경의 운영 성능과 구분해야 하며, 사망·중상·경상을 통합한 이진 타겟은 심각도 순서 정보를 활용하지 못한다. 교통량 등 노출량 보정이 이루어지지 않았으며, '미상' 범주는 정보성 결측일 수 있다. 순서형 심각도 모형, 노출량 결합, 외부 기상·기하구조 자료 연계가 후속 과제다.",
].forEach((t) => children.push(p(t)));

children.push(h1("감사의 글"));
children.push(p("본 연구는 교육부와 대전광역시의 재원으로 대전 RISE 센터의 지원을 받아 수행되었음(2026-RISE-06-013). [확인 필요: 사사 문구 확정]"));

children.push(h1("References"));
[
  "Benjamini, Y. and Hochberg, Y. (1995), Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing, Journal of the Royal Statistical Society: Series B, 57(1), 289-300.",
  "Chawla, N. V., Bowyer, K. W., Hall, L. O. and Kegelmeyer, W. P. (2002), SMOTE: Synthetic Minority Over-sampling Technique, Journal of Artificial Intelligence Research, 16, 321-357.",
  "Chen, T. and Guestrin, C. (2016), XGBoost: A Scalable Tree Boosting System, Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785-794.",
  "Lundberg, S. M. and Lee, S. I. (2017), A Unified Approach to Interpreting Model Predictions, Advances in Neural Information Processing Systems, 30, 4765-4774.",
  "Lundberg, S. M., Erion, G., Chen, H. et al. (2020), From Local Explanations to Global Understanding with Explainable AI for Trees, Nature Machine Intelligence, 2(1), 56-67.",
  "Moon, J., Jang, J. and Lee, S. (2025), Analyzing the Associations between the Fatal Accidents of Older Adult Drivers and Road Environments in Seoul, Korea, Journal of Korean Society of Transportation, 43(2), 161-180. [확인 필요: 원문 대조]",
  "[확인 필요: 국내 문헌 3~5편 — 래퍼런스 폴더 PDF 서지사항 추출 후 추가]",
].forEach((t) =>
  children.push(new Paragraph({
    spacing: { after: 80 }, indent: { left: 400, hanging: 400 },
    children: splitRuns(t, { size: 18 }),
  }))
);

const doc = new Document({
  styles: { default: { document: { run: { font: BODY_FONT, size: 20 } } } },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(__dirname, "APTE_2026_논문초안.docx");
  fs.writeFileSync(out, buf);
  console.log("saved:", out, buf.length, "bytes");
});
