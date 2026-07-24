from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app import config


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def get_insights_summary() -> dict[str, Any]:
    summary = _load_json(config.APP_INSIGHT_SUMMARY_PATH)
    summary["dashboard"] = _load_json(config.APP_INSIGHTS_DASHBOARD_PATH)
    return summary
