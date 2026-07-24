from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.app import config


DESCRIPTIVE_TABLES: dict[str, tuple[str, int | None]] = {
    "kpi_snapshot": ("kpi_snapshot.csv", None),
    "top_genres": ("top_genres.csv", 8),
    "top_platforms": ("top_platforms.csv", 8),
    "rating_coverage": ("rating_coverage.csv", None),
    "rating_bands": ("rating_bands.csv", None),
    "popularity_signals": ("popularity_signal_availability.csv", 8),
    "metadata_richness": ("metadata_richness_bands.csv", None),
    "playtime_bands": ("playtime_band_distribution.csv", None),
}


DIAGNOSTIC_TABLES: dict[str, tuple[str, int | None]] = {
    "takeaways": ("diagnostic_takeaways.csv", None),
    "dataset_snapshot": ("diagnostic_dataset_snapshot.csv", None),
    "hidden_gems_by_genre": ("hidden_gem_by_genre.csv", 8),
    "hidden_gems_by_platform_family": ("hidden_gem_by_platform_family.csv", None),
    "genre_rating_summary": ("genre_rating_summary.csv", 8),
    "platform_family_rating_summary": ("platform_family_rating_summary.csv", None),
    "rating_band_popscore_summary": ("rating_band_popscore_summary.csv", None),
    "user_critic_agreement": ("user_critic_agreement_summary.csv", None),
}


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

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = [
            {key: _coerce_value(value) for key, value in row.items()}
            for row in csv.DictReader(file)
        ]

    if limit is None:
        return rows
    return rows[:limit]


def _build_section(
    source_dir: Path,
    table_mapping: dict[str, tuple[str, int | None]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        output_name: _read_csv(source_dir / filename, limit=limit)
        for output_name, (filename, limit) in table_mapping.items()
    }


def build_insights_dashboard() -> dict[str, Any]:
    return {
        "descriptive": _build_section(config.DESCRIPTIVE_DIR, DESCRIPTIVE_TABLES),
        "diagnostic": _build_section(config.DIAGNOSTIC_DIR, DIAGNOSTIC_TABLES),
    }


def main() -> None:
    config.APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dashboard = build_insights_dashboard()
    output_path = config.APP_DATA_DIR / "app_insights_dashboard.json"
    output_path.write_text(
        json.dumps(dashboard, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote insights dashboard artifact: {output_path}")


if __name__ == "__main__":
    main()
