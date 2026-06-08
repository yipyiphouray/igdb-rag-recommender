import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from config import DATA_DIR, RAW_DATA_DIR


DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "igdb_games.db"
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def load_json(filename: str) -> List[Dict[str, Any]]:
    path = RAW_DATA_DIR / filename
    if not path.exists():
        print(f"Warning: missing raw file {path}. Loading as empty.")
        return []

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise TypeError(f"Expected a JSON list in {path}")

    return data


def bool_to_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(bool(value))


def unix_to_date(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return (UNIX_EPOCH + timedelta(seconds=int(value))).date().isoformat()
    except (OverflowError, ValueError):
        return None


def unix_to_datetime(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return (UNIX_EPOCH + timedelta(seconds=int(value))).isoformat()
    except (OverflowError, ValueError):
        return None


def year_from_unix(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return (UNIX_EPOCH + timedelta(seconds=int(value))).year
    except (OverflowError, ValueError):
        return None


def image_url(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("//"):
        return f"https:{value}"
    return value


def table_count(conn: sqlite3.Connection, table_name: str) -> int:
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
    return int(cursor.fetchone()[0])


def execute_many(
    conn: sqlite3.Connection,
    sql: str,
    rows: Iterable[Sequence[Any]],
) -> None:
    conn.executemany(sql, list(rows))


def bridge_rows(
    games: Sequence[Dict[str, Any]],
    source_field: str,
) -> Iterable[Tuple[int, int]]:
    for game in games:
        game_id = game.get("id")
        values = game.get(source_field) or []

        if game_id is None:
            continue

        for value in values:
            if value is not None:
                yield int(game_id), int(value)


def recreate_database() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE game_types (
            game_type_id INTEGER PRIMARY KEY,
            type_name TEXT NOT NULL
        );

        CREATE TABLE game_statuses (
            game_status_id INTEGER PRIMARY KEY,
            status_name TEXT NOT NULL
        );

        CREATE TABLE genres (
            genre_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE themes (
            theme_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE keywords (
            keyword_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE game_modes (
            game_mode_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE player_perspectives (
            player_perspective_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE platform_families (
            platform_family_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT
        );

        CREATE TABLE platform_types (
            platform_type_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE platforms (
            platform_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            abbreviation TEXT,
            slug TEXT,
            generation INTEGER,
            platform_family_id INTEGER,
            platform_type_id INTEGER,
            FOREIGN KEY (platform_family_id) REFERENCES platform_families(platform_family_id),
            FOREIGN KEY (platform_type_id) REFERENCES platform_types(platform_type_id)
        );

        CREATE TABLE date_formats (
            date_format_id INTEGER PRIMARY KEY,
            format_name TEXT NOT NULL
        );

        CREATE TABLE release_date_regions (
            release_date_region_id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL
        );

        CREATE TABLE release_date_statuses (
            release_date_status_id INTEGER PRIMARY KEY,
            status_name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE external_game_sources (
            external_game_source_id INTEGER PRIMARY KEY,
            source_name TEXT NOT NULL
        );

        CREATE TABLE game_release_formats (
            game_release_format_id INTEGER PRIMARY KEY,
            format_name TEXT NOT NULL
        );

        CREATE TABLE website_types (
            website_type_id INTEGER PRIMARY KEY,
            type_name TEXT NOT NULL
        );

        CREATE TABLE popularity_types (
            popularity_type_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            external_popularity_source_id INTEGER,
            FOREIGN KEY (external_popularity_source_id)
                REFERENCES external_game_sources(external_game_source_id)
        );

        CREATE TABLE companies (
            company_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT,
            country INTEGER,
            description TEXT,
            start_date INTEGER,
            start_date_iso TEXT,
            start_date_format_id INTEGER,
            status_id INTEGER,
            parent_company_id INTEGER,
            url TEXT,
            updated_at INTEGER,
            updated_at_iso TEXT,
            FOREIGN KEY (start_date_format_id) REFERENCES date_formats(date_format_id)
        );

        CREATE TABLE games (
            game_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT,
            summary TEXT,
            storyline TEXT,
            first_release_date INTEGER,
            first_release_date_iso TEXT,
            release_year INTEGER,
            rating REAL,
            rating_count INTEGER,
            aggregated_rating REAL,
            aggregated_rating_count INTEGER,
            total_rating REAL,
            total_rating_count INTEGER,
            game_type_id INTEGER,
            game_status_id INTEGER,
            parent_game_id INTEGER,
            version_parent_id INTEGER,
            cover_id INTEGER,
            updated_at INTEGER,
            updated_at_iso TEXT,
            FOREIGN KEY (game_type_id) REFERENCES game_types(game_type_id),
            FOREIGN KEY (game_status_id) REFERENCES game_statuses(game_status_id)
        );

        CREATE TABLE game_genres (
            game_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, genre_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
        );

        CREATE TABLE game_themes (
            game_id INTEGER NOT NULL,
            theme_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, theme_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
        );

        CREATE TABLE game_keywords (
            game_id INTEGER NOT NULL,
            keyword_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, keyword_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id)
        );

        CREATE TABLE game_platforms (
            game_id INTEGER NOT NULL,
            platform_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, platform_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
        );

        CREATE TABLE game_modes_bridge (
            game_id INTEGER NOT NULL,
            game_mode_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, game_mode_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (game_mode_id) REFERENCES game_modes(game_mode_id)
        );

        CREATE TABLE game_player_perspectives (
            game_id INTEGER NOT NULL,
            player_perspective_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, player_perspective_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (player_perspective_id)
                REFERENCES player_perspectives(player_perspective_id)
        );

        CREATE TABLE covers (
            cover_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            url TEXT,
            width INTEGER,
            height INTEGER,
            image_id TEXT,
            alpha_channel INTEGER,
            animated INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        );

        CREATE TABLE screenshots (
            screenshot_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            url TEXT,
            width INTEGER,
            height INTEGER,
            image_id TEXT,
            alpha_channel INTEGER,
            animated INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        );

        CREATE TABLE involved_companies (
            involved_company_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            developer INTEGER,
            publisher INTEGER,
            porting INTEGER,
            supporting INTEGER,
            updated_at INTEGER,
            updated_at_iso TEXT,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE release_dates (
            release_date_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            platform_id INTEGER,
            date_timestamp INTEGER,
            date_iso TEXT,
            date_format_id INTEGER,
            release_date_region_id INTEGER,
            release_date_status_id INTEGER,
            human TEXT,
            release_year INTEGER,
            release_month INTEGER,
            release_day INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
            FOREIGN KEY (date_format_id) REFERENCES date_formats(date_format_id),
            FOREIGN KEY (release_date_region_id)
                REFERENCES release_date_regions(release_date_region_id),
            FOREIGN KEY (release_date_status_id)
                REFERENCES release_date_statuses(release_date_status_id)
        );

        CREATE TABLE multiplayer_modes (
            multiplayer_mode_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            platform_id INTEGER,
            campaign_coop INTEGER,
            drop_in INTEGER,
            lan_coop INTEGER,
            offline_coop INTEGER,
            offline_coop_max INTEGER,
            offline_max INTEGER,
            online_coop INTEGER,
            online_coop_max INTEGER,
            online_max INTEGER,
            split_screen INTEGER,
            split_screen_online INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
        );

        CREATE TABLE external_games (
            external_game_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            name TEXT,
            uid TEXT,
            external_game_source_id INTEGER,
            game_release_format_id INTEGER,
            platform_id INTEGER,
            url TEXT,
            release_year INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (external_game_source_id)
                REFERENCES external_game_sources(external_game_source_id),
            FOREIGN KEY (game_release_format_id)
                REFERENCES game_release_formats(game_release_format_id),
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
        );

        CREATE TABLE websites (
            website_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            website_type_id INTEGER,
            trusted INTEGER,
            url TEXT,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (website_type_id) REFERENCES website_types(website_type_id)
        );

        CREATE TABLE game_time_to_beats (
            game_time_to_beat_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL UNIQUE,
            hastily INTEGER,
            normally INTEGER,
            completely INTEGER,
            count INTEGER,
            updated_at INTEGER,
            updated_at_iso TEXT,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        );

        CREATE TABLE popularity_primitives (
            popularity_primitive_id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            external_popularity_source_id INTEGER,
            popularity_type_id INTEGER,
            value REAL,
            calculated_at INTEGER,
            calculated_at_iso TEXT,
            updated_at INTEGER,
            updated_at_iso TEXT,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (external_popularity_source_id)
                REFERENCES external_game_sources(external_game_source_id),
            FOREIGN KEY (popularity_type_id) REFERENCES popularity_types(popularity_type_id)
        );

        CREATE INDEX idx_games_release_year ON games(release_year);
        CREATE INDEX idx_games_total_rating ON games(total_rating);
        CREATE INDEX idx_game_genres_genre_id ON game_genres(genre_id);
        CREATE INDEX idx_game_themes_theme_id ON game_themes(theme_id);
        CREATE INDEX idx_game_keywords_keyword_id ON game_keywords(keyword_id);
        CREATE INDEX idx_game_platforms_platform_id ON game_platforms(platform_id);
        CREATE INDEX idx_involved_companies_game_id ON involved_companies(game_id);
        CREATE INDEX idx_involved_companies_company_id ON involved_companies(company_id);
        CREATE INDEX idx_release_dates_game_id ON release_dates(game_id);
        CREATE INDEX idx_release_dates_platform_id ON release_dates(platform_id);
        CREATE INDEX idx_external_games_game_id ON external_games(game_id);
        CREATE INDEX idx_websites_game_id ON websites(game_id);
        CREATE INDEX idx_popularity_primitives_game_id ON popularity_primitives(game_id);
        """
    )


def insert_lookup_tables(conn: sqlite3.Connection, raw: Dict[str, List[Dict[str, Any]]]) -> None:
    execute_many(
        conn,
        "INSERT INTO game_types VALUES (?, ?)",
        ((row["id"], row.get("type")) for row in raw["game_types"]),
    )
    execute_many(
        conn,
        "INSERT INTO game_statuses VALUES (?, ?)",
        ((row["id"], row.get("status")) for row in raw["game_statuses"]),
    )
    execute_many(
        conn,
        "INSERT INTO genres VALUES (?, ?, ?)",
        ((row["id"], row.get("name"), row.get("slug")) for row in raw["genres"]),
    )
    execute_many(
        conn,
        "INSERT INTO themes VALUES (?, ?, ?)",
        ((row["id"], row.get("name"), row.get("slug")) for row in raw["themes"]),
    )
    execute_many(
        conn,
        "INSERT INTO keywords VALUES (?, ?, ?)",
        ((row["id"], row.get("name"), row.get("slug")) for row in raw["keywords"]),
    )
    execute_many(
        conn,
        "INSERT INTO game_modes VALUES (?, ?, ?)",
        ((row["id"], row.get("name"), row.get("slug")) for row in raw["game_modes"]),
    )
    execute_many(
        conn,
        "INSERT INTO player_perspectives VALUES (?, ?, ?)",
        (
            (row["id"], row.get("name"), row.get("slug"))
            for row in raw["player_perspectives"]
        ),
    )
    execute_many(
        conn,
        "INSERT INTO platform_families VALUES (?, ?, ?)",
        (
            (row["id"], row.get("name"), row.get("slug"))
            for row in raw["platform_families"]
        ),
    )
    execute_many(
        conn,
        "INSERT INTO platform_types VALUES (?, ?)",
        ((row["id"], row.get("name")) for row in raw["platform_types"]),
    )
    execute_many(
        conn,
        """
        INSERT INTO platforms (
            platform_id, name, abbreviation, slug, generation,
            platform_family_id, platform_type_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("name"),
                row.get("abbreviation"),
                row.get("slug"),
                row.get("generation"),
                row.get("platform_family"),
                row.get("platform_type"),
            )
            for row in raw["platforms"]
        ),
    )
    execute_many(
        conn,
        "INSERT INTO date_formats VALUES (?, ?)",
        ((row["id"], row.get("format")) for row in raw["date_formats"]),
    )
    execute_many(
        conn,
        "INSERT INTO release_date_regions VALUES (?, ?)",
        ((row["id"], row.get("region")) for row in raw["release_date_regions"]),
    )
    execute_many(
        conn,
        "INSERT INTO release_date_statuses VALUES (?, ?, ?)",
        (
            (row["id"], row.get("name"), row.get("description"))
            for row in raw["release_date_statuses"]
        ),
    )
    execute_many(
        conn,
        "INSERT INTO external_game_sources VALUES (?, ?)",
        ((row["id"], row.get("name")) for row in raw["external_game_sources"]),
    )
    execute_many(
        conn,
        "INSERT INTO game_release_formats VALUES (?, ?)",
        ((row["id"], row.get("format")) for row in raw["game_release_formats"]),
    )
    execute_many(
        conn,
        "INSERT INTO website_types VALUES (?, ?)",
        ((row["id"], row.get("type")) for row in raw["website_types"]),
    )
    execute_many(
        conn,
        "INSERT INTO popularity_types VALUES (?, ?, ?)",
        (
            (row["id"], row.get("name"), row.get("external_popularity_source"))
            for row in raw["popularity_types"]
        ),
    )


def insert_companies(conn: sqlite3.Connection, companies: Sequence[Dict[str, Any]]) -> None:
    execute_many(
        conn,
        """
        INSERT INTO companies (
            company_id, name, slug, country, description, start_date,
            start_date_iso, start_date_format_id, status_id, parent_company_id,
            url, updated_at, updated_at_iso
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("name"),
                row.get("slug"),
                row.get("country"),
                row.get("description"),
                row.get("start_date"),
                unix_to_date(row.get("start_date")),
                row.get("start_date_format"),
                row.get("status"),
                row.get("parent"),
                row.get("url"),
                row.get("updated_at"),
                unix_to_datetime(row.get("updated_at")),
            )
            for row in companies
        ),
    )


def insert_games(conn: sqlite3.Connection, games: Sequence[Dict[str, Any]]) -> None:
    execute_many(
        conn,
        """
        INSERT INTO games (
            game_id, name, slug, summary, storyline, first_release_date,
            first_release_date_iso, release_year, rating, rating_count,
            aggregated_rating, aggregated_rating_count, total_rating,
            total_rating_count, game_type_id, game_status_id, parent_game_id,
            version_parent_id, cover_id, updated_at, updated_at_iso
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("name"),
                row.get("slug"),
                row.get("summary"),
                row.get("storyline"),
                row.get("first_release_date"),
                unix_to_date(row.get("first_release_date")),
                year_from_unix(row.get("first_release_date")),
                row.get("rating"),
                row.get("rating_count"),
                row.get("aggregated_rating"),
                row.get("aggregated_rating_count"),
                row.get("total_rating"),
                row.get("total_rating_count"),
                row.get("game_type"),
                row.get("game_status"),
                row.get("parent_game"),
                row.get("version_parent"),
                row.get("cover"),
                row.get("updated_at"),
                unix_to_datetime(row.get("updated_at")),
            )
            for row in games
            if row.get("id") is not None and row.get("name")
        ),
    )


def insert_bridge_tables(conn: sqlite3.Connection, games: Sequence[Dict[str, Any]]) -> None:
    bridge_specs = [
        ("game_genres", "genre_id", "genres"),
        ("game_themes", "theme_id", "themes"),
        ("game_keywords", "keyword_id", "keywords"),
        ("game_platforms", "platform_id", "platforms"),
        ("game_modes_bridge", "game_mode_id", "game_modes"),
        ("game_player_perspectives", "player_perspective_id", "player_perspectives"),
    ]

    for table_name, id_column, source_field in bridge_specs:
        execute_many(
            conn,
            f"""
            INSERT OR IGNORE INTO {table_name} (game_id, {id_column})
            VALUES (?, ?)
            """,
            bridge_rows(games, source_field),
        )


def insert_detail_tables(conn: sqlite3.Connection, raw: Dict[str, List[Dict[str, Any]]]) -> None:
    execute_many(
        conn,
        """
        INSERT INTO covers (
            cover_id, game_id, url, width, height, image_id,
            alpha_channel, animated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                image_url(row.get("url")),
                row.get("width"),
                row.get("height"),
                row.get("image_id"),
                bool_to_int(row.get("alpha_channel")),
                bool_to_int(row.get("animated")),
            )
            for row in raw["covers"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO screenshots (
            screenshot_id, game_id, url, width, height, image_id,
            alpha_channel, animated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                image_url(row.get("url")),
                row.get("width"),
                row.get("height"),
                row.get("image_id"),
                bool_to_int(row.get("alpha_channel")),
                bool_to_int(row.get("animated")),
            )
            for row in raw["screenshots"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO involved_companies (
            involved_company_id, game_id, company_id, developer, publisher,
            porting, supporting, updated_at, updated_at_iso
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                row.get("company"),
                bool_to_int(row.get("developer")),
                bool_to_int(row.get("publisher")),
                bool_to_int(row.get("porting")),
                bool_to_int(row.get("supporting")),
                row.get("updated_at"),
                unix_to_datetime(row.get("updated_at")),
            )
            for row in raw["involved_companies"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO release_dates (
            release_date_id, game_id, platform_id, date_timestamp, date_iso,
            date_format_id, release_date_region_id, release_date_status_id,
            human, release_year, release_month, release_day
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                row.get("platform"),
                row.get("date"),
                unix_to_date(row.get("date")),
                row.get("date_format"),
                row.get("release_region"),
                row.get("status"),
                row.get("human"),
                row.get("y"),
                row.get("m"),
                row.get("d"),
            )
            for row in raw["release_dates"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO multiplayer_modes (
            multiplayer_mode_id, game_id, platform_id, campaign_coop, drop_in,
            lan_coop, offline_coop, offline_coop_max, offline_max, online_coop,
            online_coop_max, online_max, split_screen, split_screen_online
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                row.get("platform"),
                bool_to_int(row.get("campaigncoop")),
                bool_to_int(row.get("dropin")),
                bool_to_int(row.get("lancoop")),
                bool_to_int(row.get("offlinecoop")),
                row.get("offlinecoopmax"),
                row.get("offlinemax"),
                bool_to_int(row.get("onlinecoop")),
                row.get("onlinecoopmax"),
                row.get("onlinemax"),
                bool_to_int(row.get("splitscreen")),
                bool_to_int(row.get("splitscreenonline")),
            )
            for row in raw["multiplayer_modes"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO external_games (
            external_game_id, game_id, name, uid, external_game_source_id,
            game_release_format_id, platform_id, url, release_year
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                row.get("name"),
                row.get("uid"),
                row.get("external_game_source"),
                row.get("game_release_format"),
                row.get("platform"),
                row.get("url"),
                row.get("year"),
            )
            for row in raw["external_games"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO websites (website_id, game_id, website_type_id, trusted, url)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game"),
                row.get("type"),
                bool_to_int(row.get("trusted")),
                row.get("url"),
            )
            for row in raw["websites"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO game_time_to_beats (
            game_time_to_beat_id, game_id, hastily, normally, completely,
            count, updated_at, updated_at_iso
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game_id"),
                row.get("hastily"),
                row.get("normally"),
                row.get("completely"),
                row.get("count"),
                row.get("updated_at"),
                unix_to_datetime(row.get("updated_at")),
            )
            for row in raw["game_time_to_beats"]
        ),
    )
    execute_many(
        conn,
        """
        INSERT INTO popularity_primitives (
            popularity_primitive_id, game_id, external_popularity_source_id,
            popularity_type_id, value, calculated_at, calculated_at_iso,
            updated_at, updated_at_iso
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                row["id"],
                row.get("game_id"),
                row.get("external_popularity_source"),
                row.get("popularity_type"),
                row.get("value"),
                row.get("calculated_at"),
                unix_to_datetime(row.get("calculated_at")),
                row.get("updated_at"),
                unix_to_datetime(row.get("updated_at")),
            )
            for row in raw["popularity_primitives"]
        ),
    )


def load_all_raw_files() -> Dict[str, List[Dict[str, Any]]]:
    filenames = [
        "companies.json",
        "covers.json",
        "date_formats.json",
        "external_games.json",
        "external_game_sources.json",
        "games.json",
        "game_modes.json",
        "game_release_formats.json",
        "game_statuses.json",
        "game_time_to_beats.json",
        "game_types.json",
        "genres.json",
        "involved_companies.json",
        "keywords.json",
        "multiplayer_modes.json",
        "platforms.json",
        "platform_families.json",
        "platform_types.json",
        "player_perspectives.json",
        "popularity_primitives.json",
        "popularity_types.json",
        "release_dates.json",
        "release_date_regions.json",
        "release_date_statuses.json",
        "screenshots.json",
        "themes.json",
        "websites.json",
        "website_types.json",
    ]

    return {
        filename.removesuffix(".json"): load_json(filename)
        for filename in filenames
    }


def run_integrity_checks(conn: sqlite3.Connection) -> None:
    foreign_key_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        raise RuntimeError(f"Foreign key check failed: {foreign_key_errors[:10]}")

    missing_names = conn.execute(
        "SELECT COUNT(*) FROM games WHERE name IS NULL OR TRIM(name) = ''"
    ).fetchone()[0]
    if missing_names:
        raise RuntimeError(f"Found {missing_names} games with missing names.")

    duplicate_bridge_checks = [
        ("game_genres", "game_id", "genre_id"),
        ("game_themes", "game_id", "theme_id"),
        ("game_keywords", "game_id", "keyword_id"),
        ("game_platforms", "game_id", "platform_id"),
        ("game_modes_bridge", "game_id", "game_mode_id"),
        ("game_player_perspectives", "game_id", "player_perspective_id"),
    ]

    for table_name, first_col, second_col in duplicate_bridge_checks:
        duplicates = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT {first_col}, {second_col}, COUNT(*) AS n
                FROM {table_name}
                GROUP BY {first_col}, {second_col}
                HAVING n > 1
            )
            """
        ).fetchone()[0]
        if duplicates:
            raise RuntimeError(f"Found duplicate relationship rows in {table_name}.")


def print_table_counts(conn: sqlite3.Connection) -> None:
    tables = [
        "games",
        "genres",
        "themes",
        "keywords",
        "platforms",
        "companies",
        "game_genres",
        "game_themes",
        "game_keywords",
        "game_platforms",
        "game_modes_bridge",
        "game_player_perspectives",
        "covers",
        "screenshots",
        "involved_companies",
        "release_dates",
        "multiplayer_modes",
        "external_games",
        "websites",
        "game_time_to_beats",
        "popularity_primitives",
    ]

    print("\nLoaded table counts:")
    for table_name in tables:
        print(f"  {table_name}: {table_count(conn, table_name)}")


def build_database() -> None:
    raw = load_all_raw_files()
    conn = recreate_database()

    try:
        create_schema(conn)
        insert_lookup_tables(conn, raw)
        insert_companies(conn, raw["companies"])
        insert_games(conn, raw["games"])
        insert_bridge_tables(conn, raw["games"])
        insert_detail_tables(conn, raw)
        conn.commit()

        run_integrity_checks(conn)
        print_table_counts(conn)
        print(f"\nSQLite database created: {DB_PATH}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    build_database()
