from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ad_mri_similarity_network import (  # noqa: E402
    build_feature_sets,
    evaluate_binary_classifier,
    evaluate_binary_classifier_cv,
    generate_synthetic_structural_data,
)
from ad_mri_similarity_network.plotting import (  # noqa: E402
    plot_cv_performance_table,
    plot_group_mean_networks,
    plot_performance_table,
)


def main() -> None:
    examples_dir = ROOT / "examples"
    figures_dir = ROOT / "figures"
    examples_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    df = generate_synthetic_structural_data(n_controls=90, n_ad=90, random_state=42)
    sample_path = examples_dir / "synthetic_structural_mri.csv"
    df.to_csv(sample_path, index=False)

    features = build_feature_sets(df, cost=0.25, alpha=0.01)
    y = df["diagnosis"].to_numpy()

    rows = []
    cv_rows = []
    fold_rows = []
    feature_sets = {
        "structural": features["structural_features"],
        "network": features["network_features"],
        "combined": features["all_features"],
    }
    for feature_name, X in feature_sets.items():
        for model_name in ["logistic", "centroid"]:
            result = evaluate_binary_classifier(X, y, model=model_name)
            result["feature_set"] = feature_name
            rows.append(result)

            cv_result = evaluate_binary_classifier_cv(
                X,
                y,
                model=model_name,
                n_splits=5,
                random_state=42,
            )
            cv_summary = {k: v for k, v in cv_result.items() if k != "folds"}
            cv_summary["feature_set"] = feature_name
            cv_rows.append(cv_summary)
            for fold in cv_result["folds"]:
                fold = dict(fold)
                fold["feature_set"] = feature_name
                fold_rows.append(fold)

    performance = pd.DataFrame(rows)
    cv_performance = pd.DataFrame(cv_rows)
    cv_folds = pd.DataFrame(fold_rows)
    performance_path = examples_dir / "demo_classification_metrics.csv"
    cv_performance_path = examples_dir / "demo_cv_classification_metrics.csv"
    cv_fold_path = examples_dir / "demo_cv_fold_metrics.csv"
    performance.drop(columns=["confusion_matrix"]).to_csv(performance_path, index=False)
    cv_performance.to_csv(cv_performance_path, index=False)
    cv_folds.drop(columns=["confusion_matrix"]).to_csv(cv_fold_path, index=False)

    plot_group_mean_networks(
        features["weighted_networks"],
        y,
        figures_dir / "group_mean_similarity_matrices.svg",
    )
    plot_performance_table(
        performance.drop(columns=["confusion_matrix"]),
        figures_dir / "classification_performance.svg",
    )
    plot_cv_performance_table(
        cv_performance,
        figures_dir / "cv_classification_performance.svg",
    )

    print("Saved synthetic data:", sample_path)
    print("Saved metrics:", performance_path)
    print("Saved CV metrics:", cv_performance_path)
    print(performance[["feature_set", "model", "accuracy", "sensitivity", "specificity", "auc", "f1"]])
    print(cv_performance[["feature_set", "model", "accuracy_mean", "sensitivity_mean", "specificity_mean", "auc_mean", "f1_mean"]])


if __name__ == "__main__":
    main()
