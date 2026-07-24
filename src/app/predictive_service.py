from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.app import config


PREDICTIVE_ARTIFACTS = {
    "model_metrics": config.PREDICTIVE_DIR / "model_metrics.json",
    "feature_importance": config.PREDICTIVE_DIR / "feature_importance.csv",
    "model_predictions": config.PREDICTIVE_DIR / "model_predictions.parquet",
    "confusion_matrix": config.PREDICTIVE_DIR / "confusion_matrix.png",
    "roc_curve": config.PREDICTIVE_DIR / "roc_curve.png",
}


def predictive_status() -> dict[str, bool]:
    return {name: path.exists() for name, path in PREDICTIVE_ARTIFACTS.items()}


def load_predictions() -> pd.DataFrame:
    path = PREDICTIVE_ARTIFACTS["model_predictions"]
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def artifact_path(name: str) -> Path:
    return PREDICTIVE_ARTIFACTS[name]

