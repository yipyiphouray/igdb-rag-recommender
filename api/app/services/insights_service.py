from __future__ import annotations

import json
from json import JSONDecodeError
from functools import lru_cache
from pathlib import Path
from typing import Any

from app import config


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def get_insights_summary() -> dict[str, Any]:
    summary = _load_json(config.APP_INSIGHT_SUMMARY_PATH)
    dashboard_path = getattr(
        config,
        "APP_INSIGHTS_DASHBOARD_PATH",
        config.APP_DATA_DIR / "app_insights_dashboard.json",
    )
    summary["dashboard"] = _load_json(dashboard_path)
    return summary
