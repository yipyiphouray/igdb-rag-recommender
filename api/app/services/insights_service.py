from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app import config


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _coerce_value(value: str | None) -> Any:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False

    try:
        if any(marker in text for marker in (".", "e", "E")):
            return float(text)
        return int(text)
    except ValueError:
        return text


def _read_csv(path: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            rows = [
                {key: _coerce_value(value) for key, value in row.items()}
                for row in csv.DictReader(file)
            ]
    except OSError:
        return []

    if limit is None:
        return rows
    return rows[:limit]


@lru_cache(maxsize=1)
def get_insights_summary() -> dict[str, Any]:
    summary = _load_json(config.APP_INSIGHT_SUMMARY_PATH)

    summary["dashboard"] = {
        "descriptive": {
            "kpi_snapshot": _read_csv(config.DESCRIPTIVE_DIR / "kpi_snapshot.csv"),
            "top_genres": _read_csv(config.DESCRIPTIVE_DIR / "top_genres.csv", limit=8),
            "top_platforms": _read_csv(config.DESCRIPTIVE_DIR / "top_platforms.csv", limit=8),
            "rating_coverage": _read_csv(config.DESCRIPTIVE_DIR / "rating_coverage.csv"),
            "rating_bands": _read_csv(config.DESCRIPTIVE_DIR / "rating_bands.csv"),
            "popularity_signals": _read_csv(
                config.DESCRIPTIVE_DIR / "popularity_signal_availability.csv",
                limit=8,
            ),
            "metadata_richness": _read_csv(
                config.DESCRIPTIVE_DIR / "metadata_richness_bands.csv"
            ),
            "playtime_bands": _read_csv(
                config.DESCRIPTIVE_DIR / "playtime_band_distribution.csv"
            ),
        },
        "diagnostic": {
            "takeaways": _read_csv(config.DIAGNOSTIC_DIR / "diagnostic_takeaways.csv"),
            "dataset_snapshot": _read_csv(
                config.DIAGNOSTIC_DIR / "diagnostic_dataset_snapshot.csv"
            ),
            "hidden_gems_by_genre": _read_csv(
                config.DIAGNOSTIC_DIR / "hidden_gem_by_genre.csv",
                limit=8,
            ),
            "hidden_gems_by_platform_family": _read_csv(
                config.DIAGNOSTIC_DIR / "hidden_gem_by_platform_family.csv"
            ),
            "genre_rating_summary": _read_csv(
                config.DIAGNOSTIC_DIR / "genre_rating_summary.csv",
                limit=8,
            ),
            "platform_family_rating_summary": _read_csv(
                config.DIAGNOSTIC_DIR / "platform_family_rating_summary.csv"
            ),
            "rating_band_popscore_summary": _read_csv(
                config.DIAGNOSTIC_DIR / "rating_band_popscore_summary.csv"
            ),
            "user_critic_agreement": _read_csv(
                config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv"
            ),
        },
    }

    return summary
