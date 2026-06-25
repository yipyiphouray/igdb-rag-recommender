from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app import config
from src.app.constants import (
    HIDDEN_GEM_VISIBILITY_PERCENTILE,
    LIST_DELIMITER,
    MIN_RATING_COUNT,
    QUALITY_THRESHOLD,
)
from src.app.formatting import join_list, split_list
from src.app.validation import ensure_directories, validate_catalog, validate_hidden_gems


def read_sql(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)


def relation_list(
    conn: sqlite3.Connection,
    query: str,
    output_column: str,
) -> pd.DataFrame:
    values = read_sql(conn, query)
    if values.empty:
        return pd.DataFrame(columns=["game_id", output_column])
    values["value"] = values["value"].fillna("").astype(str).str.strip()
    values = values[values["value"] != ""].drop_duplicates()
    grouped = (
        values.sort_values(["game_id", "value"])
        .groupby("game_id")["value"]
        .apply(join_list)
        .reset_index(name=output_column)
    )
    return grouped


def save_table(df: pd.DataFrame, parquet_path: Path, csv_path: Path) -> str:
    try:
        df.to_parquet(parquet_path, index=False)
        if csv_path.exists():
            csv_path.unlink()
        return str(parquet_path)
    except Exception as exc:
        df.to_csv(csv_path, index=False)
        print(f"Warning: could not write {parquet_path.name} ({exc}). Wrote CSV fallback.")
        return str(csv_path)


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def add_relation_lists(conn: sqlite3.Connection, catalog: pd.DataFrame) -> pd.DataFrame:
    relation_queries = {
        "genres_list": """
            SELECT gg.game_id, ge.name AS value
            FROM game_genres gg
            JOIN genres ge ON gg.genre_id = ge.genre_id
        """,
        "themes_list": """
            SELECT gt.game_id, th.name AS value
            FROM game_themes gt
            JOIN themes th ON gt.theme_id = th.theme_id
        """,
        "keywords_list": """
            SELECT gk.game_id, kw.name AS value
            FROM game_keywords gk
            JOIN keywords kw ON gk.keyword_id = kw.keyword_id
        """,
        "platforms_list": """
            SELECT gp.game_id, p.name AS value
            FROM game_platforms gp
            JOIN platforms p ON gp.platform_id = p.platform_id
        """,
        "platform_families_list": """
            SELECT gp.game_id, COALESCE(pf.name, 'Unknown / No Family') AS value
            FROM game_platforms gp
            JOIN platforms p ON gp.platform_id = p.platform_id
            LEFT JOIN platform_families pf ON p.platform_family_id = pf.platform_family_id
        """,
        "platform_types_list": """
            SELECT gp.game_id, COALESCE(pt.name, 'Unknown Type') AS value
            FROM game_platforms gp
            JOIN platforms p ON gp.platform_id = p.platform_id
            LEFT JOIN platform_types pt ON p.platform_type_id = pt.platform_type_id
        """,
        "developers_list": """
            SELECT ic.game_id, c.name AS value
            FROM involved_companies ic
            JOIN companies c ON ic.company_id = c.company_id
            WHERE ic.developer = 1
        """,
        "publishers_list": """
            SELECT ic.game_id, c.name AS value
            FROM involved_companies ic
            JOIN companies c ON ic.company_id = c.company_id
            WHERE ic.publisher = 1
        """,
        "game_modes_list": """
            SELECT gmb.game_id, gm.name AS value
            FROM game_modes_bridge gmb
            JOIN game_modes gm ON gmb.game_mode_id = gm.game_mode_id
        """,
        "player_perspectives_list": """
            SELECT gpp.game_id, pp.name AS value
            FROM game_player_perspectives gpp
            JOIN player_perspectives pp
                ON gpp.player_perspective_id = pp.player_perspective_id
        """,
    }

    for output_column, query in relation_queries.items():
        catalog = catalog.merge(relation_list(conn, query, output_column), on="game_id", how="left")
        catalog[output_column] = catalog[output_column].fillna("")

    return catalog


def build_catalog(conn: sqlite3.Connection) -> pd.DataFrame:
    base_query = """
        WITH first_screenshot AS (
            SELECT game_id, MIN(url) AS screenshot_url
            FROM screenshots
            WHERE url IS NOT NULL AND TRIM(url) <> ''
            GROUP BY game_id
        ),
        multiplayer_flags AS (
            SELECT
                game_id,
                1 AS has_multiplayer_detail,
                MAX(COALESCE(online_coop, 0)) AS online_coop_flag,
                MAX(COALESCE(offline_coop, 0)) AS offline_coop_flag,
                MAX(COALESCE(split_screen, 0)) AS split_screen_flag
            FROM multiplayer_modes
            GROUP BY game_id
        )
        SELECT
            g.game_id,
            g.name,
            g.slug,
            g.release_year,
            g.first_release_date_iso,
            g.summary,
            g.storyline,
            c.url AS cover_url,
            fs.screenshot_url,
            g.total_rating,
            g.total_rating_count,
            g.rating,
            g.rating_count,
            g.aggregated_rating,
            g.aggregated_rating_count,
            gt.type_name AS game_type_name,
            gs.status_name AS game_status_name,
            ec.cohort AS extraction_cohort,
            ec.selection_rank,
            ec.adjusted_quality_score,
            ec.popularity_basis AS selection_popularity_basis,
            ec.popularity_score AS selection_popularity_score,
            psi.custom_interest_score,
            psi.custom_interest_percentile,
            CASE WHEN psi.custom_interest_score IS NOT NULL THEN 1 ELSE 0 END AS popscore_available_flag,
            CASE WHEN g.total_rating IS NOT NULL THEN 1 ELSE 0 END AS rating_available_flag,
            CASE
                WHEN g.total_rating IS NOT NULL
                 AND g.total_rating_count >= 25 THEN 1 ELSE 0
            END AS rating_reliable_flag,
            CASE
                WHEN g.total_rating >= 80
                 AND g.total_rating_count >= 25 THEN 1 ELSE 0
            END AS high_rated_flag,
            CASE WHEN gt.type_name = 'Main Game' THEN 1 ELSE 0 END AS main_game_flag,
            CASE
                WHEN g.total_rating IS NULL THEN 'Unrated'
                WHEN g.total_rating >= 90 THEN 'Excellent'
                WHEN g.total_rating >= 80 THEN 'Highly rated'
                WHEN g.total_rating >= 70 THEN 'Good'
                WHEN g.total_rating >= 50 THEN 'Mixed / average'
                ELSE 'Lower rated'
            END AS rating_band,
            CASE WHEN g.summary IS NOT NULL AND TRIM(g.summary) <> '' THEN 1 ELSE 0 END AS has_summary,
            CASE WHEN g.storyline IS NOT NULL AND TRIM(g.storyline) <> '' THEN 1 ELSE 0 END AS has_storyline,
            COALESCE(ttb.normally / 3600.0, NULL) AS normal_playtime_hours,
            COALESCE(ttb.completely / 3600.0, NULL) AS completionist_playtime_hours,
            COALESCE(mf.has_multiplayer_detail, 0) AS has_multiplayer_detail,
            COALESCE(mf.online_coop_flag, 0) AS online_coop_flag,
            COALESCE(mf.offline_coop_flag, 0) AS offline_coop_flag,
            COALESCE(mf.split_screen_flag, 0) AS split_screen_flag
        FROM games g
        LEFT JOIN game_types gt ON g.game_type_id = gt.game_type_id
        LEFT JOIN game_statuses gs ON g.game_status_id = gs.game_status_id
        LEFT JOIN extraction_cohorts ec ON g.game_id = ec.game_id
        LEFT JOIN covers c ON g.cover_id = c.cover_id
        LEFT JOIN first_screenshot fs ON g.game_id = fs.game_id
        LEFT JOIN vw_game_popscore_igdb_interest psi ON g.game_id = psi.game_id
        LEFT JOIN game_time_to_beats ttb ON g.game_id = ttb.game_id
        LEFT JOIN multiplayer_flags mf ON g.game_id = mf.game_id
    """
    catalog = read_sql(conn, base_query)
    catalog = add_relation_lists(conn, catalog)

    for source_col, count_col in [
        ("genres_list", "num_genres"),
        ("themes_list", "num_themes"),
        ("keywords_list", "num_keywords"),
        ("platforms_list", "num_platforms"),
    ]:
        catalog[count_col] = catalog[source_col].apply(lambda value: len(split_list(value)))

    mode_text = catalog["game_modes_list"].fillna("").str.lower()
    detail_flag = catalog["has_multiplayer_detail"].fillna(0).astype(int)
    catalog["multiplayer_flag"] = (
        detail_flag.eq(1)
        | mode_text.str.contains("multiplayer", regex=False)
        | mode_text.str.contains("co-operative", regex=False)
        | mode_text.str.contains("co-op", regex=False)
    ).astype(int)

    hidden_gem_eligible_mask = (
        (catalog["extraction_cohort"] == "quality")
        & (catalog["main_game_flag"] == 1)
        & (catalog["popscore_available_flag"] == 1)
        & (catalog["rating_reliable_flag"] == 1)
    )
    catalog["visibility_percentile_eligible_pool"] = pd.NA
    catalog["quality_percentile_eligible_pool"] = pd.NA
    catalog.loc[hidden_gem_eligible_mask, "visibility_percentile_eligible_pool"] = (
        catalog.loc[hidden_gem_eligible_mask]
        .groupby("release_year")["custom_interest_score"]
        .rank(pct=True, method="average")
    )
    catalog.loc[hidden_gem_eligible_mask, "quality_percentile_eligible_pool"] = (
        catalog.loc[hidden_gem_eligible_mask]
        .groupby("release_year")["total_rating"]
        .rank(pct=True, method="average")
    )
    catalog["inverse_visibility_percentile"] = 1 - pd.to_numeric(
        catalog["visibility_percentile_eligible_pool"], errors="coerce"
    )
    catalog["hidden_gem_conservative_flag"] = (
        hidden_gem_eligible_mask
        & (catalog["total_rating"].fillna(-1) >= 85)
        & (pd.to_numeric(catalog["visibility_percentile_eligible_pool"], errors="coerce") <= 0.25)
    ).astype(int)
    catalog["hidden_gem_broad_flag"] = (
        hidden_gem_eligible_mask
        & (catalog["total_rating"].fillna(-1) >= 75)
        & (pd.to_numeric(catalog["visibility_percentile_eligible_pool"], errors="coerce") <= 0.50)
    ).astype(int)

    hidden_gems = safe_read_csv(config.DIAGNOSTIC_DIR / "hidden_gem_candidates.csv")
    hidden_ids = set(hidden_gems.get("game_id", pd.Series(dtype=int)).astype(int).tolist())
    catalog["hidden_gem_balanced_flag"] = catalog["game_id"].isin(hidden_ids).astype(int)
    catalog["rag_ready_flag"] = (
        (catalog["has_summary"] == 1)
        & (catalog["genres_list"].fillna("") != "")
        & (catalog["platforms_list"].fillna("") != "")
    ).astype(int)

    catalog = catalog.sort_values(["release_year", "name"], na_position="last").reset_index(drop=True)
    return catalog


def build_hidden_gems(catalog: pd.DataFrame) -> pd.DataFrame:
    hidden = safe_read_csv(config.DIAGNOSTIC_DIR / "hidden_gem_candidates.csv")
    if hidden.empty:
        return pd.DataFrame()

    app_fields = [
        "game_id",
        "slug",
        "summary",
        "storyline",
        "cover_url",
        "screenshot_url",
        "genres_list",
        "themes_list",
        "platforms_list",
        "platform_families_list",
        "game_modes_list",
        "player_perspectives_list",
        "rating_band",
        "rag_ready_flag",
    ]
    hidden = hidden.merge(catalog[app_fields], on="game_id", how="left")
    hidden["hidden_gem_version"] = "Balanced"
    hidden["hidden_gem_score"] = (
        (hidden["total_rating"].fillna(0) / 100.0) * 0.65
        + hidden["inverse_visibility_percentile"].fillna(0) * 0.35
    ).round(4)
    hidden["candidate_explanation"] = hidden.apply(
        lambda row: (
            f"{row['name']} qualifies because it is a reliable high-rated quality-cohort game "
            f"({row['total_rating']:.1f}/100 from {row['total_rating_count']:.0f} ratings) "
            f"and its within-year quality-cohort visibility percentile is "
            f"{row['visibility_percentile_eligible_pool']:.0%}, at or below the "
            f"{HIDDEN_GEM_VISIBILITY_PERCENTILE:.0%} balanced cutoff."
        ),
        axis=1,
    )
    return hidden.sort_values(["hidden_gem_score", "total_rating"], ascending=False).reset_index(drop=True)


def unique_options(catalog: pd.DataFrame, column: str) -> list[str]:
    values: set[str] = set()
    if column not in catalog:
        return []
    for value in catalog[column].fillna(""):
        values.update(split_list(value))
    return sorted(values)


def build_filter_options(catalog: pd.DataFrame) -> dict[str, object]:
    return {
        "release_years": sorted(catalog["release_year"].dropna().astype(int).unique().tolist()),
        "genres": unique_options(catalog, "genres_list"),
        "themes": unique_options(catalog, "themes_list"),
        "platforms": unique_options(catalog, "platforms_list"),
        "platform_families": unique_options(catalog, "platform_families_list"),
        "platform_types": unique_options(catalog, "platform_types_list"),
        "game_modes": unique_options(catalog, "game_modes_list"),
        "player_perspectives": unique_options(catalog, "player_perspectives_list"),
        "rating_bands": sorted(catalog["rating_band"].dropna().unique().tolist()),
        "cohorts": sorted(catalog["extraction_cohort"].dropna().unique().tolist()),
    }


def build_methodology_metrics(catalog: pd.DataFrame, hidden_gems: pd.DataFrame) -> dict[str, object]:
    total_games = int(catalog["game_id"].nunique())
    cohort_counts = catalog["extraction_cohort"].value_counts(dropna=False).to_dict()
    return {
        "total_games": total_games,
        "release_year_start": int(catalog["release_year"].min()),
        "release_year_end": int(catalog["release_year"].max()),
        "games_per_year": int(catalog.groupby("release_year")["game_id"].nunique().median()),
        "quality_cohort_count": int(cohort_counts.get("quality", 0)),
        "popularity_cohort_count": int(cohort_counts.get("popularity", 0)),
        "comparison_cohort_count": int(cohort_counts.get("comparison", 0)),
        "rating_coverage": float(catalog["rating_available_flag"].mean()),
        "reliable_rating_coverage": float(catalog["rating_reliable_flag"].mean()),
        "popscore_coverage": float(catalog["popscore_available_flag"].mean()),
        "summary_coverage": float(catalog["has_summary"].mean()),
        "hidden_gem_count": int(hidden_gems["game_id"].nunique()) if not hidden_gems.empty else 0,
        "quality_threshold": QUALITY_THRESHOLD,
        "min_rating_count": MIN_RATING_COUNT,
        "hidden_gem_visibility_percentile": HIDDEN_GEM_VISIBILITY_PERCENTILE,
    }


def first_value(df: pd.DataFrame, column: str, default: object = None) -> object:
    if df.empty or column not in df:
        return default
    return df.iloc[0][column]


def build_insight_summary(catalog: pd.DataFrame, hidden_gems: pd.DataFrame) -> dict[str, object]:
    top_genres = safe_read_csv(config.DESCRIPTIVE_DIR / "top_genres.csv")
    top_platforms = safe_read_csv(config.DESCRIPTIVE_DIR / "top_platforms.csv")
    quality_popscore = safe_read_csv(config.DIAGNOSTIC_DIR / "quality_popscore_correlation.csv")
    user_critic = safe_read_csv(config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv")

    return {
        "dataset": {
            "total_games": int(catalog["game_id"].nunique()),
            "release_years": f"{int(catalog['release_year'].min())}-{int(catalog['release_year'].max())}",
            "sample_note": "Curated analytical sample; not a full-market prevalence estimate.",
        },
        "descriptive": {
            "top_genre": first_value(top_genres, "genre_name", "Unknown"),
            "top_platform": first_value(top_platforms, "platform_name", "Unknown"),
            "rating_coverage_pct": round(float(catalog["rating_available_flag"].mean() * 100), 2),
            "summary_coverage_pct": round(float(catalog["has_summary"].mean() * 100), 2),
        },
        "diagnostic": {
            "hidden_gem_count": int(hidden_gems["game_id"].nunique()) if not hidden_gems.empty else 0,
            "quality_popscore_correlation_file": "quality_popscore_correlation.csv",
            "user_critic_agreement_file": "user_critic_agreement_summary.csv",
            "quality_popscore_rows": len(quality_popscore),
            "user_critic_rows": len(user_critic),
        },
    }


def write_json(data: dict[str, object], path: Path) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main() -> None:
    ensure_directories([config.APP_DATA_DIR, config.RECOMMENDATIONS_DIR])

    if not config.DATABASE_PATH.exists():
        raise FileNotFoundError(f"Missing database: {config.DATABASE_PATH}")

    with sqlite3.connect(config.DATABASE_PATH) as conn:
        catalog = build_catalog(conn)

    hidden_gems = build_hidden_gems(catalog)
    filter_options = build_filter_options(catalog)
    methodology_metrics = build_methodology_metrics(catalog, hidden_gems)
    insight_summary = build_insight_summary(catalog, hidden_gems)

    catalog_issues = validate_catalog(catalog)
    hidden_gem_issues = validate_hidden_gems(hidden_gems) if not hidden_gems.empty else ["No hidden gems produced."]
    if catalog_issues:
        raise ValueError("Catalog validation failed: " + "; ".join(catalog_issues))
    if hidden_gem_issues:
        raise ValueError("Hidden-gem validation failed: " + "; ".join(hidden_gem_issues))

    catalog_path = save_table(catalog, config.APP_CATALOG_PATH, config.APP_CATALOG_CSV_PATH)
    hidden_path = save_table(hidden_gems, config.APP_HIDDEN_GEMS_PATH, config.APP_HIDDEN_GEMS_CSV_PATH)
    write_json(filter_options, config.APP_FILTER_OPTIONS_PATH)
    write_json(methodology_metrics, config.APP_METHODOLOGY_METRICS_PATH)
    write_json(insight_summary, config.APP_INSIGHT_SUMMARY_PATH)

    print("App data build complete.")
    print(f"Catalog rows: {len(catalog):,} -> {catalog_path}")
    print(f"Hidden gems: {len(hidden_gems):,} -> {hidden_path}")
    print(f"Filter option groups: {len(filter_options):,}")


if __name__ == "__main__":
    main()
