# -*- coding: utf-8 -*-
"""Render English-language figures for a JKST-style submission."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import FuncFormatter, NullFormatter
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "submission_outputs_v2"
TABLES = OUT / "tables"
FIGURES = OUT / "figures_en"
DATA = OUT / "data"
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

VARIABLE_LABELS = {
    "주사고원인": "Primary cause",
    "교통장애요인": "Traffic obstruction",
    "발생지점": "Crash location",
    "운전자상태": "Driver state",
    "사고시도로환경": "Road environment",
    "원인차차종": "Causal vehicle",
    "날씨": "Weather",
    "조명시설": "Lighting",
    "노면상태": "Surface condition",
    "연령구분": "Driver age",
    "사고직전차량조작": "Pre-crash maneuver",
    "차종구분": "Vehicle class",
    "절성토구분": "Cut/fill terrain",
    "평면선형": "Horizontal alignment",
    "주말여부": "Weekend",
    "포장구분": "Pavement",
    "성별": "Sex",
}

CATEGORY_LABELS = {
    "과속": "Speeding",
    "노면잡물": "Road debris",
    "주시태만": "Inattention",
    "졸음": "Drowsiness",
    "단독차량화재": "Single-vehicle fire",
    "안전거리미확보": "Insufficient headway",
    "동물침입": "Animal intrusion",
    "도로사정": "Road condition",
    "적재불량": "Improper loading",
    "타이어파손": "Tire failure",
    "추월불량": "Unsafe passing",
    "장애없음": "No obstruction",
    "정차차량": "Stopped vehicle",
    "정체": "Congestion",
    "본선": "Mainline",
    "영업소(TG)": "Tollgate (TG)",
    "램프": "Ramp",
    "터널": "Tunnel",
    "휴게소": "Service area",
    "정상": "Normal",
    "낙하물": "Fallen object",
    "포트홀": "Pothole",
    "승용": "Passenger car",
    "화물": "Truck",
    "승합": "Van",
    "트레일러": "Trailer",
    "특수": "Special vehicle",
    "맑음": "Clear",
    "눈": "Snow",
    "해당없음(주간)": "Not applicable (daytime)",
    "작동": "Operational",
    "없음": "None",
    "건조": "Dry",
    "미상": "Unknown",
    "운행차로주행": "Lane keeping",
    "차로변경": "Lane change",
    "핸들과대조작": "Excessive steering",
    "중형": "Medium",
    "소형": "Small",
    "대형": "Large",
    "평지": "Level",
    "직선": "Straight",
    "좌커브": "Left curve",
    "아스팔트": "Asphalt",
    "콘크리트": "Concrete",
    "여": "Female",
    "남": "Male",
}


def english_feature(feature: str, variable: str | None = None) -> str:
    if variable is None:
        matches = [
            name for name in VARIABLE_LABELS if feature.startswith(name + "_")
        ]
        variable = max(matches, key=len)
    category = feature[len(variable) + 1 :]
    return (
        f"{VARIABLE_LABELS.get(variable, variable)}="
        f"{CATEGORY_LABELS.get(category, category)}"
    )


def english_effect(row) -> str:
    return (
        f"{VARIABLE_LABELS.get(row.variable, row.variable)}: "
        f"{CATEGORY_LABELS.get(row.category, row.category)} "
        f"(ref. {CATEGORY_LABELS.get(row.reference, row.reference)})"
    )


def render_design_flow():
    summary = pd.read_csv(TABLES / "table01_split_summary.csv", encoding="utf-8-sig")
    counts = summary.set_index("split")["n"].to_dict()
    boxes = [
        ("Training 50%", f"n={counts['train']:,}\nfit preprocessing and models"),
        ("Validation 15%", f"n={counts['validation']:,}\nselect model, calibrate,\nfreeze threshold"),
        ("SHAP screening 15%", f"n={counts['screening']:,}\nrank and freeze\ninteraction candidates"),
        ("Independent confirmation 20%", f"n={counts['confirmation_test']:,}\nfinal performance,\nrobust ORs and BH-FDR"),
        ("Submission outputs", "tables, figures,\nclaim-evidence map"),
    ]
    colors = ["#D9E2F3", "#E2F0D9", "#FFF2CC", "#FCE4D6", "#E4DFEC"]
    fig, ax = plt.subplots(figsize=(14, 3.4), dpi=220)
    ax.axis("off")
    centers = np.linspace(0.10, 0.90, len(boxes))
    width, height = 0.16, 0.50
    for index, ((title, detail), color, center) in enumerate(
        zip(boxes, colors, centers)
    ):
        patch = FancyBboxPatch(
            (center - width / 2, 0.25),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=color,
            edgecolor="#555555",
            linewidth=1.0,
        )
        ax.add_patch(patch)
        ax.text(center, 0.58, title, ha="center", va="center", weight="bold", fontsize=10)
        ax.text(center, 0.40, detail, ha="center", va="center", fontsize=8.5)
        if index < len(boxes) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (center + width / 2, 0.50),
                    (centers[index + 1] - width / 2, 0.50),
                    arrowstyle="-|>",
                    mutation_scale=10,
                    linewidth=1.0,
                    color="#666666",
                )
            )
    ax.set_title(
        "Independent screening-confirmation design: 83,297 crashes, 8,993 casualties",
        fontsize=13,
        weight="bold",
        pad=8,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_1_independent_design.png", bbox_inches="tight")
    plt.close(fig)


def render_roc_pr():
    predictions = pd.read_csv(
        DATA / "confirmation_test_predictions.csv", encoding="utf-8-sig"
    )
    y = predictions["injury"].to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), dpi=220)
    for model, color, line in [
        ("XGB_natural", "#C00000", "-"),
        ("Logistic", "#666666", "--"),
    ]:
        probability = predictions[f"{model}_probability"].to_numpy()
        fpr, tpr, _ = roc_curve(y, probability)
        precision, recall, _ = precision_recall_curve(y, probability)
        axes[0].plot(
            fpr,
            tpr,
            color=color,
            linestyle=line,
            linewidth=2,
            label=f"{model} (AUC={roc_auc_score(y, probability):.3f})",
        )
        axes[1].plot(
            recall,
            precision,
            color=color,
            linestyle=line,
            linewidth=2,
            label=f"{model} (AP={average_precision_score(y, probability):.3f})",
        )
    axes[0].plot([0, 1], [0, 1], ":", color="#AAAAAA")
    axes[0].set(xlabel="False-positive rate", ylabel="True-positive rate", title="ROC curve")
    axes[1].axhline(y.mean(), linestyle=":", color="#AAAAAA", label=f"Prevalence={y.mean():.3f}")
    axes[1].set(xlabel="Recall", ylabel="Precision", title="Precision-recall curve")
    for ax in axes:
        ax.legend(frameon=False, fontsize=8.5)
        ax.grid(alpha=0.2)
    fig.suptitle("Final discrimination on the untouched confirmation set", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_2_confirmation_roc_pr.png", bbox_inches="tight")
    plt.close(fig)


def render_calibration():
    predictions = pd.read_csv(
        DATA / "confirmation_test_predictions.csv", encoding="utf-8-sig"
    )
    y = predictions["injury"].to_numpy()
    fig, ax = plt.subplots(figsize=(6.1, 5.2), dpi=220)
    for model, color, marker in [
        ("XGB_natural", "#C00000", "o"),
        ("Logistic", "#666666", "s"),
    ]:
        probability = predictions[f"{model}_probability"].to_numpy()
        observed, predicted = calibration_curve(
            y, probability, n_bins=10, strategy="quantile"
        )
        ax.plot(
            predicted,
            observed,
            marker=marker,
            color=color,
            linewidth=1.8,
            label=f"{model} (Brier={brier_score_loss(y, probability):.3f})",
        )
    ax.plot([0, 0.65], [0, 0.65], ":", color="#888888", label="Perfect calibration")
    ax.set(
        xlim=(0, 0.65),
        ylim=(0, 0.65),
        xlabel="Mean predicted probability",
        ylabel="Observed casualty proportion",
        title="Probability calibration on the confirmation set",
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_3_confirmation_calibration.png", bbox_inches="tight")
    plt.close(fig)


def render_model_metrics():
    metric_ci = pd.read_csv(
        TABLES / "table03_confirmation_performance_ci.csv", encoding="utf-8-sig"
    )
    metrics = ["ROC_AUC", "PR_AUC", "F1", "Recall", "Precision", "Brier"]
    models = metric_ci["model"].drop_duplicates().tolist()
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.5), dpi=220)
    for index, (ax, metric) in enumerate(zip(axes.ravel(), metrics)):
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
        ax.set_yticklabels(models if index % 3 == 0 else [])
        ax.set_title(metric.replace("_", "-"))
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle("Confirmation-set performance with stratified bootstrap 95% CIs", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_4_model_metrics.png", bbox_inches="tight")
    plt.close(fig)


def render_shap():
    importance = pd.read_csv(
        TABLES / "table06_screening_shap_importance.csv", encoding="utf-8-sig"
    )
    top = importance.head(20).sort_values("mean_abs_shap")
    labels = [
        english_feature(row.feature, row.variable) for row in top.itertuples()
    ]
    fig, ax = plt.subplots(figsize=(8.2, 7.0), dpi=220)
    ax.barh(labels, top["mean_abs_shap"], color="#4472C4")
    ax.set_xlabel("Mean |SHAP| on the independent screening set")
    ax.set_title("Top 20 category-level SHAP contributions", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_5_screening_shap.png", bbox_inches="tight")
    plt.close(fig)


def render_main_effects():
    effects = pd.read_csv(
        TABLES / "table05_confirmation_main_effects.csv", encoding="utf-8-sig"
    )
    top = (
        effects[
            effects["confirmed_q05"]
            & ~effects["category"].isin(["미상", "기타", "-"])
        ]
        .assign(abs_log_or=lambda frame: np.abs(np.log(frame["OR"])))
        .nlargest(20, "abs_log_or")
        .sort_values("OR")
    )
    fig, ax = plt.subplots(figsize=(8.5, 7.8), dpi=220)
    y_pos = np.arange(len(top))
    colors = np.where(top["OR"] >= 1, "#C00000", "#2F75B5")
    ax.errorbar(
        top["OR"],
        y_pos,
        xerr=[top["OR"] - top["CI_low"], top["CI_high"] - top["OR"]],
        fmt="none",
        ecolor="#7F7F7F",
        capsize=2.4,
    )
    ax.scatter(top["OR"], y_pos, color=colors, s=35, zorder=3)
    ax.axvline(1, color="#404040", linestyle="--", linewidth=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([english_effect(row) for row in top.itertuples()], fontsize=8.3)
    ax.set_xscale("log")
    lower = max(0.003, float(top["CI_low"].min()) * 0.8)
    upper = float(top["CI_high"].max()) * 1.2
    ax.set_xlim(lower, upper)
    ax.set_xticks(
        [value for value in (0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30) if lower <= value <= upper]
    )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("Adjusted odds ratio (95% CI, log scale)")
    ax.set_title("Top confirmed main effects by |log OR| (BH-FDR q<0.05)", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_6_main_effects.png", bbox_inches="tight")
    plt.close(fig)


def render_interactions():
    interactions = pd.read_csv(
        TABLES / "table07_independent_interaction_confirmation.csv",
        encoding="utf-8-sig",
    )
    tested = interactions.dropna(subset=["interaction_OR_ratio"]).sort_values(
        "interaction_OR_ratio"
    )
    fig, ax = plt.subplots(figsize=(9.0, 4.8), dpi=220)
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
    )
    ax.scatter(tested["interaction_OR_ratio"], y_pos, color=colors, s=38, zorder=3)
    ax.axvline(1, color="#404040", linestyle="--", linewidth=0.9)
    labels = []
    for row in tested.itertuples():
        labels.append(
            f"{english_feature(row.feature_1, row.parent_1)} × "
            f"{english_feature(row.feature_2, row.parent_2)}\nq={row.q_value_BH:.3g}"
        )
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
    ax.set_xlabel("Interaction odds-ratio ratio (95% CI, log scale)")
    ax.set_title("Independent confirmation of SHAP-screened interactions", weight="bold")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_7_interactions.png", bbox_inches="tight")
    plt.close(fig)


def render_top_rate():
    rates = pd.read_csv(
        TABLES / "table08_top_confirmed_interaction_rates.csv", encoding="utf-8-sig"
    )
    cell_labels = {
        "둘 다 없음": "Neither",
        "승합만": "Van only",
        "대형만": "Large only",
        "두 조건 동시": "Both",
    }
    fig, ax = plt.subplots(figsize=(7.0, 4.8), dpi=220)
    x = np.arange(len(rates))
    values = rates["rate"].to_numpy()
    ax.bar(x, values, color=["#D9E2F3", "#A9D18E", "#FFD966", "#C00000"])
    ax.errorbar(
        x,
        values,
        yerr=[
            values - rates["CI_low"].to_numpy(),
            rates["CI_high"].to_numpy() - values,
        ],
        fmt="none",
        color="#404040",
        capsize=3,
    )
    for index, row in enumerate(rates.itertuples()):
        ax.text(
            index,
            row.rate + 0.012,
            f"{row.rate:.1%}\n(n={row.n:,})",
            ha="center",
            fontsize=9,
        )
    ax.set_xticks(x)
    ax.set_xticklabels([cell_labels.get(value, value) for value in rates["cell"]])
    ax.set_ylabel("Observed casualty proportion (95% Wilson CI)")
    ax.set_title("Confirmed van × large-vehicle interaction", weight="bold")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure_8_van_large_rates.png", bbox_inches="tight")
    plt.close(fig)


def main():
    render_design_flow()
    render_roc_pr()
    render_calibration()
    render_model_metrics()
    render_shap()
    render_main_effects()
    render_interactions()
    render_top_rate()
    print(FIGURES)


if __name__ == "__main__":
    main()
