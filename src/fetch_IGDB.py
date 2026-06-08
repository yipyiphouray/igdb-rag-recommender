import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests
from dotenv import load_dotenv

from config import RAW_DATA_DIR


# -----------------------------
# Configuration
# -----------------------------

IGDB_BASE_URL = "https://api.igdb.com/v4"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"

# IGDB docs say 4 requests per second.
# Use 0.30 seconds to stay safely under the limit.
REQUEST_SLEEP_SECONDS = 0.30


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

    response = requests.post(TWITCH_TOKEN_URL, params=params)
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
# Core request function
# -----------------------------

def query_endpoint(
    endpoint: str,
    query: str,
    headers: Dict[str, str],
    max_retries: int = 3,
) -> List[Dict[str, Any]]:
    """
    Query one IGDB endpoint using APICalypse query syntax.
    Includes basic retry handling for 429 rate limit responses.
    """
    url = f"{IGDB_BASE_URL}/{endpoint}"

    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, data=query)

        if response.status_code == 429:
            wait_time = 1.5 * (attempt + 1)
            print(f"Rate limited on {endpoint}. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            continue

        if response.status_code >= 400:
            print(f"Error querying endpoint: {endpoint}")
            print("Status:", response.status_code)
            print("Response:", response.text)
            response.raise_for_status()

        time.sleep(REQUEST_SLEEP_SECONDS)
        return response.json()

    raise RuntimeError(f"Failed after retries: {endpoint}")


def save_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save raw endpoint data as JSON.
    """
    output_path = RAW_DATA_DIR / filename

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} records to {output_path}")


# -----------------------------
# Endpoint configs
# -----------------------------

ENDPOINT_QUERIES = {
    # Main fact-like table
    "games": """
        fields
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
            genres,
            themes,
            keywords,
            platforms,
            game_modes,
            player_perspectives,
            involved_companies,
            cover,
            screenshots,
            external_games;
        where total_rating_count > 50 & summary != null;
        sort total_rating_count desc;
        limit 500;
    """,

    # Reference / dimension tables
    "genres": """
        fields id, name, slug;
        limit 500;
    """,

    "themes": """
        fields id, name, slug;
        limit 500;
    """,

    "keywords": """
        fields id, name, slug;
        limit 500;
    """,

    "platforms": """
        fields id, name, abbreviation, slug, generation, platform_family;
        limit 500;
    """,

    "game_modes": """
        fields id, name, slug;
        limit 500;
    """,

    "player_perspectives": """
        fields id, name, slug;
        limit 500;
    """,

    "companies": """
        fields id, name, slug, country, description, start_date;
        limit 500;
    """,

    # Relationship/detail tables
    "involved_companies": """
        fields id, game, company, developer, publisher, porting, supporting;
        limit 500;
    """,

    "covers": """
        fields id, game, url, width, height, image_id;
        limit 500;
    """,

    "screenshots": """
        fields id, game, url, width, height, image_id;
        limit 500;
    """,

    "external_games": """
        fields id, game, name, uid, category, url;
        limit 500;
    """,

    "release_dates": """
        fields id, game, platform, date, region, human, y, m;
        limit 500;
    """,
}


def fetch_selected_endpoints(endpoint_queries: Dict[str, str]) -> None:
    """
    Fetch configured IGDB endpoints and save each as raw JSON.
    """
    access_token = get_access_token()
    headers = get_headers(access_token)

    for endpoint, query in endpoint_queries.items():
        print(f"\nFetching endpoint: {endpoint}")

        data = query_endpoint(
            endpoint=endpoint,
            query=query,
            headers=headers,
        )

        save_json(data, f"{endpoint}.json")


if __name__ == "__main__":
    fetch_selected_endpoints(ENDPOINT_QUERIES)