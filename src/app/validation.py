from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.app import config
from src.app.constants import HIDDEN_GEM_VISIBILITY_PERCENTILE, MIN_RATING_COUNT, QUALITY_THRESHOLD


REQUIRED_CATALOG_COLUMNS = {
    "game_id",
    "name",
    "release_year",
    "extraction_cohort",
    "genres_list",
    "platforms_list",
    "total_rating",
    "total_rating_count",
    "rating_reliable_flag",
    "hidden_gem_balanced_flag",
}


def artifact_audit() -> dict[str, bool]:
    return {
        "database_exists": config.DATABASE_PATH.exists(),
        "descriptive_dir_exists": config.DESCRIPTIVE_DIR.exists(),
        "diagnostic_dir_exists": config.DIAGNOSTIC_DIR.exists(),
        "hidden_gem_candidates_exists": (config.DIAGNOSTIC_DIR / "hidden_gem_candidates.csv").exists(),
        "rag_dir_exists": config.RAG_DIR.exists(),
        "app_catalog_exists": config.APP_CATALOG_PATH.exists() or config.APP_CATALOG_CSV_PATH.exists(),
        "app_hidden_gems_exists": config.APP_HIDDEN_GEMS_PATH.exists() or config.APP_HIDDEN_GEMS_CSV_PATH.exists(),
        "filter_options_exists": config.APP_FILTER_OPTIONS_PATH.exists(),
    }


def validate_catalog(catalog: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_CATALOG_COLUMNS.difference(catalog.columns)
    if missing:
        issues.append(f"Missing required catalog columns: {sorted(missing)}")
    if "game_id" in catalog and catalog["game_id"].duplicated().any():
        issues.append("Catalog contains duplicate game_id values.")
    if "total_rating" in catalog:
        invalid = catalog["total_rating"].dropna().lt(0).any() or catalog["total_rating"].dropna().gt(100).any()
        if invalid:
            issues.append("Catalog contains total_rating values outside 0-100.")
    if "platforms_list" in catalog:
        missing_platforms = catalog["platforms_list"].fillna("").eq("").sum()
        if missing_platforms:
            issues.append(f"{missing_platforms} catalog rows are missing platforms_list.")
    return issues


def validate_hidden_gems(hidden_gems: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if hidden_gems.empty:
        issues.append("Hidden-gem artifact is empty.")
        return issues

    checks = {
        "total_rating": hidden_gems["total_rating"].fillna(-1) >= QUALITY_THRESHOLD,
        "total_rating_count": hidden_gems["total_rating_count"].fillna(0) >= MIN_RATING_COUNT,
        "custom_interest_percentile": hidden_gems["visibility_percentile_eligible_pool"].fillna(1)
        <= HIDDEN_GEM_VISIBILITY_PERCENTILE,
    }
    for name, mask in checks.items():
        if not mask.all():
            issues.append(f"Hidden-gem rule failed for column/check: {name}")
    return issues


def ensure_directories(paths: list[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

