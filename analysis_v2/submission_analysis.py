# -*- coding: utf-8 -*-
"""
APTE submission-grade reanalysis

Core safeguards:
1. Restore three previously target-screened variables (weekend, pavement, sex).
2. Use a fixed 17-variable pre-accident feature set.
3. Split before any model fitting: train 50%, validation 15%, SHAP screening
   15%, independent confirmation/final test 20%.
4. Apply imbalance handling only to training data.
5. Tune decision thresholds and probability calibration only on validation.
6. Select SHAP interaction candidates only on screening data and test them
   only on independent confirmation data with BH-FDR.

The count outcome is intentionally excluded because the repository does not
contain the incident-level casualty count source needed for independent
reproduction.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path

import imblearn
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.ticker import FuncFormatter, NullFormatter
import numpy as np
import pandas as pd
import scipy
from scipy.special import expit, logit
from scipy.stats import norm
import shap
import sklearn
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import statsmodels
from imblearn.metrics import specificity_score
from imblearn.over_sampling import SMOTEN
from xgboost import XGBClassifier
import xgboost


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "submission_outputs_v2"
TABLES = OUT / "tables"
FIGURES = OUT / "figures"
MODELS = OUT / "models"
DATA_OUT = OUT / "data"
for directory in (OUT, TABLES, FIGURES, MODELS, DATA_OUT):
    directory.mkdir(parents=True, exist_ok=True)

PROCESSED_PATH = BASE / "data" / "processed" / "analysis_dataset.csv"
PARTIAL_RAW_PATH = BASE / "data" / "raw" / "5차 전처리 데이터(1).csv"

SEED = 20260716
N_BOOT = 1000
N_SHAP_INTERACTION = 2500
TOP_K_A = 10
TOP_K_B = 10
MIN_SCREEN_COOCCURRENCE = 25
MIN_CONFIRM_COOCCURRENCE = 100
MIN_CONFIRM_EVENTS = 10
NON_SUBSTANTIVE_CATEGORIES = {"미상", "기타", "-"}
REFERENCE_OVERRIDES = {"연령구분": "40대"}

FINAL_VARIABLES = [
    "주사고원인",
    "교통장애요인",
    "발생지점",
    "운전자상태",
    "사고시도로환경",
    "원인차차종",
    "날씨",
    "조명시설",
    "노면상태",
    "연령구분",
    "사고직전차량조작",
    "차종구분",
    "절성토구분",
    "평면선형",
    "주말여부",
    "포장구분",
    "성별",
]


def set_korean_font() -> str:
    candidates = ["Malgun Gothic", "NanumGothic", "Noto Sans CJK KR", "Arial Unicode MS"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((name for name in candidates if name in available), "DejaVu Sans")
    plt.rcParams["font.family"] = chosen
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


FONT_NAME = set_korean_font()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "-": pd.NA, "nan": pd.NA, "<NA>": pd.NA})
    )


def build_reproducible_dataset() -> tuple[pd.DataFrame, dict]:
    processed = pd.read_csv(PROCESSED_PATH, encoding="utf-8-sig")
    raw = pd.read_csv(PARTIAL_RAW_PATH, encoding="utf-8-sig")
    if len(processed) != len(raw):
        raise ValueError("Processed and partial raw row counts differ.")

    raw_target = (
        raw[["사망발생", "중상발생", "경상발생"]]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum(axis=1)
        .gt(0)
        .astype(int)
    )
    target_match = float((raw_target.to_numpy() == processed["injury"].to_numpy()).mean())
    if target_match != 1.0:
        raise ValueError(f"Target alignment failed: {target_match:.4%}")

    data = processed.copy()
    data["주사고원인"] = clean_text(data["주사고원인"]).fillna("미상")
    data["주말여부"] = (
        clean_text(raw["주말_공휴일_여부"])
        .replace({"주말(공휴일)": "주말", "평일": "평일"})
        .fillna("미상")
    )
    data["포장구분"] = (
        clean_text(raw["포장구분"])
        .where(lambda s: s.isin(["콘크리트", "아스팔트"]), "미상")
        .fillna("미상")
    )
    data["성별"] = (
        clean_text(raw["성별"])
        .replace({"남자": "남", "남성": "남", "여자": "여", "여성": "여"})
        .fillna("미상")
    )

    # Day/night is deliberately excluded a priori because lighting includes
    # a structural "not applicable (daytime)" category. This decision does
    # not use the target.
    data = data[FINAL_VARIABLES + ["injury"]].copy()
    for column in FINAL_VARIABLES:
        data[column] = clean_text(data[column]).fillna("미상").astype(str)

    # Deterministic analysis ID: row position plus content hash. It is not an
    # original incident identifier and is labeled accordingly in the paper.
    content = data.astype(str).agg("|".join, axis=1)
    data.insert(
        0,
        "analysis_id",
        [
            f"APTE-{i + 1:06d}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:8]}"
            for i, value in enumerate(content)
        ],
    )

    provenance = {
        "n_rows": int(len(data)),
        "n_predictors": len(FINAL_VARIABLES),
        "target_positive": int(data["injury"].sum()),
        "target_prevalence": float(data["injury"].mean()),
        "partial_raw_target_alignment": target_match,
        "processed_sha256": sha256(PROCESSED_PATH),
        "partial_raw_sha256": sha256(PARTIAL_RAW_PATH),
        "note": (
            "analysis_id is deterministic for reproduction but is not the "
            "source-system accident identifier. Three restored variables are "
            "joined by preserved row position after exact target-vector and "
            "row-count checks; this remains a provenance limitation."
        ),
    }
    data.to_csv(DATA_OUT / "analysis_dataset_v2.csv", index=False, encoding="utf-8-sig")
    return data, provenance


def stratified_four_way_split(data: pd.DataFrame) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    indices = np.arange(len(data))
    y = data["injury"].to_numpy()

    development, confirmation = train_test_split(
        indices, test_size=0.20, stratify=y, random_state=SEED
    )
    train, temp = train_test_split(
        development,
        test_size=0.375,
        stratify=y[development],
        random_state=SEED + 1,
    )
    validation, screening = train_test_split(
        temp,
        test_size=0.50,
        stratify=y[temp],
        random_state=SEED + 2,
    )
    splits = {
        "train": np.sort(train),
        "validation": np.sort(validation),
        "screening": np.sort(screening),
        "confirmation_test": np.sort(confirmation),
    }

    assignment = pd.DataFrame(
        {
            "analysis_id": data["analysis_id"],
            "injury": y,
            "split": "",
        }
    )
    for name, idx in splits.items():
        assignment.loc[idx, "split"] = name
    assignment.to_csv(DATA_OUT / "split_assignment.csv", index=False, encoding="utf-8-sig")

    summary = (
        assignment.groupby("split", sort=False)["injury"]
        .agg(n="size", casualty_n="sum", prevalence="mean")
        .reset_index()
    )
    summary["proportion"] = summary["n"] / len(data)
    summary.to_csv(TABLES / "table01_split_summary.csv", index=False, encoding="utf-8-sig")
    return splits, summary


def optimize_f1_threshold(y_true: np.ndarray, probability: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probability)
    if len(thresholds) == 0:
        return 0.5
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(
        precision[:-1] + recall[:-1], 1e-12
    )
    return float(thresholds[int(np.nanargmax(f1))])


def fit_platt(y_validation: np.ndarray, probability_validation: np.ndarray):
    score = logit(np.clip(probability_validation, 1e-6, 1 - 1e-6)).reshape(-1, 1)
    calibrator = LogisticRegression(penalty=None, solver="lbfgs", max_iter=2000)
    calibrator.fit(score, y_validation)
    return calibrator


def apply_platt(calibrator, probability: np.ndarray) -> np.ndarray:
    score = logit(np.clip(probability, 1e-6, 1 - 1e-6)).reshape(-1, 1)
    return calibrator.predict_proba(score)[:, 1]


def binary_metrics(
    y_true: np.ndarray, probability: np.ndarray, threshold: float
) -> dict[str, float]:
    prediction = probability >= threshold
    return {
        "ROC_AUC": float(roc_auc_score(y_true, probability)),
        "PR_AUC": float(average_precision_score(y_true, probability)),
        "Accuracy": float(accuracy_score(y_true, prediction)),
        "Balanced_Accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "Precision": float(precision_score(y_true, prediction, zero_division=0)),
        "Recall": float(recall_score(y_true, prediction)),
        "Specificity": float(specificity_score(y_true, prediction)),
        "F1": float(f1_score(y_true, prediction)),
        "Brier": float(brier_score_loss(y_true, probability)),
    }


def bootstrap_metrics(
    y_true: np.ndarray,
    predictions: dict[str, tuple[np.ndarray, float]],
    n_boot: int = N_BOOT,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    point_rows = []
    samples: dict[str, list[dict[str, float]]] = {name: [] for name in predictions}
    rng = np.random.default_rng(SEED + 10)
    pos = np.flatnonzero(y_true == 1)
    neg = np.flatnonzero(y_true == 0)

    for name, (probability, threshold) in predictions.items():
        metrics = binary_metrics(y_true, probability, threshold)
        for metric, value in metrics.items():
            point_rows.append(
                {
                    "model": name,
                    "metric": metric,
                    "estimate": value,
                    "threshold": threshold,
                }
            )

    for _ in range(n_boot):
        take = np.concatenate(
            [
                rng.choice(pos, size=len(pos), replace=True),
                rng.choice(neg, size=len(neg), replace=True),
            ]
        )
        for name, (probability, threshold) in predictions.items():
            samples[name].append(binary_metrics(y_true[take], probability[take], threshold))

    point = pd.DataFrame(point_rows)
    sample_frames = {name: pd.DataFrame(rows) for name, rows in samples.items()}
    ci_rows = []
    for row in point.itertuples():
        distribution = sample_frames[row.model][row.metric]
        ci_rows.append(
            {
                **row._asdict(),
                "ci_low": float(distribution.quantile(0.025)),
                "ci_high": float(distribution.quantile(0.975)),
            }
        )
    return pd.DataFrame(ci_rows).drop(columns=["Index"]), sample_frames


def calibration_stats(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    score = logit(np.clip(probability, 1e-6, 1 - 1e-6))
    fit = sm.GLM(
        y_true,
        sm.add_constant(score),
        family=sm.families.Binomial(),
    ).fit()
    return {
        "calibration_intercept": float(fit.params[0]),
        "calibration_slope": float(fit.params[1]),
    }


def xgb_parameters(random_state: int, scale_pos_weight: float = 1.0) -> dict:
    return {
        "n_estimators": 800,
        "learning_rate": 0.05,
        "max_depth": 6,
        "min_child_weight": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_lambda": 1.0,
        "gamma": 0.0,
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "early_stopping_rounds": 60,
        "random_state": random_state,
        "n_jobs": -1,
        "scale_pos_weight": scale_pos_weight,
    }


def fit_models(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
) -> tuple[
    OneHotEncoder,
    dict[str, object],
    dict[str, dict[str, np.ndarray | float]],
    pd.DataFrame,
]:
    x_all = data[FINAL_VARIABLES]
    y_all = data["injury"].to_numpy()
    train = splits["train"]
    validation = splits["validation"]
    screening = splits["screening"]
    confirmation = splits["confirmation_test"]

    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
        dtype=np.float32,
    )
    x_train = encoder.fit_transform(x_all.iloc[train])
    x_validation = encoder.transform(x_all.iloc[validation])
    x_screening = encoder.transform(x_all.iloc[screening])
    x_confirmation = encoder.transform(x_all.iloc[confirmation])
    feature_names = encoder.get_feature_names_out(FINAL_VARIABLES)
    pd.Series(feature_names, name="feature").to_csv(
        DATA_OUT / "onehot_feature_names.csv", index=False, encoding="utf-8-sig"
    )

    y_train = y_all[train]
    y_validation = y_all[validation]
    y_confirmation = y_all[confirmation]

    models: dict[str, object] = {}
    prediction_store: dict[str, dict[str, np.ndarray | float]] = {}
    validation_rows = []

    logistic = LogisticRegression(
        penalty="l2",
        C=1.0,
        solver="lbfgs",
        max_iter=3000,
        random_state=SEED,
    )
    logistic.fit(x_train, y_train)
    models["Logistic"] = logistic

    training_sets: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    training_sets["XGB_natural"] = (x_train, y_train, 1.0)
    class_weight = float((y_train == 0).sum() / (y_train == 1).sum())
    training_sets["XGB_weighted"] = (x_train, y_train, class_weight)

    rng = np.random.default_rng(SEED)
    positive = np.flatnonzero(y_train == 1)
    negative = np.flatnonzero(y_train == 0)
    sampled_negative = rng.choice(negative, size=len(positive), replace=False)
    rus_idx = np.concatenate([positive, sampled_negative])
    rng.shuffle(rus_idx)
    training_sets["XGB_RUS"] = (x_train[rus_idx], y_train[rus_idx], 1.0)

    smoten = SMOTEN(random_state=SEED, k_neighbors=5)
    x_smoten_raw, y_smoten = smoten.fit_resample(
        x_all.iloc[train].reset_index(drop=True), y_train
    )
    x_smoten = encoder.transform(pd.DataFrame(x_smoten_raw, columns=FINAL_VARIABLES))
    training_sets["XGB_SMOTEN"] = (x_smoten, np.asarray(y_smoten), 1.0)
    pd.DataFrame(
        {
            "strategy": ["natural", "weighted", "random_undersampling", "SMOTEN"],
            "training_n": [
                len(y_train),
                len(y_train),
                len(rus_idx),
                len(y_smoten),
            ],
            "training_positive": [
                int(y_train.sum()),
                int(y_train.sum()),
                int(y_train[rus_idx].sum()),
                int(np.asarray(y_smoten).sum()),
            ],
        }
    ).to_csv(TABLES / "training_strategy_counts.csv", index=False, encoding="utf-8-sig")

    for name, (x_fit, y_fit, spw) in training_sets.items():
        model = XGBClassifier(**xgb_parameters(SEED, spw))
        model.fit(
            x_fit,
            y_fit,
            eval_set=[(x_validation, y_validation)],
            verbose=False,
        )
        models[name] = model

    for name, model in models.items():
        validation_raw = model.predict_proba(x_validation)[:, 1]
        confirmation_raw = model.predict_proba(x_confirmation)[:, 1]
        screening_raw = model.predict_proba(x_screening)[:, 1]

        calibrator = fit_platt(y_validation, validation_raw)
        validation_probability = apply_platt(calibrator, validation_raw)
        confirmation_probability = apply_platt(calibrator, confirmation_raw)
        screening_probability = apply_platt(calibrator, screening_raw)
        threshold = optimize_f1_threshold(y_validation, validation_probability)

        validation_metric = binary_metrics(y_validation, validation_probability, threshold)
        validation_rows.append(
            {
                "model": name,
                **validation_metric,
                "validation_threshold": threshold,
                "best_iteration": int(getattr(model, "best_iteration", -1)),
            }
        )
        prediction_store[name] = {
            "validation_raw": validation_raw,
            "validation_probability": validation_probability,
            "screening_raw": screening_raw,
            "screening_probability": screening_probability,
            "confirmation_raw": confirmation_raw,
            "confirmation_probability": confirmation_probability,
            "threshold": threshold,
            "x_screening": x_screening,
            "x_confirmation": x_confirmation,
        }

        if name.startswith("XGB"):
            model.save_model(MODELS / f"{name}.json")

    validation_table = pd.DataFrame(validation_rows).sort_values(
        ["PR_AUC", "ROC_AUC"], ascending=False
    )
    validation_table.to_csv(
        TABLES / "table02_validation_model_selection.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return encoder, models, prediction_store, validation_table


def evaluate_confirmation_models(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
    prediction_store: dict[str, dict[str, np.ndarray | float]],
    validation_table: pd.DataFrame,
) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    confirmation = splits["confirmation_test"]
    y_test = data["injury"].to_numpy()[confirmation]
    selected_xgb = (
        validation_table[validation_table["model"].str.startswith("XGB")]
        .iloc[0]["model"]
    )
    predictions = {
        name: (
            np.asarray(store["confirmation_probability"]),
            float(store["threshold"]),
        )
        for name, store in prediction_store.items()
    }
    metric_ci, bootstrap = bootstrap_metrics(y_test, predictions)

    calibration_rows = []
    for name, (probability, _) in predictions.items():
        calibration_rows.append(
            {
                "model": name,
                **calibration_stats(y_test, probability),
            }
        )
    calibration_table = pd.DataFrame(calibration_rows)
    metric_ci = metric_ci.merge(calibration_table, on="model", how="left")
    metric_ci.to_csv(
        TABLES / "table03_confirmation_performance_ci.csv",
        index=False,
        encoding="utf-8-sig",
    )

    pair_rows = []
    for metric in ["ROC_AUC", "PR_AUC", "F1", "Brier"]:
        difference = bootstrap[selected_xgb][metric] - bootstrap["Logistic"][metric]
        point_selected = metric_ci.loc[
            (metric_ci.model == selected_xgb) & (metric_ci.metric == metric), "estimate"
        ].iloc[0]
        point_logistic = metric_ci.loc[
            (metric_ci.model == "Logistic") & (metric_ci.metric == metric), "estimate"
        ].iloc[0]
        pair_rows.append(
            {
                "metric": metric,
                "selected_model": selected_xgb,
                "selected_estimate": point_selected,
                "logistic_estimate": point_logistic,
                "difference": point_selected - point_logistic,
                "ci_low": float(difference.quantile(0.025)),
                "ci_high": float(difference.quantile(0.975)),
                "bootstrap_two_sided_p": float(
                    min(1.0, 2 * min((difference <= 0).mean(), (difference >= 0).mean()))
                ),
            }
        )
    paired = pd.DataFrame(pair_rows)
    paired.to_csv(
        TABLES / "table04_paired_model_differences.csv",
        index=False,
        encoding="utf-8-sig",
    )

    prediction_frame = pd.DataFrame(
        {
            "analysis_id": data.iloc[confirmation]["analysis_id"].to_numpy(),
            "injury": y_test,
        }
    )
    for name, (probability, threshold) in predictions.items():
        prediction_frame[f"{name}_probability"] = probability
        prediction_frame[f"{name}_prediction"] = (probability >= threshold).astype(int)
    prediction_frame.to_csv(
        DATA_OUT / "confirmation_test_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return selected_xgb, metric_ci, paired


def training_categories_and_references(
    data: pd.DataFrame, train_idx: np.ndarray
) -> tuple[dict[str, list[str]], dict[str, str]]:
    categories = {}
    references = {}
    for variable in FINAL_VARIABLES:
        counts = data.iloc[train_idx][variable].value_counts()
        categories[variable] = sorted(data.iloc[train_idx][variable].unique().tolist())
        preferred = REFERENCE_OVERRIDES.get(variable)
        references[variable] = (
            preferred if preferred in categories[variable] else str(counts.index[0])
        )
    return categories, references


def encode_reference_design(
    frame: pd.DataFrame,
    categories: dict[str, list[str]],
    references: dict[str, str],
) -> pd.DataFrame:
    columns = {}
    for variable in FINAL_VARIABLES:
        for category in categories[variable]:
            if category == references[variable]:
                continue
            columns[f"{variable}={category}"] = (
                frame[variable].astype(str).eq(category).astype(float).to_numpy()
            )
    return pd.DataFrame(columns, index=frame.index)


def fit_confirmation_main_effects(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], dict[str, str]]:
    categories, references = training_categories_and_references(data, splits["train"])
    confirm = data.iloc[splits["confirmation_test"]].copy()
    y = confirm["injury"].to_numpy()
    design = encode_reference_design(confirm, categories, references)

    separated = []
    keep = []
    for column in design.columns:
        on = design[column].to_numpy() == 1
        positives = int(y[on].sum())
        if on.sum() == 0 or positives in (0, int(on.sum())):
            separated.append(
                {
                    "dummy": column,
                    "n": int(on.sum()),
                    "casualty_n": positives,
                    "reason": "complete separation or absent category in confirmation set",
                }
            )
        else:
            keep.append(column)
    separated_table = pd.DataFrame(separated)
    separated_table.to_csv(
        TABLES / "confirmation_separated_dummies.csv",
        index=False,
        encoding="utf-8-sig",
    )
    design_fit = design[keep]
    model = sm.GLM(
        y,
        sm.add_constant(design_fit),
        family=sm.families.Binomial(),
    ).fit(cov_type="HC3", maxiter=300)

    ci = model.conf_int()
    table = pd.DataFrame(
        {
            "dummy": model.params.index,
            "coef": model.params.to_numpy(),
            "robust_se": model.bse.to_numpy(),
            "OR": np.exp(model.params.to_numpy()),
            "CI_low": np.exp(ci[0].to_numpy()),
            "CI_high": np.exp(ci[1].to_numpy()),
            "p_value": model.pvalues.to_numpy(),
        }
    )
    table = table[table["dummy"] != "const"].copy()
    table["q_value_BH"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["variable"] = table["dummy"].str.split("=", n=1).str[0]
    table["category"] = table["dummy"].str.split("=", n=1).str[1]
    table["reference"] = table["variable"].map(references)
    category_n = []
    category_casualty_n = []
    for row in table.itertuples():
        mask = confirm[row.variable].astype(str).eq(row.category).to_numpy()
        category_n.append(int(mask.sum()))
        category_casualty_n.append(int(y[mask].sum()))
    table["category_n"] = category_n
    table["category_casualty_n"] = category_casualty_n
    table["category_rate"] = table["category_casualty_n"] / table["category_n"]
    table["confirmed_q05"] = table["q_value_BH"] < 0.05
    table = table.sort_values(["q_value_BH", "p_value"])
    table.to_csv(
        TABLES / "table05_confirmation_main_effects.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return table, design_fit, categories, references


def feature_parent(feature: str) -> str:
    matches = [variable for variable in FINAL_VARIABLES if feature.startswith(variable + "_")]
    if not matches:
        raise ValueError(f"Cannot identify parent variable for {feature}")
    return max(matches, key=len)


def feature_category(feature: str, parent: str) -> str:
    return feature[len(parent) + 1 :]


def pretty_feature(feature: str) -> str:
    parent = feature_parent(feature)
    return f"{parent}={feature_category(feature, parent)}"


def screen_and_confirm_interactions(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
    encoder: OneHotEncoder,
    selected_model: XGBClassifier,
    prediction_store: dict[str, dict[str, np.ndarray | float]],
    base_confirmation_design: pd.DataFrame,
    references: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    feature_names = np.asarray(encoder.get_feature_names_out(FINAL_VARIABLES))
    x_screen = np.asarray(prediction_store["x_screening"])
    screen_idx = splits["screening"]
    confirm_idx = splits["confirmation_test"]
    y_confirm = data.iloc[confirm_idx]["injury"].to_numpy()

    explainer = shap.TreeExplainer(selected_model)
    shap_values = np.asarray(explainer.shap_values(x_screen))
    np.save(MODELS / "shap_values_screening.npy", shap_values)

    importance_rows = []
    for j, feature in enumerate(feature_names):
        present = x_screen[:, j] == 1
        importance_rows.append(
            {
                "feature": feature,
                "variable": feature_parent(feature),
                "mean_abs_shap": float(np.abs(shap_values[:, j]).mean()),
                "mean_shap_when_present": (
                    float(shap_values[present, j].mean()) if present.sum() >= 30 else np.nan
                ),
                "screen_n_present": int(present.sum()),
            }
        )
    importance = pd.DataFrame(importance_rows).sort_values(
        "mean_abs_shap", ascending=False
    )
    importance.to_csv(
        TABLES / "table06_screening_shap_importance.csv",
        index=False,
        encoding="utf-8-sig",
    )

    rng = np.random.default_rng(SEED + 30)
    n_take = min(N_SHAP_INTERACTION, len(x_screen))
    take = rng.choice(len(x_screen), size=n_take, replace=False)
    x_sample = x_screen[take]
    interaction_values = np.asarray(explainer.shap_interaction_values(x_sample))
    np.save(MODELS / "shap_interaction_screening_sample.npy", interaction_values)
    mean_abs = np.abs(interaction_values).mean(axis=0)
    np.fill_diagonal(mean_abs, 0)

    reference_features = {
        f"{variable}_{reference}" for variable, reference in references.items()
    }
    pair_rows = []
    for i in range(len(feature_names)):
        feature_1 = feature_names[i]
        parent_1 = feature_parent(feature_1)
        if feature_1 in reference_features:
            continue
        for j in range(i + 1, len(feature_names)):
            feature_2 = feature_names[j]
            parent_2 = feature_parent(feature_2)
            if feature_2 in reference_features or parent_1 == parent_2:
                continue
            both = (x_sample[:, i] == 1) & (x_sample[:, j] == 1)
            n_both = int(both.sum())
            pair_rows.append(
                {
                    "feature_1": feature_1,
                    "feature_2": feature_2,
                    "parent_1": parent_1,
                    "parent_2": parent_2,
                    "rankA_mean_abs": float(mean_abs[i, j]),
                    "screen_sample_n_both": n_both,
                    "rankB_per_occurrence": (
                        float(np.abs(interaction_values[both, i, j]).mean() * 2)
                        if n_both >= MIN_SCREEN_COOCCURRENCE
                        else np.nan
                    ),
                    "screen_joint_signed": (
                        float(interaction_values[both, i, j].mean() * 2)
                        if n_both >= MIN_SCREEN_COOCCURRENCE
                        else np.nan
                    ),
                }
            )
    pair_table = pd.DataFrame(pair_rows)
    eligible = pair_table[
        (pair_table["screen_sample_n_both"] >= MIN_SCREEN_COOCCURRENCE)
        & ~pair_table.apply(
            lambda row: (
                feature_category(row["feature_1"], row["parent_1"])
                in NON_SUBSTANTIVE_CATEGORIES
                or feature_category(row["feature_2"], row["parent_2"])
                in NON_SUBSTANTIVE_CATEGORIES
            ),
            axis=1,
        )
    ].copy()
    top_a = eligible.nlargest(TOP_K_A, "rankA_mean_abs")
    top_b = eligible.dropna(subset=["rankB_per_occurrence"]).nlargest(
        TOP_K_B, "rankB_per_occurrence"
    )
    candidates = (
        pd.concat([top_a, top_b])
        .drop_duplicates(["feature_1", "feature_2"])
        .copy()
        .reset_index(drop=True)
    )
    candidate_keys_a = set(zip(top_a.feature_1, top_a.feature_2))
    candidate_keys_b = set(zip(top_b.feature_1, top_b.feature_2))
    candidates["selected_rankA"] = [
        (a, b) in candidate_keys_a for a, b in zip(candidates.feature_1, candidates.feature_2)
    ]
    candidates["selected_rankB"] = [
        (a, b) in candidate_keys_b for a, b in zip(candidates.feature_1, candidates.feature_2)
    ]

    x_confirm_all = encoder.transform(data.iloc[confirm_idx][FINAL_VARIABLES])
    feature_index = {name: i for i, name in enumerate(feature_names)}
    x_base = base_confirmation_design.reset_index(drop=True)
    x_base_constant = sm.add_constant(x_base)

    confirm_rows = []
    for row in candidates.itertuples(index=False):
        product = (
            x_confirm_all[:, feature_index[row.feature_1]]
            * x_confirm_all[:, feature_index[row.feature_2]]
        ).astype(float)
        n_both = int(product.sum())
        casualty_n = int(y_confirm[product == 1].sum())
        result = {
            **row._asdict(),
            "confirmation_n_both": n_both,
            "confirmation_casualty_n_both": casualty_n,
            "confirmation_rate_both": (
                float(casualty_n / n_both) if n_both else np.nan
            ),
            "interaction_coef": np.nan,
            "interaction_OR_ratio": np.nan,
            "CI_low": np.nan,
            "CI_high": np.nan,
            "p_value": np.nan,
            "note": "",
        }
        if (
            n_both < MIN_CONFIRM_COOCCURRENCE
            or casualty_n < MIN_CONFIRM_EVENTS
            or (n_both - casualty_n) < MIN_CONFIRM_EVENTS
        ):
            result["note"] = (
                "excluded: confirmation cell below minimum "
                "co-occurrence/event/non-event rule"
            )
        else:
            interaction = pd.Series(product, name="INTERACTION")
            design = pd.concat([x_base_constant, interaction], axis=1)
            try:
                fit = sm.GLM(
                    y_confirm,
                    design,
                    family=sm.families.Binomial(),
                ).fit(cov_type="HC3", maxiter=300)
                coef = float(fit.params["INTERACTION"])
                low, high = fit.conf_int().loc["INTERACTION"].tolist()
                result.update(
                    {
                        "interaction_coef": coef,
                        "interaction_OR_ratio": float(math.exp(coef)),
                        "CI_low": float(math.exp(low)),
                        "CI_high": float(math.exp(high)),
                        "p_value": float(fit.pvalues["INTERACTION"]),
                    }
                )
            except Exception as error:
                result["note"] = f"fit failed: {type(error).__name__}"
        confirm_rows.append(result)

    confirmation = pd.DataFrame(confirm_rows)
    tested = confirmation["p_value"].notna()
    confirmation["q_value_BH"] = np.nan
    if tested.any():
        confirmation.loc[tested, "q_value_BH"] = multipletests(
            confirmation.loc[tested, "p_value"], method="fdr_bh"
        )[1]
    confirmation["confirmed_q05"] = confirmation["q_value_BH"] < 0.05
    confirmation = confirmation.sort_values(
        ["confirmed_q05", "q_value_BH", "rankA_mean_abs"],
        ascending=[False, True, False],
    )
    confirmation.to_csv(
        TABLES / "table07_independent_interaction_confirmation.csv",
        index=False,
        encoding="utf-8-sig",
    )
    candidates.to_csv(
        TABLES / "interaction_candidates_screening_only.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return importance, confirmation, shap_values


def wilson_interval(success: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    if total == 0:
        return np.nan, np.nan
    z = norm.ppf(1 - alpha / 2)
    phat = success / total
    denominator = 1 + z**2 / total
    center = (phat + z**2 / (2 * total)) / denominator
    half = (
        z
        * math.sqrt(phat * (1 - phat) / total + z**2 / (4 * total**2))
        / denominator
    )
    return center - half, center + half


def build_conditional_rate_table(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
    interaction_table: pd.DataFrame,
) -> pd.DataFrame:
    confirmed = interaction_table[interaction_table["confirmed_q05"]].copy()
    if confirmed.empty:
        return pd.DataFrame()
    top = confirmed.iloc[0]
    confirm = data.iloc[splits["confirmation_test"]].copy()

    def decode(feature: str) -> tuple[str, str]:
        variable = feature_parent(feature)
        return variable, feature[len(variable) + 1 :]

    variable_1, category_1 = decode(top.feature_1)
    variable_2, category_2 = decode(top.feature_2)
    a = confirm[variable_1].eq(category_1)
    b = confirm[variable_2].eq(category_2)
    rows = []
    for a_value, b_value, label in [
        (False, False, "둘 다 없음"),
        (True, False, f"{category_1}만"),
        (False, True, f"{category_2}만"),
        (True, True, "두 조건 동시"),
    ]:
        mask = (a == a_value) & (b == b_value)
        total = int(mask.sum())
        casualty = int(confirm.loc[mask, "injury"].sum())
        low, high = wilson_interval(casualty, total)
        rows.append(
            {
                "feature_1": top.feature_1,
                "feature_2": top.feature_2,
                "cell": label,
                "n": total,
                "casualty_n": casualty,
                "rate": casualty / total if total else np.nan,
                "CI_low": low,
                "CI_high": high,
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(
        TABLES / "table08_top_confirmed_interaction_rates.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return table


def plot_study_design(split_summary: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 3.8), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (0.02, 0.28, 0.17, 0.44, "학습 50%", "전처리 규칙·인코더 학습\n모형 적합"),
        (0.23, 0.28, 0.17, 0.44, "검증 15%", "조기종료·모형선택\n확률보정·임계값 결정"),
        (0.44, 0.28, 0.17, 0.44, "SHAP 탐색 15%", "주효과 설명\n상호작용 후보 고정"),
        (0.65, 0.28, 0.17, 0.44, "독립 확인 20%", "상호작용 검정·BH-FDR\n최종 자연기저율 평가"),
        (0.86, 0.28, 0.12, 0.44, "투고 결과", "표·그림·본문\n근거 매핑"),
    ]
    colors = ["#DCE6F1", "#E2F0D9", "#FFF2CC", "#FCE4D6", "#E4DFEC"]
    for (x, y, w, h, title, body), color in zip(boxes, colors):
        box = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            facecolor=color,
            edgecolor="#444444",
            linewidth=1.0,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center", weight="bold")
        ax.text(x + w / 2, y + h * 0.35, body, ha="center", va="center", fontsize=9)
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i + 1][0]
        ax.add_patch(
            FancyArrowPatch(
                (x1 + 0.005, 0.5),
                (x2 - 0.005, 0.5),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.0,
                color="#555555",
            )
        )
    total = int(split_summary["n"].sum())
    positive = int((split_summary["n"] * split_summary["prevalence"]).round().sum())
    ax.text(
        0.5,
        0.91,
        f"사전 고정 17개 사고 전 변수 · 총 {total:,}건 · 인명피해 {positive:,}건",
        ha="center",
        va="center",
        fontsize=12,
        weight="bold",
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "figure01_independent_design_flow.png", bbox_inches="tight")
    plt.close(fig)


def plot_roc_pr(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
    selected_model: str,
    prediction_store: dict[str, dict[str, np.ndarray | float]],
):
    y = data.iloc[splits["confirmation_test"]]["injury"].to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), dpi=220)
    styles = {
        selected_model: ("#C00000", "-", 2.2),
        "Logistic": ("#595959", "--", 1.8),
    }
    for name in [selected_model, "Logistic"]:
        probability = np.asarray(prediction_store[name]["confirmation_probability"])
        fpr, tpr, _ = roc_curve(y, probability)
        precision, recall, _ = precision_recall_curve(y, probability)
        axes[0].plot(
            fpr,
            tpr,
            color=styles[name][0],
            linestyle=styles[name][1],
            linewidth=styles[name][2],
            label=f"{name} (AUC={roc_auc_score(y, probability):.3f})",
        )
        axes[1].plot(
            recall,
            precision,
            color=styles[name][0],
            linestyle=styles[name][1],
            linewidth=styles[name][2],
            label=f"{name} (AP={average_precision_score(y, probability):.3f})",
        )
    axes[0].plot([0, 1], [0, 1], ":", color="#A6A6A6")
    axes[1].axhline(y.mean(), linestyle=":", color="#A6A6A6", label=f"기저율={y.mean():.3f}")
    axes[0].set(xlabel="False positive rate", ylabel="True positive rate", title="ROC 곡선")
    axes[1].set(xlabel="Recall", ylabel="Precision", title="Precision-Recall 곡선")
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle("독립 확인셋의 최종 판별 성능(자연 기저율)", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure02_confirmation_roc_pr.png", bbox_inches="tight")
    plt.close(fig)


def plot_calibration(
    data: pd.DataFrame,
    splits: dict[str, np.ndarray],
    selected_model: str,
    prediction_store: dict[str, dict[str, np.ndarray | float]],
):
    y = data.iloc[splits["confirmation_test"]]["injury"].to_numpy()
    fig, ax = plt.subplots(figsize=(6.3, 5.2), dpi=220)
    for name, color, marker in [
        (selected_model, "#C00000", "o"),
        ("Logistic", "#595959", "s"),
    ]:
        probability = np.asarray(prediction_store[name]["confirmation_probability"])
        observed, predicted = calibration_curve(
            y, probability, n_bins=10, strategy="quantile"
        )
        ax.plot(
            predicted,
            observed,
            marker=marker,
            linewidth=1.8,
            color=color,
            label=f"{name} (Brier={brier_score_loss(y, probability):.3f})",
        )
    ax.plot([0, 1], [0, 1], ":", color="#7F7F7F", label="완전 보정")
    ax.set(
        xlabel="평균 예측확률",
        ylabel="관찰 인명피해율",
        title="독립 확인셋 확률 보정",
        xlim=(0, 0.65),
        ylim=(0, 0.65),
    )
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure03_confirmation_calibration.png", bbox_inches="tight")
    plt.close(fig)


def plot_model_metrics(metric_ci: pd.DataFrame):
    metrics = ["ROC_AUC", "PR_AUC", "F1", "Recall", "Precision", "Brier"]
    models = metric_ci["model"].drop_duplicates().tolist()
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.2), dpi=220)
    for plot_index, (ax, metric) in enumerate(zip(axes.ravel(), metrics)):
        table = metric_ci[metric_ci.metric == metric].set_index("model").loc[models]
        y_pos = np.arange(len(models))
        ax.errorbar(
            table["estimate"],
            y_pos,
            xerr=[
                table["estimate"] - table["ci_low"],
                table["ci_high"] - table["estimate"],
            ],
            fmt="o",
            color="#1F4E79",
            ecolor="#7F8C8D",
            capsize=2.5,
        )
        ax.set_yticks(y_pos)
        ax.set_yticklabels(models if plot_index % 3 == 0 else [])
        ax.set_title(metric)
        ax.grid(axis="x", alpha=0.2)
        if metric != "Brier":
            ax.set_xlim(max(0, table["ci_low"].min() - 0.04), min(1, table["ci_high"].max() + 0.04))
    fig.suptitle("독립 확인셋 모형 성능과 층화 bootstrap 95% 신뢰구간", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure04_model_metric_comparison.png", bbox_inches="tight")
    plt.close(fig)


def plot_shap_importance(importance: pd.DataFrame):
    top = importance.head(20).sort_values("mean_abs_shap")
    fig, ax = plt.subplots(figsize=(8.4, 7.2), dpi=220)
    labels = [pretty_feature(feature) for feature in top["feature"]]
    ax.barh(labels, top["mean_abs_shap"], color="#4472C4")
    ax.set_xlabel("mean |SHAP| (screening set)")
    ax.set_title("독립 SHAP 탐색셋 전역 중요도 상위 20", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure05_screening_shap_importance.png", bbox_inches="tight")
    plt.close(fig)


def plot_main_effect_forest(main_effects: pd.DataFrame):
    top = (
        main_effects[
            main_effects["confirmed_q05"]
            & ~main_effects["category"].isin(NON_SUBSTANTIVE_CATEGORIES)
        ]
        .assign(abs_log_or=lambda x: np.abs(np.log(x["OR"])))
        .nlargest(20, "abs_log_or")
        .sort_values("OR")
    )
    fig, ax = plt.subplots(figsize=(8.6, 8.0), dpi=220)
    y_pos = np.arange(len(top))
    colors = np.where(top["OR"] >= 1, "#C00000", "#2F75B5")
    ax.errorbar(
        top["OR"],
        y_pos,
        xerr=[top["OR"] - top["CI_low"], top["CI_high"] - top["OR"]],
        fmt="none",
        ecolor="#7F7F7F",
        capsize=2.4,
        linewidth=1,
    )
    ax.scatter(top["OR"], y_pos, color=colors, s=35, zorder=3)
    ax.axvline(1, color="#404040", linestyle="--", linewidth=0.9)
    labels = [
        f"{r.variable}: {r.category} (ref. {r.reference})" for r in top.itertuples()
    ]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xscale("log")
    lower = max(0.003, float(top["CI_low"].min()) * 0.8)
    upper = float(top["CI_high"].max()) * 1.2
    ax.set_xlim(lower, upper)
    ax.set_xticks(
        [value for value in (0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30) if lower <= value <= upper]
    )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("조정 오즈비(95% CI, log scale)")
    ax.set_title("독립 확인셋의 BH-FDR 유의 주효과 중 |log OR| 상위 20", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure06_confirmation_main_effect_forest.png", bbox_inches="tight")
    plt.close(fig)


def plot_interaction_confirmation(interactions: pd.DataFrame):
    tested = interactions.dropna(subset=["interaction_OR_ratio"]).copy()
    if tested.empty:
        return
    tested = tested.sort_values("interaction_OR_ratio")
    fig_height = max(5.0, 0.43 * len(tested) + 1.7)
    fig, ax = plt.subplots(figsize=(9.2, fig_height), dpi=220)
    y_pos = np.arange(len(tested))
    colors = np.where(tested["confirmed_q05"], "#C00000", "#A6A6A6")
    ax.errorbar(
        tested["interaction_OR_ratio"],
        y_pos,
        xerr=[
            tested["interaction_OR_ratio"] - tested["CI_low"],
            tested["CI_high"] - tested["interaction_OR_ratio"],
        ],
        fmt="none",
        ecolor="#7F7F7F",
        capsize=2.3,
        linewidth=1,
    )
    ax.scatter(tested["interaction_OR_ratio"], y_pos, color=colors, s=38, zorder=3)
    ax.axvline(1, color="#404040", linestyle="--", linewidth=0.9)
    labels = [
        f"{pretty_feature(r.feature_1)} × {pretty_feature(r.feature_2)}\n"
        f"q={r.q_value_BH:.3g}"
        for r in tested.itertuples()
    ]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xscale("log")
    lower = max(0.1, float(tested["CI_low"].min()) * 0.85)
    upper = float(tested["CI_high"].max()) * 1.1
    ax.set_xlim(lower, upper)
    ax.set_xticks(
        [value for value in (0.2, 0.3, 0.5, 1, 2, 3, 5, 10) if lower <= value <= upper]
    )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("상호작용 오즈비 비율(95% CI, log scale)")
    ax.set_title("SHAP 탐색 후보의 독립 확인셋 검정", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(
        FIGURES / "figure07_independent_interaction_confirmation.png",
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_top_interaction_rates(rate_table: pd.DataFrame):
    if rate_table.empty:
        return
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=220)
    x = np.arange(len(rate_table))
    rates = rate_table["rate"].to_numpy()
    low = rate_table["CI_low"].to_numpy()
    high = rate_table["CI_high"].to_numpy()
    ax.bar(x, rates, color=["#D9E2F3", "#A9D18E", "#FFD966", "#C00000"])
    ax.errorbar(
        x,
        rates,
        yerr=[rates - low, high - rates],
        fmt="none",
        color="#404040",
        capsize=3,
    )
    for i, row in enumerate(rate_table.itertuples()):
        ax.text(i, row.rate + 0.012, f"{row.rate:.1%}\n(n={row.n:,})", ha="center", fontsize=9)
    title = (
        f"{pretty_feature(rate_table.iloc[0]['feature_1'])} × "
        f"{pretty_feature(rate_table.iloc[0]['feature_2'])}"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(rate_table["cell"])
    ax.set_ylabel("인명피해 발생률(95% Wilson CI)")
    ax.set_title(f"독립 확인셋의 최상위 확인 상호작용\n{title}", weight="bold")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure08_top_confirmed_interaction_rates.png", bbox_inches="tight")
    plt.close(fig)


def create_claim_evidence_map(
    provenance: dict,
    split_summary: pd.DataFrame,
    selected_model: str,
    metric_ci: pd.DataFrame,
    main_effects: pd.DataFrame,
    interactions: pd.DataFrame,
):
    selected_metrics = metric_ci[metric_ci.model == selected_model].set_index("metric")
    confirmed_main = main_effects[main_effects.confirmed_q05]
    confirmed_interactions = interactions[interactions.confirmed_q05]
    tested_interactions = interactions[interactions["p_value"].notna()]
    rows = [
        {
            "claim_id": "C01",
            "claim": f"분석자료는 {provenance['n_rows']:,}건이며 인명피해 발생률은 {provenance['target_prevalence']:.2%}이다.",
            "evidence_file": "submission_outputs_v2/data/analysis_dataset_v2.csv",
            "status": "verified",
        },
        {
            "claim_id": "C02",
            "claim": "자료는 학습·검증·SHAP 탐색·독립 확인으로 분리되었다.",
            "evidence_file": "submission_outputs_v2/tables/table01_split_summary.csv",
            "status": "verified",
        },
        {
            "claim_id": "C03",
            "claim": (
                f"검증셋에서 선택된 {selected_model}의 독립 확인셋 ROC-AUC는 "
                f"{selected_metrics.loc['ROC_AUC','estimate']:.3f} "
                f"(95% CI {selected_metrics.loc['ROC_AUC','ci_low']:.3f}-"
                f"{selected_metrics.loc['ROC_AUC','ci_high']:.3f})이다."
            ),
            "evidence_file": "submission_outputs_v2/tables/table03_confirmation_performance_ci.csv",
            "status": "verified",
        },
        {
            "claim_id": "C04",
            "claim": f"독립 확인셋에서 BH q<0.05인 주효과 더미는 {len(confirmed_main)}개이다.",
            "evidence_file": "submission_outputs_v2/tables/table05_confirmation_main_effects.csv",
            "status": "verified",
        },
        {
            "claim_id": "C05",
            "claim": (
                f"SHAP으로 사전 선별한 {len(interactions)}개 후보 중 안정성 기준을 "
                f"충족해 독립 확인셋에서 검정한 {len(tested_interactions)}개 후보에서 "
                f"BH q<0.05인 상호작용은 {len(confirmed_interactions)}개이다."
            ),
            "evidence_file": "submission_outputs_v2/tables/table07_independent_interaction_confirmation.csv",
            "status": "verified",
        },
    ]
    pd.DataFrame(rows).to_csv(
        TABLES / "claim_evidence_map.csv", index=False, encoding="utf-8-sig"
    )


def write_manifest(provenance: dict, selected_model: str, validation_table: pd.DataFrame):
    manifest = {
        "analysis_name": "APTE independent screening-confirmation reanalysis",
        "seed": SEED,
        "split": {
            "train": 0.50,
            "validation": 0.15,
            "screening": 0.15,
            "confirmation_test": 0.20,
        },
        "selection_primary_metric": "validation PR-AUC",
        "threshold_selection": "validation-set maximum F1, then frozen",
        "interaction_screening_rules": {
            "exclude_categories": sorted(NON_SUBSTANTIVE_CATEGORIES),
            "minimum_screening_joint_n": MIN_SCREEN_COOCCURRENCE,
            "minimum_confirmation_joint_n": MIN_CONFIRM_COOCCURRENCE,
            "minimum_confirmation_events": MIN_CONFIRM_EVENTS,
            "minimum_confirmation_non_events": MIN_CONFIRM_EVENTS,
            "fdr_family": "all candidates satisfying confirmation stability rules",
        },
        "selected_model": selected_model,
        "final_variables": FINAL_VARIABLES,
        "excluded_a_priori": {
            "주야구분": (
                "structural redundancy with lighting variable containing "
                "'해당없음(주간)' category; outcome not used"
            )
        },
        "provenance": provenance,
        "versions": {
            "python": sys.version,
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "xgboost": xgboost.__version__,
            "shap": shap.__version__,
            "statsmodels": statsmodels.__version__,
            "imbalanced_learn": imblearn.__version__,
            "matplotlib": matplotlib.__version__,
            "font": FONT_NAME,
        },
        "validation_ranking": validation_table.to_dict(orient="records"),
    }
    (OUT / "reproducibility_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    print("[1/8] Building reproducible 17-variable dataset", flush=True)
    data, provenance = build_reproducible_dataset()

    print("[2/8] Creating independent four-way split", flush=True)
    splits, split_summary = stratified_four_way_split(data)

    print("[3/8] Fitting Logistic and four XGBoost imbalance strategies", flush=True)
    encoder, models, prediction_store, validation_table = fit_models(data, splits)

    print("[4/8] Evaluating untouched natural-prevalence confirmation set", flush=True)
    selected_name, metric_ci, paired = evaluate_confirmation_models(
        data, splits, prediction_store, validation_table
    )
    print(f"Selected model by validation PR-AUC: {selected_name}", flush=True)

    print("[5/8] Fitting robust main-effect inference on confirmation set", flush=True)
    main_effects, base_design, categories, references = fit_confirmation_main_effects(
        data, splits
    )
    (OUT / "reference_categories.json").write_text(
        json.dumps(references, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("[6/8] SHAP screening and independent interaction confirmation", flush=True)
    importance, interactions, shap_values = screen_and_confirm_interactions(
        data,
        splits,
        encoder,
        models[selected_name],
        prediction_store[selected_name],
        base_design,
        references,
    )
    rate_table = build_conditional_rate_table(data, splits, interactions)

    print("[7/8] Rendering submission figures", flush=True)
    plot_study_design(split_summary)
    plot_roc_pr(data, splits, selected_name, prediction_store)
    plot_calibration(data, splits, selected_name, prediction_store)
    plot_model_metrics(metric_ci)
    plot_shap_importance(importance)
    plot_main_effect_forest(main_effects)
    plot_interaction_confirmation(interactions)
    plot_top_interaction_rates(rate_table)

    print("[8/8] Writing claim map and reproducibility manifest", flush=True)
    create_claim_evidence_map(
        provenance,
        split_summary,
        selected_name,
        metric_ci,
        main_effects,
        interactions,
    )
    write_manifest(provenance, selected_name, validation_table)

    summary = {
        "selected_model": selected_name,
        "confirmation_n": int(len(splits["confirmation_test"])),
        "confirmation_prevalence": float(
            data.iloc[splits["confirmation_test"]]["injury"].mean()
        ),
        "confirmed_main_effects": int(main_effects["confirmed_q05"].sum()),
        "interaction_candidates": int(len(interactions)),
        "interaction_candidates_tested": int(interactions["p_value"].notna().sum()),
        "confirmed_interactions": int(interactions["confirmed_q05"].sum()),
        "output_dir": str(OUT),
    }
    (OUT / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
