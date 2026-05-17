from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


FEATURE_COLUMNS = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PlantOps failure-risk baseline.")
    parser.add_argument("--data", default="ml/data/ai4i2020.csv", help="Path to AI4I 2020 CSV.")
    parser.add_argument("--artifact", default="ml/artifacts/failure_model.joblib")
    parser.add_argument("--report", default="ml/reports/model_report.md")
    args = parser.parse_args()

    try:
        import joblib
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
        from sklearn.model_selection import train_test_split
    except ImportError as exc:
        raise SystemExit(
            "Missing ML dependencies. Install scikit-learn, pandas, and joblib before training."
        ) from exc

    data_path = Path(args.data)
    fallback_used = not data_path.exists()
    frame = _load_frame(data_path, fallback_used, pd)

    train, test = train_test_split(
        frame,
        test_size=0.25,
        random_state=42,
        stratify=frame["target"],
    )
    x_train = train[FEATURE_COLUMNS]
    y_train = train["target"]
    x_test = test[FEATURE_COLUMNS]
    y_test = test["target"]

    models: dict[str, Any] = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
    }

    results = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test)[:, 1]
        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "f1": f1_score(y_test, predictions, zero_division=0),
            "roc_auc": roc_auc_score(y_test, probabilities),
        }

    best_name = max(results, key=lambda name: results[name]["f1"])
    best = results[best_name]
    artifact_path = Path(args.artifact)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": best["model"],
            "feature_columns": FEATURE_COLUMNS,
            "model_version": f"{best_name}-v0",
            "fallback_data_used": fallback_used,
        },
        artifact_path,
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_report(report_path, results, best_name, fallback_used)


def _load_frame(data_path: Path, fallback_used: bool, pd: Any) -> Any:
    if not fallback_used:
        frame = pd.read_csv(data_path)
        rename_map = {
            "Air temperature [K]": "air_temperature_k",
            "Process temperature [K]": "process_temperature_k",
            "Rotational speed [rpm]": "rotational_speed_rpm",
            "Torque [Nm]": "torque_nm",
            "Tool wear [min]": "tool_wear_min",
            "Machine failure": "target",
        }
        return frame.rename(columns=rename_map)[FEATURE_COLUMNS + ["target"]].dropna()

    return pd.DataFrame(
        [
            [298.1, 308.6, 1551, 42.8, 0, 0],
            [298.5, 309.1, 1408, 46.3, 3, 0],
            [299.2, 310.5, 1320, 58.2, 145, 1],
            [300.4, 311.8, 1280, 65.1, 210, 1],
            [297.8, 308.2, 1602, 35.4, 12, 0],
            [301.2, 312.2, 1210, 71.0, 230, 1],
            [298.9, 309.4, 1500, 38.0, 40, 0],
            [300.8, 311.0, 1265, 62.5, 188, 1],
        ],
        columns=FEATURE_COLUMNS + ["target"],
    )


def _write_report(report_path: Path, results: dict[str, dict[str, Any]], best_name: str, fallback_used: bool) -> None:
    lines = [
        "# Predictive Maintenance Model Report",
        "",
        f"Fallback synthetic data used: `{fallback_used}`",
        "",
        "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, metrics in results.items():
        lines.append(
            f"| {name} | {metrics['accuracy']:.3f} | {metrics['precision']:.3f} | "
            f"{metrics['recall']:.3f} | {metrics['f1']:.3f} | {metrics['roc_auc']:.3f} |"
        )
    lines.extend(["", f"Selected model: `{best_name}`", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
