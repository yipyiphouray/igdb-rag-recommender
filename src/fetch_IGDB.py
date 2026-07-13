import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Sequence, Set

import requests
from dotenv import load_dotenv

from config import RAW_DATA_DIR


# -----------------------------
# Configuration
# -----------------------------

IGDB_BASE_URL = "https://api.igdb.com/v4"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"

# Final analytical sample: exactly 50,000 released main games across completed years
# when enough eligible candidates exist. The yearly target is distributed as
# evenly as possible across START_YEAR..END_YEAR.
START_YEAR = 2010
END_YEAR = 2024
TARGET_TOTAL_GAMES = 50_000

# Target composition within each year. If a cohort is undersupplied, the
# comparison cohort fills the remaining yearly capacity.
QUALITY_QUOTA = 800
LOWER_RATED_QUOTA = 400
POPULARITY_QUOTA = 600
LOW_VISIBILITY_QUOTA = 400

# "Well received" is an operational reception proxy, not objective quality.
QUALITY_RATING_THRESHOLD = 75.0
LOWER_RATING_THRESHOLD = 60.0
MIN_TOTAL_RATING_COUNT = 25
BAYESIAN_PRIOR_COUNT = 25

# Current IGDB lookup IDs used by the extraction rules.
MAIN_GAME_TYPE_ID = 0
EXCLUDED_GAME_STATUS_IDS = {6, 7}  # Cancelled, Rumored
IGDB_POPULARITY_SOURCE_ID = 121
IGDB_VISITS_TYPE_ID = 1
IGDB_WANT_TO_PLAY_TYPE_ID = 2
IGDB_PLAYING_TYPE_ID = 3

RANDOM_SEED = 649
VALIDATION_TITLES = [
    "Baldur's Gate III",
    "Elden Ring",
    "Hades",
    "Cyberpunk 2077",
    "Stardew Valley",
]

# IGDB allows a maximum of 500 records per request and 4 requests per second.
IGDB_MAX_LIMIT = 500
RELATED_GAME_CHUNK_SIZE = 100
REQUEST_SLEEP_SECONDS = 0.30
REQUEST_TIMEOUT_SECONDS = 30
PROGRESS_REFRESH_SECONDS = 1.0
NON_INTERACTIVE_PROGRESS_REFRESH_SECONDS = 10.0


GAME_FIELDS = """
    id,
    name,
    slug,
    summary,
    storyline,
    first_release_date,
    rating,
    rating_count,
    aggregated_rating,
    aggregated_rating_count,
    total_rating,
    total_rating_count,
    game_type,
    game_status,
    parent_game,
    version_parent,
    genres,
    themes,
    keywords,
    platforms,
    game_modes,
    multiplayer_modes,
    player_perspectives,
    involved_companies,
    cover,
    screenshots,
    external_games,
    release_dates,
    websites,
    updated_at
"""

GAME_CANDIDATE_FIELDS = """
    id,
    name,
    slug,
    first_release_date,
    rating,
    rating_count,
    aggregated_rating,
    aggregated_rating_count,
    total_rating,
    total_rating_count,
    game_type,
    game_status,
    version_parent,
    genres,
    platforms
"""


def year_bounds(year: int) -> tuple[int, int]:
    """Return UTC Unix timestamps for the start of a year and the next year."""
    start = int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp())
    return start, end


def target_games_for_year(year: int) -> int:
    """Return this year's share of the total target sample size."""
    if year < START_YEAR or year > END_YEAR:
        raise ValueError(f"Year {year} is outside configured extraction range.")

    year_count = END_YEAR - START_YEAR + 1
    base_target = TARGET_TOTAL_GAMES // year_count
    extra_years = TARGET_TOTAL_GAMES % year_count
    year_index = year - START_YEAR
    return base_target + (1 if year_index < extra_years else 0)


def build_year_candidate_query(year: int, min_game_id: int = 0) -> str:
    """
    Build a candidate query for released main games in one completed year.

    Richness requirements and status exclusions are also rechecked locally
    before selection.
    """
    start_timestamp, end_timestamp = year_bounds(year)
    id_cursor_filter = f"\n          & id > {min_game_id}" if min_game_id > 0 else ""
    return f"""
        fields {GAME_CANDIDATE_FIELDS};
        where first_release_date >= {start_timestamp}
          & first_release_date < {end_timestamp}
          & game_type = {MAIN_GAME_TYPE_ID}
          & version_parent = null{id_cursor_filter};
        sort id asc;
    """


def fetch_year_candidates(year: int, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Fetch all candidate games for a year using id-cursor pagination.

    The larger 50,000-game extraction can require large yearly candidate pools.
    Cursor pagination avoids relying on high offsets for the candidate pull.
    """
    records: List[Dict[str, Any]] = []
    last_game_id = 0

    while True:
        base_query = build_year_candidate_query(year, min_game_id=last_game_id)
        query = f"""
            {base_query.strip()}
            limit {IGDB_MAX_LIMIT};
        """
        page = query_endpoint(endpoint="games", query=query, headers=headers)
        records.extend(page)

        if len(page) < IGDB_MAX_LIMIT:
            break

        next_last_game_id = max(int(game["id"]) for game in page)
        if next_last_game_id <= last_game_id:
            raise RuntimeError(
                f"Candidate cursor did not advance for {year}; "
                f"last id stayed at {last_game_id}."
            )
        last_game_id = next_last_game_id

    return records


LOOKUP_ENDPOINTS = {
    "genres": "id, name, slug",
    "themes": "id, name, slug",
    "keywords": "id, name, slug",
    "platforms": "id, name, abbreviation, slug, generation, platform_family, platform_type",
    "game_modes": "id, name, slug",
    "player_perspectives": "id, name, slug",
    "game_types": "id, type",
    "game_statuses": "id, status",
}

DETAIL_ENDPOINTS = {
    "covers": "id, game, game_localization, url, width, height, image_id, alpha_channel, animated",
    "screenshots": "id, game, url, width, height, image_id, alpha_channel, animated",
    "multiplayer_modes": (
        "id, game, platform, campaigncoop, dropin, lancoop, offlinecoop, "
        "offlinecoopmax, offlinemax, onlinecoop, onlinecoopmax, onlinemax, "
        "splitscreen, splitscreenonline"
    ),
    "release_dates": (
        "id, game, platform, date, date_format, release_region, "
        "status, human, y, m, d"
    ),
    "websites": "id, game, type, trusted, url",
}

EXTERNAL_GAME_FIELDS = (
    "id, game, name, uid, external_game_source, game_release_format, "
    "platform, url, year"
)

COMPANY_FIELDS = (
    "id, name, slug, country, description, start_date, start_date_format, "
    "status, parent, url, updated_at"
)

INVOLVED_COMPANY_FIELDS = (
    "id, game, company, developer, publisher, porting, supporting, updated_at"
)

GAME_TIME_TO_BEAT_FIELDS = (
    "id, game_id, hastily, normally, completely, count, updated_at"
)

OPTIONAL_FULL_ENDPOINTS = {
    "date_formats": "id, format",
    "external_game_sources": "id, name",
    "game_release_formats": "id, format",
    "platform_families": "id, name, slug",
    "platform_types": "id, name",
    "release_date_regions": "id, region",
    "release_date_statuses": "id, name, description",
    "website_types": "id, type",
    "popularity_types": "id, name, external_popularity_source",
}


# -----------------------------
# Authentication
# -----------------------------

def get_access_token() -> str:
    """
    Get Twitch app access token for IGDB API.
    Requires IGDB_CLIENT_ID and IGDB_CLIENT_SECRET in .env.
    """
    load_dotenv()

    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Missing IGDB_CLIENT_ID or IGDB_CLIENT_SECRET. "
            "Check your .env file."
        )

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(
        TWITCH_TOKEN_URL,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return response.json()["access_token"]


def get_headers(access_token: str) -> Dict[str, str]:
    """
    Build headers required by IGDB.
    """
    client_id = os.getenv("IGDB_CLIENT_ID")

    if not client_id:
        raise ValueError("Missing IGDB_CLIENT_ID. Check your .env file.")

    return {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


# -----------------------------
# Request helpers
# -----------------------------

def format_duration(seconds: float | None) -> str:
    """Format seconds as a compact human-readable duration."""
    if seconds is None or seconds < 0:
        return "--:--"

    total_seconds = int(round(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class ProgressTracker:
    """Render throttled single-line progress with elapsed time and phase ETA."""

    def __init__(self, label: str, total: int) -> None:
        self.label = label
        self.total = max(int(total), 0)
        self.started_at = time.monotonic()
        self.last_rendered_at = 0.0
        self.last_line_length = 0
        self.interactive = sys.stdout.isatty()

    def update(
        self,
        completed: int,
        detail: str = "",
        force: bool = False,
    ) -> None:
        now = time.monotonic()
        elapsed = now - self.started_at
        completed = min(max(int(completed), 0), self.total)
        finished = completed >= self.total
        refresh_seconds = (
            PROGRESS_REFRESH_SECONDS
            if self.interactive
            else NON_INTERACTIVE_PROGRESS_REFRESH_SECONDS
        )

        if (
            not force
            and not finished
            and now - self.last_rendered_at < refresh_seconds
        ):
            return

        progress = completed / self.total if self.total else 1.0
        rate = completed / elapsed if elapsed > 0 and completed > 0 else 0.0
        remaining = self.total - completed
        eta = remaining / rate if rate > 0 else None

        bar_width = 18
        filled = round(bar_width * progress)
        bar = "#" * filled + "-" * (bar_width - filled)
        suffix = f" | {detail}" if detail else ""
        line = (
            f"[{bar}] {progress:6.1%} {self.label} "
            f"{completed}/{self.total} | "
            f"{format_duration(elapsed)} elapsed | "
            f"{format_duration(eta)} left{suffix}"
        )

        if self.interactive:
            padding = " " * max(self.last_line_length - len(line), 0)
            sys.stdout.write(f"\r{line}{padding}")
            if finished:
                sys.stdout.write("\n")
            sys.stdout.flush()
            self.last_line_length = len(line)
        else:
            print(line, flush=True)

        self.last_rendered_at = now


def query_endpoint(
    endpoint: str,
    query: str,
    headers: Dict[str, str],
    max_retries: int = 3,
) -> List[Dict[str, Any]]:
    """
    Query one IGDB endpoint using APICalypse query syntax.
    Includes retry handling for rate limits and transient server errors.
    """
    url = f"{IGDB_BASE_URL}/{endpoint}"

    for attempt in range(max_retries):
        response = requests.post(
            url,
            headers=headers,
            data=query,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 429:
            wait_time = 1.5 * (attempt + 1)
            print(f"Rate limited on {endpoint}. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            continue

        if response.status_code >= 500:
            wait_time = 1.5 * (attempt + 1)
            print(
                f"Server error on {endpoint} ({response.status_code}). "
                f"Waiting {wait_time:.1f}s..."
            )
            time.sleep(wait_time)
            continue

        if response.status_code >= 400:
            print(f"Error querying endpoint: {endpoint}")
            print("Query:", query)
            print("Status:", response.status_code)
            print("Response:", response.text)
            response.raise_for_status()

        time.sleep(REQUEST_SLEEP_SECONDS)
        data = response.json()
        if not isinstance(data, list):
            raise TypeError(f"Expected list response from {endpoint}, got {type(data)}")
        return data

    raise RuntimeError(f"Failed after retries: {endpoint}")


def fetch_paginated(
    endpoint: str,
    base_query: str,
    headers: Dict[str, str],
    max_records: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch pages from an endpoint until the endpoint is exhausted or max_records is met.
    The base_query must contain fields and any optional where/sort clauses,
    but no limit/offset.
    """
    if max_records is not None and max_records <= 0:
        raise ValueError("max_records must be greater than zero or None.")

    records: List[Dict[str, Any]] = []
    offset = 0
    while True:
        remaining = None if max_records is None else max_records - len(records)
        if remaining is not None and remaining <= 0:
            break

        page_size = IGDB_MAX_LIMIT if remaining is None else min(IGDB_MAX_LIMIT, remaining)
        query = f"""
            {base_query.strip()}
            limit {page_size};
            offset {offset};
        """

        page = query_endpoint(endpoint=endpoint, query=query, headers=headers)
        records.extend(page)

        if len(page) < page_size:
            break

        offset += len(page)

    return records


def fetch_all(
    endpoint: str,
    fields: str,
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    Fetch a full small lookup endpoint.
    """
    base_query = f"fields {fields};"
    return fetch_paginated(endpoint=endpoint, base_query=base_query, headers=headers)


def fetch_by_ids(
    endpoint: str,
    fields: str,
    ids: Iterable[int],
    headers: Dict[str, str],
    progress_label: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch records by primary key IDs in safe chunks.
    """
    clean_ids = sorted({int(item) for item in ids if item is not None})
    if not clean_ids:
        print(f"No IDs found for {endpoint}; saving empty file.")
        return []

    records: List[Dict[str, Any]] = []
    chunks = list(chunked(clean_ids, IGDB_MAX_LIMIT))
    tracker = ProgressTracker(
        progress_label or f"{endpoint} ID chunks",
        len(chunks),
    )

    for chunk_number, chunk in enumerate(chunks, start=1):
        id_list = ",".join(str(item) for item in chunk)
        query = f"""
            fields {fields};
            where id = ({id_list});
            limit {IGDB_MAX_LIMIT};
        """

        page = query_endpoint(endpoint=endpoint, query=query, headers=headers)
        records.extend(page)
        tracker.update(
            chunk_number,
            detail=f"rows={len(records)}",
        )

    return dedupe_records(records)


def fetch_by_game_ids(
    endpoint: str,
    fields: str,
    game_ids: Iterable[int],
    game_field: str,
    headers: Dict[str, str],
    progress_label: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch records for selected game IDs when a related endpoint is keyed by game/game_id.
    Uses pagination inside each chunk because one game can have many related rows.
    """
    records: List[Dict[str, Any]] = []
    clean_game_ids = sorted({int(item) for item in game_ids if item is not None})
    game_chunks = list(chunked(clean_game_ids, RELATED_GAME_CHUNK_SIZE))
    tracker = ProgressTracker(
        progress_label or f"{endpoint} game chunks",
        len(game_chunks),
    )

    # Smaller game chunks avoid IGDB's practical offset ceiling on
    # high-cardinality endpoints such as external_games.
    for chunk_number, chunk in enumerate(game_chunks, start=1):
        id_list = ",".join(str(item) for item in chunk)
        base_query = f"""
            fields {fields};
            where {game_field} = ({id_list});
            sort id asc;
        """
        chunk_rows = fetch_paginated(
            endpoint=endpoint,
            base_query=base_query,
            headers=headers,
        )
        records.extend(chunk_rows)
        tracker.update(
            chunk_number,
            detail=f"rows={len(records)}",
        )

    return dedupe_records(records)


# -----------------------------
# Data helpers
# -----------------------------

def save_json(data: Any, filename: str) -> None:
    """
    Save raw endpoint data as JSON.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / filename

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    record_count = len(data) if hasattr(data, "__len__") else 1
    print(f"Saved {record_count} records to {output_path}")


def collect_ids(records: Sequence[Dict[str, Any]], field: str) -> Set[int]:
    """
    Collect integer IDs from a scalar field or an array field.
    """
    ids: Set[int] = set()

    for record in records:
        value = record.get(field)

        if value is None:
            continue

        if isinstance(value, list):
            ids.update(int(item) for item in value if item is not None)
        else:
            ids.add(int(value))

    return ids


def dedupe_records(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate records by IGDB ID while keeping stable order.
    """
    seen: Set[int] = set()
    deduped: List[Dict[str, Any]] = []

    for record in records:
        record_id = record.get("id")

        if record_id is None:
            deduped.append(record)
            continue

        if int(record_id) in seen:
            continue

        seen.add(int(record_id))
        deduped.append(record)

    return deduped


def chunked(items: Sequence[int], chunk_size: int) -> Iterable[Sequence[int]]:
    """
    Yield fixed-size chunks from a sequence.
    """
    for start in range(0, len(items), chunk_size):
        yield items[start : start + chunk_size]


def is_eligible_candidate(game: Dict[str, Any], year: int) -> bool:
    """Apply the final local eligibility rules to a yearly candidate."""
    if not game.get("name"):
        return False
    if game.get("game_type") != MAIN_GAME_TYPE_ID:
        return False
    if game.get("version_parent") is not None:
        return False
    if game.get("game_status") in EXCLUDED_GAME_STATUS_IDS:
        return False
    if not game.get("genres") or not game.get("platforms"):
        return False

    release_timestamp = game.get("first_release_date")
    if release_timestamp is None:
        return False

    release_year = datetime.fromtimestamp(
        int(release_timestamp),
        tz=timezone.utc,
    ).year
    return release_year == year


def latest_popularity_by_game_type(
    popularity_rows: Sequence[Dict[str, Any]],
) -> Dict[int, Dict[int, Dict[str, Any]]]:
    """Keep the latest popularity primitive for each game and type."""
    latest: Dict[int, Dict[int, Dict[str, Any]]] = {}

    for row in popularity_rows:
        game_id = row.get("game_id")
        popularity_type = row.get("popularity_type")
        source_id = row.get("external_popularity_source")

        if (
            game_id is None
            or popularity_type is None
            or source_id != IGDB_POPULARITY_SOURCE_ID
        ):
            continue

        game_id = int(game_id)
        popularity_type = int(popularity_type)
        existing = latest.setdefault(game_id, {}).get(popularity_type)
        row_order = (
            int(row.get("calculated_at") or 0),
            int(row.get("updated_at") or 0),
            int(row.get("id") or 0),
        )
        existing_order = (
            int(existing.get("calculated_at") or 0),
            int(existing.get("updated_at") or 0),
            int(existing.get("id") or 0),
        ) if existing else (-1, -1, -1)

        if row_order > existing_order:
            latest[game_id][popularity_type] = row

    return latest


def popularity_signals_for_games(
    popularity_rows: Sequence[Dict[str, Any]],
) -> Dict[int, Dict[str, float]]:
    """
    Derive comparable IGDB-source visibility signals for cohort selection.

    The interest score follows IGDB's documented example and is only calculated
    when both Want to Play and Playing primitives exist. Visits remain a
    separate fallback signal rather than being averaged into that score.
    """
    latest = latest_popularity_by_game_type(popularity_rows)
    signals: Dict[int, Dict[str, float]] = {}

    for game_id, type_rows in latest.items():
        visits_row = type_rows.get(IGDB_VISITS_TYPE_ID)
        want_row = type_rows.get(IGDB_WANT_TO_PLAY_TYPE_ID)
        playing_row = type_rows.get(IGDB_PLAYING_TYPE_ID)

        game_signals: Dict[str, float] = {}
        if visits_row and visits_row.get("value") is not None:
            game_signals["visits"] = float(visits_row["value"])

        if (
            want_row
            and playing_row
            and want_row.get("value") is not None
            and playing_row.get("value") is not None
        ):
            game_signals["igdb_interest"] = (
                0.60 * float(want_row["value"])
                + 0.40 * float(playing_row["value"])
            )

        if game_signals:
            signals[game_id] = game_signals

    return signals


def adjusted_quality_scores(
    candidates: Sequence[Dict[str, Any]],
) -> Dict[int, float]:
    """Calculate a yearly Bayesian-adjusted total rating for reliable games."""
    reliable = [
        game
        for game in candidates
        if game.get("total_rating") is not None
        and int(game.get("total_rating_count") or 0) >= MIN_TOTAL_RATING_COUNT
    ]
    if not reliable:
        return {}

    yearly_mean = sum(float(game["total_rating"]) for game in reliable) / len(reliable)
    scores: Dict[int, float] = {}

    for game in reliable:
        rating = float(game["total_rating"])
        count = int(game["total_rating_count"])
        scores[int(game["id"])] = (
            (count / (count + BAYESIAN_PRIOR_COUNT)) * rating
            + (BAYESIAN_PRIOR_COUNT / (count + BAYESIAN_PRIOR_COUNT))
            * yearly_mean
        )

    return scores


def select_popularity_cohort(
    candidates: Sequence[Dict[str, Any]],
    popularity_signals: Dict[int, Dict[str, float]],
    quota: int,
    selected_ids: Set[int],
    *,
    reverse: bool,
) -> tuple[List[Dict[str, Any]], Dict[int, str], Dict[int, float]]:
    """Select high- or low-visibility games using IGDB interest, then visits."""
    selected: List[Dict[str, Any]] = []
    basis_by_game: Dict[int, str] = {}
    score_by_game: Dict[int, float] = {}

    if quota <= 0:
        return selected, basis_by_game, score_by_game

    interest_candidates = [
        game
        for game in candidates
        if int(game["id"]) not in selected_ids
        and "igdb_interest" in popularity_signals.get(int(game["id"]), {})
    ]
    interest_candidates.sort(
        key=lambda game: (
            popularity_signals[int(game["id"])]["igdb_interest"],
            -int(game["id"]),
        ),
        reverse=reverse,
    )

    for game in interest_candidates[:quota]:
        game_id = int(game["id"])
        selected.append(game)
        selected_ids.add(game_id)
        basis_by_game[game_id] = "igdb_interest"
        score_by_game[game_id] = popularity_signals[game_id]["igdb_interest"]

    shortfall = quota - len(selected)
    if shortfall <= 0:
        return selected, basis_by_game, score_by_game

    visit_candidates = [
        game
        for game in candidates
        if int(game["id"]) not in selected_ids
        and "visits" in popularity_signals.get(int(game["id"]), {})
    ]
    visit_candidates.sort(
        key=lambda game: (
            popularity_signals[int(game["id"])]["visits"],
            -int(game["id"]),
        ),
        reverse=reverse,
    )

    for game in visit_candidates[:shortfall]:
        game_id = int(game["id"])
        selected.append(game)
        selected_ids.add(game_id)
        basis_by_game[game_id] = "igdb_visits"
        score_by_game[game_id] = popularity_signals[game_id]["visits"]

    return selected, basis_by_game, score_by_game


def select_year_cohorts(
    year: int,
    candidates: Sequence[Dict[str, Any]],
    popularity_signals: Dict[int, Dict[str, float]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Select stratified quality, lower-rated, visibility, and comparison cohorts."""
    yearly_target = target_games_for_year(year)
    eligible = [game for game in candidates if is_eligible_candidate(game, year)]
    quality_scores = adjusted_quality_scores(eligible)

    quality_candidates = [
        game
        for game in eligible
        if game.get("total_rating") is not None
        and float(game["total_rating"]) >= QUALITY_RATING_THRESHOLD
        and int(game.get("total_rating_count") or 0) >= MIN_TOTAL_RATING_COUNT
    ]
    quality_candidates.sort(
        key=lambda game: (
            quality_scores.get(int(game["id"]), float("-inf")),
            int(game.get("total_rating_count") or 0),
            -int(game["id"]),
        ),
        reverse=True,
    )
    quality_selected = quality_candidates[:QUALITY_QUOTA]
    selected_ids = {int(game["id"]) for game in quality_selected}

    lower_rated_candidates = [
        game
        for game in eligible
        if int(game["id"]) not in selected_ids
        and game.get("total_rating") is not None
        and float(game["total_rating"]) <= LOWER_RATING_THRESHOLD
        and int(game.get("total_rating_count") or 0) >= MIN_TOTAL_RATING_COUNT
    ]
    lower_rated_candidates.sort(
        key=lambda game: (
            quality_scores.get(int(game["id"]), float("inf")),
            -int(game.get("total_rating_count") or 0),
            int(game["id"]),
        ),
    )
    lower_rated_selected = lower_rated_candidates[:LOWER_RATED_QUOTA]
    selected_ids.update(int(game["id"]) for game in lower_rated_selected)

    (
        popularity_selected,
        popularity_basis_by_game,
        popularity_scores_by_game,
    ) = select_popularity_cohort(
        eligible,
        popularity_signals,
        POPULARITY_QUOTA,
        selected_ids,
        reverse=True,
    )

    low_visibility_selected, low_visibility_basis, low_visibility_scores = (
        select_popularity_cohort(
            eligible,
            popularity_signals,
            LOW_VISIBILITY_QUOTA,
            selected_ids,
            reverse=False,
        )
    )

    remaining = [game for game in eligible if int(game["id"]) not in selected_ids]
    comparison_target = max(
        yearly_target
        - len(quality_selected)
        - len(lower_rated_selected)
        - len(popularity_selected)
        - len(low_visibility_selected),
        0,
    )

    rng = random.Random(RANDOM_SEED + year)
    comparison_selected = (
        rng.sample(remaining, min(comparison_target, len(remaining)))
        if remaining and comparison_target
        else []
    )

    selected_games = (
        quality_selected
        + lower_rated_selected
        + popularity_selected
        + low_visibility_selected
        + comparison_selected
    )[:yearly_target]

    cohort_rows: List[Dict[str, Any]] = []
    for cohort_name, cohort_games in (
        ("quality", quality_selected),
        ("lower_rated", lower_rated_selected),
        ("popularity", popularity_selected),
        ("low_visibility", low_visibility_selected),
        ("comparison", comparison_selected),
    ):
        for rank, game in enumerate(cohort_games, start=1):
            game_id = int(game["id"])
            popularity_basis = None
            popularity_score = None
            if cohort_name == "popularity":
                popularity_basis = popularity_basis_by_game.get(game_id)
                popularity_score = popularity_scores_by_game.get(game_id)
            elif cohort_name == "low_visibility":
                popularity_basis = low_visibility_basis.get(game_id)
                popularity_score = low_visibility_scores.get(game_id)

            cohort_rows.append(
                {
                    "game_id": game_id,
                    "release_year": year,
                    "cohort": cohort_name,
                    "selection_rank": rank,
                    "adjusted_quality_score": quality_scores.get(game_id),
                    "popularity_basis": popularity_basis,
                    "popularity_score": popularity_score,
                    "random_seed": RANDOM_SEED + year
                    if cohort_name == "comparison"
                    else None,
                }
            )

    summary = {
        "release_year": year,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "target_selected_count": yearly_target,
        "quality_eligible_count": len(quality_candidates),
        "lower_rated_eligible_count": len(lower_rated_candidates),
        "popscore_interest_available_count": sum(
            1
            for game in eligible
            if "igdb_interest" in popularity_signals.get(int(game["id"]), {})
        ),
        "popscore_visits_available_count": sum(
            1
            for game in eligible
            if "visits" in popularity_signals.get(int(game["id"]), {})
        ),
        "quality_selected_count": len(quality_selected),
        "lower_rated_selected_count": len(lower_rated_selected),
        "popularity_selected_count": len(popularity_selected),
        "low_visibility_selected_count": len(low_visibility_selected),
        "comparison_selected_count": len(comparison_selected),
        "total_selected_count": len(selected_games),
    }
    return selected_games, cohort_rows, summary


# -----------------------------
# Extraction pipeline
# -----------------------------

def fetch_selected_endpoints() -> None:
    """
    Fetch the curated IGDB analytical sample and its related records.

    The extraction is intentionally game-first:
    1. Fetch eligible main-game candidates separately for each year.
    2. Fetch candidate PopScore primitives for visibility selection.
    3. Select quality, lower-rated, visibility, and comparison cohorts per year.
    4. Fetch full game records and related data only for selected games.
    """
    load_dotenv()
    access_token = get_access_token()
    headers = get_headers(access_token)
    extraction_timestamp = int(time.time())
    pipeline_started_at = time.monotonic()
    year_count = END_YEAR - START_YEAR + 1

    print(
        "\nFetching yearly main-game candidate pools: "
        f"{START_YEAR}-{END_YEAR}\n"
        f"Target sample size: {TARGET_TOTAL_GAMES:,} games\n"
        "Progress bars report ETA for the current phase; the final line reports "
        "total pipeline time.",
        flush=True,
    )
    candidates_by_year: Dict[int, List[Dict[str, Any]]] = {}
    all_candidates: List[Dict[str, Any]] = []
    year_tracker = ProgressTracker("Yearly candidate pools", year_count)

    for year_number, year in enumerate(
        range(START_YEAR, END_YEAR + 1),
        start=1,
    ):
        print(f"\nFetching candidate games for {year}")
        year_candidates = fetch_year_candidates(year, headers)
        year_candidates = dedupe_records(year_candidates)
        candidates_by_year[year] = year_candidates
        all_candidates.extend(year_candidates)
        year_tracker.update(
            year_number,
            detail=f"{year}: {len(year_candidates)} candidates",
        )

    all_candidates = dedupe_records(all_candidates)
    candidate_ids = collect_ids(all_candidates, "id")

    print("\nFetching candidate PopScore primitives for cohort selection")
    candidate_popularity = fetch_by_game_ids(
        endpoint="popularity_primitives",
        fields=(
            "id, game_id, external_popularity_source, popularity_type, "
            "value, calculated_at, updated_at"
        ),
        game_ids=candidate_ids,
        game_field="game_id",
        headers=headers,
        progress_label="Candidate PopScore chunks",
    )
    popularity_signals = popularity_signals_for_games(candidate_popularity)

    selected_candidate_games: List[Dict[str, Any]] = []
    extraction_cohorts: List[Dict[str, Any]] = []
    yearly_summaries: List[Dict[str, Any]] = []

    for year in range(START_YEAR, END_YEAR + 1):
        selected, cohort_rows, summary = select_year_cohorts(
            year=year,
            candidates=candidates_by_year[year],
            popularity_signals=popularity_signals,
        )
        selected_candidate_games.extend(selected)
        extraction_cohorts.extend(cohort_rows)
        yearly_summaries.append(summary)
        print(
            f"Selected {year}: {summary['total_selected_count']} games "
            f"(target={summary['target_selected_count']}, "
            f"quality={summary['quality_selected_count']}, "
            f"lower_rated={summary['lower_rated_selected_count']}, "
            f"popularity={summary['popularity_selected_count']}, "
            f"low_visibility={summary['low_visibility_selected_count']}, "
            f"comparison={summary['comparison_selected_count']})"
        )

    selected_candidate_games = dedupe_records(selected_candidate_games)
    selected_game_ids = collect_ids(selected_candidate_games, "id")

    print("\nFetching full records for selected games")
    games = fetch_by_ids(
        endpoint="games",
        fields=GAME_FIELDS,
        ids=selected_game_ids,
        headers=headers,
        progress_label="Selected full-game chunks",
    )

    cohort_order = {
        int(row["game_id"]): (
            int(row["release_year"]),
            {
                "quality": 0,
                "lower_rated": 1,
                "popularity": 2,
                "low_visibility": 3,
                "comparison": 4,
            }[row["cohort"]],
            int(row["selection_rank"]),
        )
        for row in extraction_cohorts
    }
    games.sort(key=lambda game: cohort_order[int(game["id"])])
    save_json(games, "games.json")

    selected_titles = {str(game.get("name", "")).casefold() for game in games}
    candidate_titles = {
        str(game.get("name", "")).casefold() for game in all_candidates
    }
    validation_results = {
        title: {
            "present_in_candidate_pool": title.casefold() in candidate_titles,
            "selected": title.casefold() in selected_titles,
        }
        for title in VALIDATION_TITLES
    }

    extraction_manifest = {
        "schema_version": 2,
        "extraction_timestamp": extraction_timestamp,
        "extraction_timestamp_iso": datetime.fromtimestamp(
            extraction_timestamp,
            tz=timezone.utc,
        ).isoformat(),
        "population": {
            "start_year": START_YEAR,
            "end_year": END_YEAR,
            "game_type": "Main Game",
            "required_fields": ["name", "first_release_date", "genres", "platforms"],
            "excluded_game_status_ids": sorted(EXCLUDED_GAME_STATUS_IDS),
            "version_parent_must_be_null": True,
        },
        "yearly_target": {
            "target_total_games": TARGET_TOTAL_GAMES,
            "target_years": year_count,
            "base_games_per_year": TARGET_TOTAL_GAMES // year_count,
            "extra_year_count": TARGET_TOTAL_GAMES % year_count,
            "extra_year_rule": "first configured release years receive one additional game",
            "quality_quota": QUALITY_QUOTA,
            "lower_rated_quota": LOWER_RATED_QUOTA,
            "popularity_quota": POPULARITY_QUOTA,
            "low_visibility_quota": LOW_VISIBILITY_QUOTA,
            "comparison_rule": "fills remaining yearly target after other cohorts",
        },
        "quality_rule": {
            "total_rating_minimum": QUALITY_RATING_THRESHOLD,
            "total_rating_count_minimum": MIN_TOTAL_RATING_COUNT,
            "ranking_method": "Bayesian-adjusted total_rating within release year",
            "bayesian_prior_count": BAYESIAN_PRIOR_COUNT,
        },
        "lower_rated_rule": {
            "total_rating_maximum": LOWER_RATING_THRESHOLD,
            "total_rating_count_minimum": MIN_TOTAL_RATING_COUNT,
            "ranking_method": "lowest Bayesian-adjusted total_rating within release year",
            "interpretation": "lower-rated reliable reception, not objectively bad games",
        },
        "popularity_rule": {
            "primary": "0.60 * IGDB Want to Play + 0.40 * IGDB Playing",
            "fallback": "IGDB Visits",
            "cross_source_values_are_not_averaged": True,
        },
        "low_visibility_rule": {
            "primary": "lowest project-defined IGDB interest score among games with known visibility",
            "fallback": "lowest IGDB Visits among games with known visits",
            "missing_popscore_interpretation": "unknown visibility, not low visibility",
        },
        "comparison_rule": {
            "method": "random sample from remaining eligible games",
            "base_random_seed": RANDOM_SEED,
            "year_seed_formula": "base_random_seed + release_year",
        },
        "candidate_count": len(all_candidates),
        "selected_game_count": len(games),
        "yearly_summaries": yearly_summaries,
        "validation_titles": validation_results,
    }
    save_json(extraction_cohorts, "extraction_cohorts.json")
    save_json(extraction_manifest, "extraction_manifest.json")

    game_ids = collect_ids(games, "id")

    lookup_ids = {
        "genres": collect_ids(games, "genres"),
        "themes": collect_ids(games, "themes"),
        "keywords": collect_ids(games, "keywords"),
        "platforms": collect_ids(games, "platforms"),
        "game_modes": collect_ids(games, "game_modes"),
        "player_perspectives": collect_ids(games, "player_perspectives"),
        "game_types": collect_ids(games, "game_type"),
        "game_statuses": collect_ids(games, "game_status"),
    }

    lookup_tracker = ProgressTracker("Lookup endpoints", len(LOOKUP_ENDPOINTS))
    for endpoint_number, (endpoint, fields) in enumerate(
        LOOKUP_ENDPOINTS.items(),
        start=1,
    ):
        print(f"\nFetching lookup endpoint: {endpoint}")
        data = fetch_by_ids(
            endpoint=endpoint,
            fields=fields,
            ids=lookup_ids[endpoint],
            headers=headers,
            progress_label=f"Lookup {endpoint}",
        )
        save_json(data, f"{endpoint}.json")
        lookup_tracker.update(
            endpoint_number,
            detail=f"completed {endpoint}",
        )

    detail_ids = {
        "covers": collect_ids(games, "cover"),
        "screenshots": collect_ids(games, "screenshots"),
        "multiplayer_modes": collect_ids(games, "multiplayer_modes"),
        "release_dates": collect_ids(games, "release_dates"),
        "websites": collect_ids(games, "websites"),
    }

    detail_tracker = ProgressTracker("Detail endpoints", len(DETAIL_ENDPOINTS))
    for endpoint_number, (endpoint, fields) in enumerate(
        DETAIL_ENDPOINTS.items(),
        start=1,
    ):
        print(f"\nFetching detail endpoint: {endpoint}")
        data = fetch_by_ids(
            endpoint=endpoint,
            fields=fields,
            ids=detail_ids[endpoint],
            headers=headers,
            progress_label=f"Detail {endpoint}",
        )
        save_json(data, f"{endpoint}.json")
        detail_tracker.update(
            endpoint_number,
            detail=f"completed {endpoint}",
        )

    # Fetch by game instead of the IDs embedded in games. IGDB game records can
    # retain stale external-product IDs that are no longer queryable.
    print("\nFetching detail endpoint: external_games")
    external_games = fetch_by_game_ids(
        endpoint="external_games",
        fields=EXTERNAL_GAME_FIELDS,
        game_ids=game_ids,
        game_field="game",
        headers=headers,
        progress_label="External-game chunks",
    )
    save_json(external_games, "external_games.json")

    print("\nFetching relationship endpoint: involved_companies")
    involved_companies = fetch_by_ids(
        endpoint="involved_companies",
        fields=INVOLVED_COMPANY_FIELDS,
        ids=collect_ids(games, "involved_companies"),
        headers=headers,
        progress_label="Involved-company chunks",
    )
    save_json(involved_companies, "involved_companies.json")

    print("\nFetching entity endpoint: companies")
    companies = fetch_by_ids(
        endpoint="companies",
        fields=COMPANY_FIELDS,
        ids=collect_ids(involved_companies, "company"),
        headers=headers,
        progress_label="Company chunks",
    )
    save_json(companies, "companies.json")

    print("\nFetching enrichment endpoint: game_time_to_beats")
    time_to_beats = fetch_by_game_ids(
        endpoint="game_time_to_beats",
        fields=GAME_TIME_TO_BEAT_FIELDS,
        game_ids=game_ids,
        game_field="game_id",
        headers=headers,
        progress_label="Time-to-beat chunks",
    )
    save_json(time_to_beats, "game_time_to_beats.json")

    print("\nSaving selected-game popularity primitives")
    popularity_primitives = [
        row
        for row in candidate_popularity
        if int(row.get("game_id", -1)) in game_ids
    ]
    save_json(popularity_primitives, "popularity_primitives.json")

    optional_tracker = ProgressTracker(
        "Small lookup endpoints",
        len(OPTIONAL_FULL_ENDPOINTS),
    )
    for endpoint_number, (endpoint, fields) in enumerate(
        OPTIONAL_FULL_ENDPOINTS.items(),
        start=1,
    ):
        print(f"\nFetching small lookup endpoint: {endpoint}")
        data = fetch_all(endpoint=endpoint, fields=fields, headers=headers)
        save_json(data, f"{endpoint}.json")
        optional_tracker.update(
            endpoint_number,
            detail=f"completed {endpoint}",
        )

    print(
        "\nIGDB fetch complete. "
        f"Total elapsed time: "
        f"{format_duration(time.monotonic() - pipeline_started_at)}",
        flush=True,
    )


if __name__ == "__main__":
    fetch_selected_endpoints()
