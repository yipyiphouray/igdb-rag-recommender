# IGDB Relational Database ERD

This document visualizes the SQLite database created at:

```text
data/database/igdb_games.db
```

The database contains 34 tables. It is split into two diagrams to keep the
relationships readable.

## Core Catalog

```mermaid
erDiagram
    GAMES {
        INTEGER game_id PK
        TEXT name
        TEXT slug
        TEXT summary
        TEXT storyline
        INTEGER first_release_date
        TEXT first_release_date_iso
        INTEGER release_year
        REAL rating
        INTEGER rating_count
        REAL total_rating
        INTEGER total_rating_count
        INTEGER game_type_id FK
        INTEGER game_status_id FK
    }

    GAME_TYPES {
        INTEGER game_type_id PK
        TEXT type_name
    }

    GAME_STATUSES {
        INTEGER game_status_id PK
        TEXT status_name
    }

    GENRES {
        INTEGER genre_id PK
        TEXT name
        TEXT slug
    }

    THEMES {
        INTEGER theme_id PK
        TEXT name
        TEXT slug
    }

    KEYWORDS {
        INTEGER keyword_id PK
        TEXT name
        TEXT slug
    }

    GAME_MODES {
        INTEGER game_mode_id PK
        TEXT name
        TEXT slug
    }

    PLAYER_PERSPECTIVES {
        INTEGER player_perspective_id PK
        TEXT name
        TEXT slug
    }

    GAME_GENRES {
        INTEGER game_id PK,FK
        INTEGER genre_id PK,FK
    }

    GAME_THEMES {
        INTEGER game_id PK,FK
        INTEGER theme_id PK,FK
    }

    GAME_KEYWORDS {
        INTEGER game_id PK,FK
        INTEGER keyword_id PK,FK
    }

    GAME_MODES_BRIDGE {
        INTEGER game_id PK,FK
        INTEGER game_mode_id PK,FK
    }

    GAME_PLAYER_PERSPECTIVES {
        INTEGER game_id PK,FK
        INTEGER player_perspective_id PK,FK
    }

    PLATFORMS {
        INTEGER platform_id PK
        TEXT name
        TEXT abbreviation
        INTEGER generation
        INTEGER platform_family_id FK
        INTEGER platform_type_id FK
    }

    PLATFORM_FAMILIES {
        INTEGER platform_family_id PK
        TEXT name
        TEXT slug
    }

    PLATFORM_TYPES {
        INTEGER platform_type_id PK
        TEXT name
    }

    GAME_PLATFORMS {
        INTEGER game_id PK,FK
        INTEGER platform_id PK,FK
    }

    COMPANIES {
        INTEGER company_id PK
        TEXT name
        TEXT slug
        INTEGER country
        INTEGER start_date
        TEXT start_date_iso
    }

    INVOLVED_COMPANIES {
        INTEGER involved_company_id PK
        INTEGER game_id FK
        INTEGER company_id FK
        INTEGER developer
        INTEGER publisher
        INTEGER porting
        INTEGER supporting
    }

    RELEASE_DATES {
        INTEGER release_date_id PK
        INTEGER game_id FK
        INTEGER platform_id FK
        INTEGER date_timestamp
        TEXT date_iso
        INTEGER release_year
        INTEGER release_month
        INTEGER release_day
    }

    GAME_TYPES ||--o{ GAMES : categorizes
    GAME_STATUSES ||--o{ GAMES : describes

    GAMES ||--o{ GAME_GENRES : has
    GENRES ||--o{ GAME_GENRES : classifies

    GAMES ||--o{ GAME_THEMES : has
    THEMES ||--o{ GAME_THEMES : classifies

    GAMES ||--o{ GAME_KEYWORDS : has
    KEYWORDS ||--o{ GAME_KEYWORDS : tags

    GAMES ||--o{ GAME_MODES_BRIDGE : has
    GAME_MODES ||--o{ GAME_MODES_BRIDGE : describes

    GAMES ||--o{ GAME_PLAYER_PERSPECTIVES : has
    PLAYER_PERSPECTIVES ||--o{ GAME_PLAYER_PERSPECTIVES : describes

    GAMES ||--o{ GAME_PLATFORMS : supports
    PLATFORMS ||--o{ GAME_PLATFORMS : hosts
    PLATFORM_FAMILIES ||--o{ PLATFORMS : groups
    PLATFORM_TYPES ||--o{ PLATFORMS : categorizes

    GAMES ||--o{ INVOLVED_COMPANIES : credits
    COMPANIES ||--o{ INVOLVED_COMPANIES : participates

    GAMES ||--o{ RELEASE_DATES : has
    PLATFORMS ||--o{ RELEASE_DATES : receives
```

## Enrichment And Media

```mermaid
erDiagram
    GAMES {
        INTEGER game_id PK
        TEXT name
    }

    PLATFORMS {
        INTEGER platform_id PK
        TEXT name
    }

    COVERS {
        INTEGER cover_id PK
        INTEGER game_id FK
        TEXT image_id
        TEXT url
        INTEGER width
        INTEGER height
    }

    SCREENSHOTS {
        INTEGER screenshot_id PK
        INTEGER game_id FK
        TEXT image_id
        TEXT url
        INTEGER width
        INTEGER height
    }

    WEBSITES {
        INTEGER website_id PK
        INTEGER game_id FK
        INTEGER website_type_id FK
        INTEGER trusted
        TEXT url
    }

    WEBSITE_TYPES {
        INTEGER website_type_id PK
        TEXT type_name
    }

    EXTERNAL_GAMES {
        INTEGER external_game_id PK
        INTEGER game_id FK
        INTEGER external_game_source_id FK
        INTEGER game_release_format_id FK
        INTEGER platform_id FK
        TEXT uid
        TEXT url
    }

    EXTERNAL_GAME_SOURCES {
        INTEGER external_game_source_id PK
        TEXT source_name
    }

    GAME_RELEASE_FORMATS {
        INTEGER game_release_format_id PK
        TEXT format_name
    }

    MULTIPLAYER_MODES {
        INTEGER multiplayer_mode_id PK
        INTEGER game_id FK
        INTEGER platform_id FK
        INTEGER campaign_coop
        INTEGER offline_coop
        INTEGER online_coop
        INTEGER split_screen
    }

    GAME_TIME_TO_BEATS {
        INTEGER game_time_to_beat_id PK
        INTEGER game_id FK
        INTEGER hastily
        INTEGER normally
        INTEGER completely
        INTEGER count
    }

    POPULARITY_PRIMITIVES {
        INTEGER popularity_primitive_id PK
        INTEGER game_id FK
        INTEGER external_popularity_source_id FK
        INTEGER popularity_type_id FK
        REAL value
        INTEGER calculated_at
    }

    POPULARITY_TYPES {
        INTEGER popularity_type_id PK
        INTEGER external_popularity_source_id FK
        TEXT name
    }

    GAMES ||--o| COVERS : displays
    GAMES ||--o{ SCREENSHOTS : displays

    GAMES ||--o{ WEBSITES : links
    WEBSITE_TYPES ||--o{ WEBSITES : categorizes

    GAMES ||--o{ EXTERNAL_GAMES : maps
    EXTERNAL_GAME_SOURCES ||--o{ EXTERNAL_GAMES : identifies
    GAME_RELEASE_FORMATS ||--o{ EXTERNAL_GAMES : formats
    PLATFORMS ||--o{ EXTERNAL_GAMES : distributes

    GAMES ||--o{ MULTIPLAYER_MODES : supports
    PLATFORMS ||--o{ MULTIPLAYER_MODES : scopes

    GAMES ||--o| GAME_TIME_TO_BEATS : estimates

    GAMES ||--o{ POPULARITY_PRIMITIVES : measures
    POPULARITY_TYPES ||--o{ POPULARITY_PRIMITIVES : defines
    EXTERNAL_GAME_SOURCES ||--o{ POPULARITY_PRIMITIVES : supplies
    EXTERNAL_GAME_SOURCES ||--o{ POPULARITY_TYPES : supplies
```

## Release Date Lookups

```mermaid
erDiagram
    GAMES ||--o{ RELEASE_DATES : has
    PLATFORMS ||--o{ RELEASE_DATES : receives
    DATE_FORMATS ||--o{ RELEASE_DATES : specifies
    RELEASE_DATE_REGIONS ||--o{ RELEASE_DATES : locates
    RELEASE_DATE_STATUSES ||--o{ RELEASE_DATES : describes

    RELEASE_DATES {
        INTEGER release_date_id PK
        INTEGER game_id FK
        INTEGER platform_id FK
        INTEGER date_format_id FK
        INTEGER release_date_region_id FK
        INTEGER release_date_status_id FK
        TEXT date_iso
        TEXT human
    }

    GAMES {
        INTEGER game_id PK
    }

    PLATFORMS {
        INTEGER platform_id PK
    }

    DATE_FORMATS {
        INTEGER date_format_id PK
        TEXT format_name
    }

    RELEASE_DATE_REGIONS {
        INTEGER release_date_region_id PK
        TEXT region_name
    }

    RELEASE_DATE_STATUSES {
        INTEGER release_date_status_id PK
        TEXT status_name
    }
```

## Viewing The Diagrams

In VS Code:

1. Open this file.
2. Press `Ctrl+Shift+V` to open Markdown Preview.
3. If Mermaid is not rendered by your VS Code setup, view the file on GitHub
   or install a Markdown Mermaid preview extension.

The diagrams describe table relationships. The authoritative schema remains
`src/create_IGDB_relational_DB.py` and the generated SQLite database.
