from __future__ import annotations

from functools import lru_cache
from typing import Any

from app import config
from src.app.data_loader import load_json_artifact


@lru_cache(maxsize=1)
def get_insights_summary() -> dict[str, Any]:
    summary = dict(load_json_artifact(config.APP_INSIGHT_SUMMARY_PATH))
    dashboard_path = getattr(
        config,
        "APP_INSIGHTS_DASHBOARD_PATH",
        config.APP_DATA_DIR / "app_insights_dashboard.json",
    )
    summary["dashboard"] = load_json_artifact(dashboard_path)
    return summary
