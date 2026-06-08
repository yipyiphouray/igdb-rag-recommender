import json
import os
import time
from typing import Any, Dict, Iterable, List, Sequence, Set

import requests
from dotenv import load_dotenv

from config import RAW_DATA_DIR


# -----------------------------
# Configuration
# -----------------------------

IGDB_BASE_URL = "https://api.igdb.com/v4"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"

# IGDB allows a maximum limit of 500 and documents 4 requests per second.
IGDB_MAX_LIMIT = 500
RELATED_GAME_CHUNK_SIZE = 100
REQUEST_SLEEP_SECONDS = 0.30
REQUEST_TIMEOUT_SECONDS = 30

DEFAULT_GAME_LIMIT = 500


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

BASE_GAME_QUERY = f"""
    fields {GAME_FIELDS};
    where total_rating_count > 50
        & summary != null;
    sort total_rating_count desc;
"""


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
    The base_query must contain fields/where/sort clauses, but no limit/offset.
    """
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

        print(f"Fetched {len(page)} {endpoint} records at offset {offset}")

        if len(page) < page_size:
            break

        offset += page_size

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
) -> List[Dict[str, Any]]:
    """
    Fetch records by primary key IDs in safe chunks.
    """
    clean_ids = sorted({int(item) for item in ids if item is not None})
    if not clean_ids:
        print(f"No IDs found for {endpoint}; saving empty file.")
        return []

    records: List[Dict[str, Any]] = []

    for chunk in chunked(clean_ids, IGDB_MAX_LIMIT):
        id_list = ",".join(str(item) for item in chunk)
        query = f"""
            fields {fields};
            where id = ({id_list});
            limit {IGDB_MAX_LIMIT};
        """

        page = query_endpoint(endpoint=endpoint, query=query, headers=headers)
        records.extend(page)
        print(f"Fetched {len(page)} of {len(chunk)} requested {endpoint} records")

    return dedupe_records(records)


def fetch_by_game_ids(
    endpoint: str,
    fields: str,
    game_ids: Iterable[int],
    game_field: str,
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    Fetch records for selected game IDs when a related endpoint is keyed by game/game_id.
    Uses pagination inside each chunk because one game can have many related rows.
    """
    records: List[Dict[str, Any]] = []
    clean_game_ids = sorted({int(item) for item in game_ids if item is not None})

    # Smaller game chunks avoid IGDB's practical offset ceiling on
    # high-cardinality endpoints such as external_games.
    for chunk in chunked(clean_game_ids, RELATED_GAME_CHUNK_SIZE):
        id_list = ",".join(str(item) for item in chunk)
        base_query = f"""
            fields {fields};
            where {game_field} = ({id_list});
            sort id asc;
        """
        records.extend(
            fetch_paginated(endpoint=endpoint, base_query=base_query, headers=headers)
        )

    return dedupe_records(records)


# -----------------------------
# Data helpers
# -----------------------------

def save_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save raw endpoint data as JSON.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / filename

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} records to {output_path}")


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


def get_game_limit() -> int:
    """
    Read the requested game count from IGDB_GAME_LIMIT, defaulting to 500.
    """
    raw_value = os.getenv("IGDB_GAME_LIMIT")
    if raw_value is None:
        return DEFAULT_GAME_LIMIT

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError("IGDB_GAME_LIMIT must be an integer.") from exc

    if value <= 0:
        raise ValueError("IGDB_GAME_LIMIT must be greater than zero.")

    return value


# -----------------------------
# Extraction pipeline
# -----------------------------

def fetch_selected_endpoints() -> None:
    """
    Fetch IGDB data for the project MVP.

    The extraction is intentionally game-first:
    1. Fetch the selected games.
    2. Collect relationship IDs from those games.
    3. Fetch only the lookup/detail records connected to those games.
    """
    load_dotenv()
    access_token = get_access_token()
    headers = get_headers(access_token)
    game_limit = get_game_limit()

    print(f"\nFetching games: target={game_limit}")
    games = fetch_paginated(
        endpoint="games",
        base_query=BASE_GAME_QUERY,
        headers=headers,
        max_records=game_limit,
    )
    save_json(games, "games.json")

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

    for endpoint, fields in LOOKUP_ENDPOINTS.items():
        print(f"\nFetching lookup endpoint: {endpoint}")
        data = fetch_by_ids(
            endpoint=endpoint,
            fields=fields,
            ids=lookup_ids[endpoint],
            headers=headers,
        )
        save_json(data, f"{endpoint}.json")

    detail_ids = {
        "covers": collect_ids(games, "cover"),
        "screenshots": collect_ids(games, "screenshots"),
        "multiplayer_modes": collect_ids(games, "multiplayer_modes"),
        "release_dates": collect_ids(games, "release_dates"),
        "websites": collect_ids(games, "websites"),
    }

    for endpoint, fields in DETAIL_ENDPOINTS.items():
        print(f"\nFetching detail endpoint: {endpoint}")
        data = fetch_by_ids(
            endpoint=endpoint,
            fields=fields,
            ids=detail_ids[endpoint],
            headers=headers,
        )
        save_json(data, f"{endpoint}.json")

    # Fetch by game instead of the IDs embedded in games. IGDB game records can
    # retain stale external-product IDs that are no longer queryable.
    print("\nFetching detail endpoint: external_games")
    external_games = fetch_by_game_ids(
        endpoint="external_games",
        fields=EXTERNAL_GAME_FIELDS,
        game_ids=game_ids,
        game_field="game",
        headers=headers,
    )
    save_json(external_games, "external_games.json")

    print("\nFetching relationship endpoint: involved_companies")
    involved_companies = fetch_by_ids(
        endpoint="involved_companies",
        fields=INVOLVED_COMPANY_FIELDS,
        ids=collect_ids(games, "involved_companies"),
        headers=headers,
    )
    save_json(involved_companies, "involved_companies.json")

    print("\nFetching entity endpoint: companies")
    companies = fetch_by_ids(
        endpoint="companies",
        fields=COMPANY_FIELDS,
        ids=collect_ids(involved_companies, "company"),
        headers=headers,
    )
    save_json(companies, "companies.json")

    print("\nFetching enrichment endpoint: game_time_to_beats")
    time_to_beats = fetch_by_game_ids(
        endpoint="game_time_to_beats",
        fields=GAME_TIME_TO_BEAT_FIELDS,
        game_ids=game_ids,
        game_field="game_id",
        headers=headers,
    )
    save_json(time_to_beats, "game_time_to_beats.json")

    print("\nFetching enrichment endpoint: popularity_primitives")
    popularity_primitives = fetch_by_game_ids(
        endpoint="popularity_primitives",
        fields=(
            "id, game_id, external_popularity_source, popularity_type, "
            "value, calculated_at, updated_at"
        ),
        game_ids=game_ids,
        game_field="game_id",
        headers=headers,
    )
    save_json(popularity_primitives, "popularity_primitives.json")

    for endpoint, fields in OPTIONAL_FULL_ENDPOINTS.items():
        print(f"\nFetching small lookup endpoint: {endpoint}")
        data = fetch_all(endpoint=endpoint, fields=fields, headers=headers)
        save_json(data, f"{endpoint}.json")

    print("\nIGDB fetch complete.")


if __name__ == "__main__":
    fetch_selected_endpoints()
