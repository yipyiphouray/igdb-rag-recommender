# IGDB Relational Database Data Dictionary

This data dictionary follows the standard from https://datamanagement.hms.harvard.edu/collect-analyze/documentation-metadata/data-dictionary

## Purpose

This data dictionary documents the structure, content, variable definitions, allowed values, units, and transformation notes for the IGDB relational SQLite database used in the **IGDB Game Discovery & RAG Recommendation System**.

Database file:

```text
data/database/igdb_games.db
```

The database is centered on the `games` table and supports descriptive analytics, diagnostic analytics, predictive modeling, prescriptive recommendation logic, and RAG-based game discovery.

---

## Data Dictionary Standard

Each table uses the following fields:

| Field                   | Meaning                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| Table                   | Name of the database table.                                                                   |
| Variable Name           | Exact column name in the database.                                                            |
| Human-Readable Name     | Plain-English name for the variable.                                                          |
| Data Type               | SQLite data type: `INTEGER`, `TEXT`, or `REAL`.                                               |
| Unit                    | Measurement unit, if applicable. Use `N/A` when there is no measurement unit.                 |
| Allowed Values / Range  | Valid values, expected range, or referenced lookup table.                                     |
| Definition              | Meaning of the variable.                                                                      |
| Source / Transformation | Whether the variable is direct from IGDB, renamed, derived, or created through normalization. |
| Notes                   | Additional context for analytics, data quality, or interpretation.                            |

---

## Value Type Guidance

| Value Type    | Meaning                                                               |
| ------------- | --------------------------------------------------------------------- |
| Primary Key   | Unique identifier for a row.                                          |
| Foreign Key   | Identifier that links to another table.                               |
| Lookup Value  | Human-readable category stored in a lookup table.                     |
| Attribute     | Descriptive field such as name, slug, URL, or text.                   |
| Measure       | Numeric value used directly in analysis.                              |
| Count         | Numeric count of ratings, observations, or records.                   |
| Timestamp     | Unix timestamp or derived date field.                                 |
| Boolean       | `1 = yes/true`, `0 = no/false`.                                       |
| Derived Field | Created during transformation from another field.                     |
| Bridge Field  | Created during normalization to represent many-to-many relationships. |

---

# 1. Core Catalog Tables

## Table: `games`

One row represents one video game.

| Table | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range | Definition | Source / Transformation | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `games` | `game_id` | Game ID | INTEGER | N/A | Unique positive integer | Unique identifier for a game. | Renamed from IGDB `games.id`. | Primary key. |
| `games` | `name` | Game Name | TEXT | N/A | Non-empty text | Official game title. | Direct IGDB field. | Required by the loader. |
| `games` | `slug` | Game Slug | TEXT | N/A | URL-safe text; nullable | URL-friendly version of the game name. | Direct IGDB field. | Useful for matching and links. |
| `games` | `summary` | Game Summary | TEXT | N/A | Free text; nullable | Game description. | Direct IGDB field. | Required by the current extraction filter. |
| `games` | `storyline` | Game Storyline | TEXT | N/A | Free text; nullable | Narrative description. | Direct IGDB field. | Optional RAG context. |
| `games` | `first_release_date` | First Release Timestamp | INTEGER | Unix seconds | Valid Unix timestamp; nullable | First known game-level release date. | Direct IGDB field. | Use the ISO field for display. |
| `games` | `first_release_date_iso` | First Release Date | TEXT | Date | `YYYY-MM-DD`; nullable | Readable UTC date derived from `first_release_date`. | Derived field. | |
| `games` | `release_year` | Release Year | INTEGER | Year | Reasonable year; nullable | Year derived from the first release date. | Derived field. | Used for trends and modeling. |
| `games` | `rating` | IGDB User Rating | REAL | Score out of 100 | 0-100; nullable | Average IGDB user rating. | Direct IGDB field. | Interpret with `rating_count`. |
| `games` | `rating_count` | IGDB User Rating Count | INTEGER | Count | Integer >= 0; nullable | Number of IGDB user ratings. | Direct IGDB field. | |
| `games` | `aggregated_rating` | Critic Rating | REAL | Score out of 100 | 0-100; nullable | Average external critic rating. | Direct IGDB field. | Interpret with `aggregated_rating_count`. |
| `games` | `aggregated_rating_count` | Critic Rating Count | INTEGER | Count | Integer >= 0; nullable | Number of external critic scores. | Direct IGDB field. | |
| `games` | `total_rating` | Total Rating | REAL | Score out of 100 | 0-100; nullable | Combined user and external critic rating. | Direct IGDB field. | Default project quality score. |
| `games` | `total_rating_count` | Total Rating Count | INTEGER | Count | Integer >= 0; nullable | Number of scores behind `total_rating`. | Direct IGDB field. | |
| `games` | `game_type_id` | Game Type ID | INTEGER | N/A | FK to `game_types`; nullable | Type of game record. | Direct IGDB reference. | |
| `games` | `game_status_id` | Game Status ID | INTEGER | N/A | FK to `game_statuses`; nullable | Explicit game availability/status value. | Direct IGDB reference. | Current loaded values are `Offline` and `Delisted`; null does not prove release status. |
| `games` | `parent_game_id` | Parent Game ID | INTEGER | N/A | IGDB game ID; nullable | Main game or bundle for a dependent record. | Renamed from IGDB `parent_game`. | Not an enforced FK because the parent may be outside the sample. |
| `games` | `version_parent_id` | Version Parent Game ID | INTEGER | N/A | IGDB game ID; nullable | Main game for a version or edition. | Renamed from IGDB `version_parent`. | Not an enforced FK. |
| `games` | `cover_id` | Selected Cover ID | INTEGER | N/A | IGDB cover ID; nullable | Cover selected on the game record. | Renamed from IGDB `cover`. | All current values resolve, but no SQLite FK is declared. |
| `games` | `updated_at` | IGDB Updated Timestamp | INTEGER | Unix seconds | Valid timestamp; nullable | Last source update time. | Direct IGDB field. | Audit field. |
| `games` | `updated_at_iso` | IGDB Updated Datetime | TEXT | UTC datetime | ISO 8601 text; nullable | Readable UTC value derived from `updated_at`. | Derived field. | Audit field. |

---

## Table: `game_types`

One row represents one game type/category.

| Table        | Variable Name  | Human-Readable Name | Data Type | Unit | Allowed Values / Range  | Definition                         | Source / Transformation            | Notes                                                                                |
| ------------ | -------------- | ------------------- | --------- | ---- | ----------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| `game_types` | `game_type_id` | Game Type ID        | INTEGER   | N/A  | Unique non-negative integer | Unique identifier for a game type. | From IGDB `game_types.id`.         | Primary key; `0` is Main Game.                                                        |
| `game_types` | `type_name`    | Game Type Name      | TEXT      | N/A  | Controlled vocabulary   | Human-readable game type.          | Renamed from IGDB game type field. | Examples may include main game, DLC, expansion, bundle, remake, remaster, port, etc. |

---

## Table: `game_statuses`

One row represents one explicit game availability/status value.

| Table           | Variable Name    | Human-Readable Name | Data Type | Unit | Allowed Values / Range  | Definition                           | Source / Transformation              | Notes                                                                               |
| --------------- | ---------------- | ------------------- | --------- | ---- | ----------------------- | ------------------------------------ | ------------------------------------ | ----------------------------------------------------------------------------------- |
| `game_statuses` | `game_status_id` | Game Status ID      | INTEGER   | N/A  | Unique positive integer | Unique identifier for a game status. | From IGDB `game_statuses.id`.        | Primary key.                                                                        |
| `game_statuses` | `status_name`    | Game Status Name    | TEXT      | N/A  | Controlled vocabulary   | Human-readable explicit game status. | Renamed from IGDB game status field. | Current extract contains `Offline` and `Delisted`; release lifecycle values are in `release_date_statuses`. |

---

## Table: `genres`

One row represents one game genre.

| Table    | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range      | Definition                              | Source / Transformation        | Notes                                        |
| -------- | ------------- | ------------------- | --------- | ---- | --------------------------- | --------------------------------------- | ------------------------------ | -------------------------------------------- |
| `genres` | `genre_id`    | Genre ID            | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a genre.          | Renamed from IGDB `genres.id`. | Primary key.                                 |
| `genres` | `name`        | Genre Name          | TEXT      | N/A  | Controlled vocabulary       | Broad gameplay category.                | Direct IGDB field.             | Examples: RPG, Shooter, Adventure, Strategy. |
| `genres` | `slug`        | Genre Slug          | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the genre name. | Direct IGDB field.             | Useful for filtering and display.            |

---

## Table: `themes`

One row represents one game theme.

| Table    | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range      | Definition                                   | Source / Transformation        | Notes                                                    |
| -------- | ------------- | ------------------- | --------- | ---- | --------------------------- | -------------------------------------------- | ------------------------------ | -------------------------------------------------------- |
| `themes` | `theme_id`    | Theme ID            | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a theme.               | Renamed from IGDB `themes.id`. | Primary key.                                             |
| `themes` | `name`        | Theme Name          | TEXT      | N/A  | Controlled vocabulary       | High-level theme, mood, setting, or subject. | Direct IGDB field.             | Examples: Fantasy, Sci-Fi, Horror, Survival.             |
| `themes` | `slug`        | Theme Slug          | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the theme name.      | Direct IGDB field.             | Useful for filtering, display, and recommendation logic. |

---

## Table: `keywords`

One row represents one descriptive keyword or tag.

| Table      | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range      | Definition                                | Source / Transformation          | Notes                                 |
| ---------- | ------------- | ------------------- | --------- | ---- | --------------------------- | ----------------------------------------- | -------------------------------- | ------------------------------------- |
| `keywords` | `keyword_id`  | Keyword ID          | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a keyword.          | Renamed from IGDB `keywords.id`. | Primary key.                          |
| `keywords` | `name`        | Keyword Name        | TEXT      | N/A  | Controlled vocabulary       | Fine-grained game tag or concept.         | Direct IGDB field.               | Useful for semantic matching and RAG. |
| `keywords` | `slug`        | Keyword Slug        | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the keyword name. | Direct IGDB field.               | Useful for filtering and display.     |

---

## Table: `game_modes`

One row represents one gameplay mode.

| Table        | Variable Name  | Human-Readable Name | Data Type | Unit | Allowed Values / Range      | Definition                                  | Source / Transformation            | Notes                                                    |
| ------------ | -------------- | ------------------- | --------- | ---- | --------------------------- | ------------------------------------------- | ---------------------------------- | -------------------------------------------------------- |
| `game_modes` | `game_mode_id` | Game Mode ID        | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a gameplay mode.      | Renamed from IGDB `game_modes.id`. | Primary key.                                             |
| `game_modes` | `name`         | Game Mode Name      | TEXT      | N/A  | Controlled vocabulary       | Gameplay mode.                              | Direct IGDB field.                 | Examples: Single player, Multiplayer, Co-operative, MMO. |
| `game_modes` | `slug`         | Game Mode Slug      | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the game mode name. | Direct IGDB field.                 | Useful for filtering and display.                        |

---

## Table: `player_perspectives`

One row represents one player/camera perspective.

| Table                 | Variable Name           | Human-Readable Name     | Data Type | Unit | Allowed Values / Range      | Definition                                     | Source / Transformation                     | Notes                                                       |
| --------------------- | ----------------------- | ----------------------- | --------- | ---- | --------------------------- | ---------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| `player_perspectives` | `player_perspective_id` | Player Perspective ID   | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a player perspective.    | Renamed from IGDB `player_perspectives.id`. | Primary key.                                                |
| `player_perspectives` | `name`                  | Player Perspective Name | TEXT      | N/A  | Controlled vocabulary       | Camera/viewpoint perspective used by the game. | Direct IGDB field.                          | Examples: First person, Third person, Side view, Bird view. |
| `player_perspectives` | `slug`                  | Player Perspective Slug | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the perspective name.  | Direct IGDB field.                          | Useful for filtering and display.                           |

---

# 2. Core Bridge Tables

## Table: `game_genres`

One row represents one game-genre relationship.

| Table         | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range          | Definition              | Source / Transformation                                      | Notes                                  |
| ------------- | ------------- | ------------------- | --------- | ---- | ------------------------------- | ----------------------- | ------------------------------------------------------------ | -------------------------------------- |
| `game_genres` | `game_id`     | Game ID             | INTEGER   | N/A  | Must exist in `games.game_id`   | Game linked to a genre. | Created from IGDB `games.genres` array during normalization. | Composite primary key with `genre_id`. |
| `game_genres` | `genre_id`    | Genre ID            | INTEGER   | N/A  | Must exist in `genres.genre_id` | Genre linked to a game. | Created from IGDB `games.genres` array during normalization. | Composite primary key with `game_id`.  |

---

## Table: `game_themes`

One row represents one game-theme relationship.

| Table         | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range          | Definition              | Source / Transformation                                      | Notes                                  |
| ------------- | ------------- | ------------------- | --------- | ---- | ------------------------------- | ----------------------- | ------------------------------------------------------------ | -------------------------------------- |
| `game_themes` | `game_id`     | Game ID             | INTEGER   | N/A  | Must exist in `games.game_id`   | Game linked to a theme. | Created from IGDB `games.themes` array during normalization. | Composite primary key with `theme_id`. |
| `game_themes` | `theme_id`    | Theme ID            | INTEGER   | N/A  | Must exist in `themes.theme_id` | Theme linked to a game. | Created from IGDB `games.themes` array during normalization. | Composite primary key with `game_id`.  |

---

## Table: `game_keywords`

One row represents one game-keyword relationship.

| Table           | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range              | Definition                | Source / Transformation                                        | Notes                                    |
| --------------- | ------------- | ------------------- | --------- | ---- | ----------------------------------- | ------------------------- | -------------------------------------------------------------- | ---------------------------------------- |
| `game_keywords` | `game_id`     | Game ID             | INTEGER   | N/A  | Must exist in `games.game_id`       | Game linked to a keyword. | Created from IGDB `games.keywords` array during normalization. | Composite primary key with `keyword_id`. |
| `game_keywords` | `keyword_id`  | Keyword ID          | INTEGER   | N/A  | Must exist in `keywords.keyword_id` | Keyword linked to a game. | Created from IGDB `games.keywords` array during normalization. | Composite primary key with `game_id`.    |

---

## Table: `game_modes_bridge`

One row represents one game-game mode relationship.

| Table               | Variable Name  | Human-Readable Name | Data Type | Unit | Allowed Values / Range                  | Definition                      | Source / Transformation                                          | Notes                                      |
| ------------------- | -------------- | ------------------- | --------- | ---- | --------------------------------------- | ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------ |
| `game_modes_bridge` | `game_id`      | Game ID             | INTEGER   | N/A  | Must exist in `games.game_id`           | Game linked to a gameplay mode. | Created from IGDB `games.game_modes` array during normalization. | Composite primary key with `game_mode_id`. |
| `game_modes_bridge` | `game_mode_id` | Game Mode ID        | INTEGER   | N/A  | Must exist in `game_modes.game_mode_id` | Gameplay mode linked to a game. | Created from IGDB `games.game_modes` array during normalization. | Composite primary key with `game_id`.      |

---

## Table: `game_player_perspectives`

One row represents one game-player perspective relationship.

| Table                      | Variable Name           | Human-Readable Name   | Data Type | Unit | Allowed Values / Range                                    | Definition                           | Source / Transformation                                                   | Notes                                               |
| -------------------------- | ----------------------- | --------------------- | --------- | ---- | --------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------- |
| `game_player_perspectives` | `game_id`               | Game ID               | INTEGER   | N/A  | Must exist in `games.game_id`                             | Game linked to a player perspective. | Created from IGDB `games.player_perspectives` array during normalization. | Composite primary key with `player_perspective_id`. |
| `game_player_perspectives` | `player_perspective_id` | Player Perspective ID | INTEGER   | N/A  | Must exist in `player_perspectives.player_perspective_id` | Player perspective linked to a game. | Created from IGDB `games.player_perspectives` array during normalization. | Composite primary key with `game_id`.               |

---

## Table: `game_platforms`

One row represents one game-platform relationship.

| Table            | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range                | Definition                 | Source / Transformation                                         | Notes                                     |
| ---------------- | ------------- | ------------------- | --------- | ---- | ------------------------------------- | -------------------------- | --------------------------------------------------------------- | ----------------------------------------- |
| `game_platforms` | `game_id`     | Game ID             | INTEGER   | N/A  | Must exist in `games.game_id`         | Game linked to a platform. | Created from IGDB `games.platforms` array during normalization. | Composite primary key with `platform_id`. |
| `game_platforms` | `platform_id` | Platform ID         | INTEGER   | N/A  | Must exist in `platforms.platform_id` | Platform linked to a game. | Created from IGDB `games.platforms` array during normalization. | Composite primary key with `game_id`.     |

---

# 3. Platform Tables

## Table: `platforms`

One row represents one game platform.

| Table       | Variable Name        | Human-Readable Name   | Data Type | Unit              | Allowed Values / Range                                         | Definition                                  | Source / Transformation                          | Notes                                                          |
| ----------- | -------------------- | --------------------- | --------- | ----------------- | -------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------- |
| `platforms` | `platform_id`        | Platform ID           | INTEGER   | N/A               | Unique positive integer                                        | Unique identifier for a platform.           | Renamed from IGDB `platforms.id`.                | Primary key.                                                   |
| `platforms` | `name`               | Platform Name         | TEXT      | N/A               | Controlled vocabulary                                          | Platform name.                              | Direct IGDB field.                               | Examples: PC, PlayStation 5, Nintendo Switch, Xbox Series X/S. |
| `platforms` | `abbreviation`       | Platform Abbreviation | TEXT      | N/A               | Short text; nullable                                           | Short platform label.                       | Direct IGDB field.                               | Examples: PC, PS5, XONE, Switch.                               |
| `platforms` | `slug`               | Platform Slug         | TEXT      | N/A               | URL-safe text; nullable                                        | URL-friendly platform name.                 | Direct IGDB field.                               | Useful for stable filtering and links.                         |
| `platforms` | `generation`         | Platform Generation   | INTEGER   | Generation number | Positive integer; nullable                                     | Console/platform generation when available. | Direct IGDB field.                               | Often null for PC, mobile, or non-console platforms.           |
| `platforms` | `platform_family_id` | Platform Family ID    | INTEGER   | N/A               | Must exist in `platform_families.platform_family_id`; nullable | Identifies the broader platform family.     | Foreign key from IGDB platform family reference. | Join to `platform_families` for readable meaning.              |
| `platforms` | `platform_type_id`   | Platform Type ID      | INTEGER   | N/A               | Must exist in `platform_types.platform_type_id`; nullable      | Identifies the type/category of platform.   | Foreign key from IGDB platform type reference.   | Join to `platform_types` for readable meaning.                 |

---

## Table: `platform_families`

One row represents one platform family.

| Table               | Variable Name        | Human-Readable Name  | Data Type | Unit | Allowed Values / Range      | Definition                                        | Source / Transformation                   | Notes                                  |
| ------------------- | -------------------- | -------------------- | --------- | ---- | --------------------------- | ------------------------------------------------- | ----------------------------------------- | -------------------------------------- |
| `platform_families` | `platform_family_id` | Platform Family ID   | INTEGER   | N/A  | Unique positive integer     | Unique identifier for a platform family.          | Renamed from IGDB `platform_families.id`. | Primary key.                           |
| `platform_families` | `name`               | Platform Family Name | TEXT      | N/A  | Controlled vocabulary       | Broader platform family name.                     | Direct IGDB field.                        | Examples: PlayStation, Xbox, Nintendo. |
| `platform_families` | `slug`               | Platform Family Slug | TEXT      | N/A  | URL-friendly text; nullable | URL-friendly version of the platform family name. | Direct IGDB field.                        | Useful for filtering/display.          |

---

## Table: `platform_types`

One row represents one platform type.

| Table            | Variable Name      | Human-Readable Name | Data Type | Unit | Allowed Values / Range  | Definition                             | Source / Transformation                | Notes                                                                                    |
| ---------------- | ------------------ | ------------------- | --------- | ---- | ----------------------- | -------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| `platform_types` | `platform_type_id` | Platform Type ID    | INTEGER   | N/A  | Unique positive integer | Unique identifier for a platform type. | Renamed from IGDB `platform_types.id`. | Primary key.                                                                             |
| `platform_types` | `name`             | Platform Type Name  | TEXT      | N/A  | Controlled vocabulary   | Human-readable platform type.          | Direct or renamed IGDB field.          | Examples may include console, arcade, operating system, portable console, computer, etc. |

---

# 4. Company Tables

## Table: `companies`

One row represents one game company.

| Table | Variable Name | Human-Readable Name | Data Type | Unit | Allowed Values / Range | Definition | Source / Transformation | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `companies` | `company_id` | Company ID | INTEGER | N/A | Unique positive integer | Unique identifier for a company. | Renamed from IGDB `companies.id`. | Primary key. |
| `companies` | `name` | Company Name | TEXT | N/A | Non-empty text | Company name. | Direct IGDB field. | |
| `companies` | `slug` | Company Slug | TEXT | N/A | URL-safe text; nullable | URL-friendly company name. | Direct IGDB field. | |
| `companies` | `country` | Company Country Code | INTEGER | ISO 3166-1 numeric code | Integer; nullable | Country associated with the company. | Direct IGDB field. | Requires an external ISO country mapping for labels. |
| `companies` | `description` | Company Description | TEXT | N/A | Free text; nullable | Description of the company. | Direct IGDB field. | |
| `companies` | `start_date` | Company Start Timestamp | INTEGER | Unix seconds | Integer timestamp; nullable | Company founding date from IGDB. | Direct IGDB field. | One current source value is outside the supported ISO conversion range. |
| `companies` | `start_date_iso` | Company Start Date | TEXT | Date | `YYYY-MM-DD`; nullable | Readable date derived from `start_date`. | Derived field. | Null when the source timestamp cannot be represented. |
| `companies` | `start_date_format_id` | Start Date Format ID | INTEGER | N/A | FK to `date_formats`; nullable | Precision/format of the founding date. | Renamed from IGDB `start_date_format`. | Enforced FK. |
| `companies` | `status_id` | Company Status ID | INTEGER | N/A | IGDB company status code; nullable | Source company status reference. | Renamed from IGDB `status`. | No company-status lookup table or FK is implemented yet. |
| `companies` | `parent_company_id` | Parent Company ID | INTEGER | N/A | IGDB company ID; nullable | Company with a controlling interest. | Renamed from IGDB `parent`. | Not an enforced FK; some parents are outside the extracted company set. |
| `companies` | `url` | IGDB Company URL | TEXT | N/A | URL; nullable | IGDB URL for the company. | Direct IGDB field. | |
| `companies` | `updated_at` | IGDB Updated Timestamp | INTEGER | Unix seconds | Valid timestamp; nullable | Last source update time. | Direct IGDB field. | Audit field. |
| `companies` | `updated_at_iso` | IGDB Updated Datetime | TEXT | UTC datetime | ISO 8601 text; nullable | Readable UTC value derived from `updated_at`. | Derived field. | Audit field. |

---

## Table: `involved_companies`

One row represents one relationship between a game and a company.

| Table                | Variable Name         | Human-Readable Name | Data Type | Unit    | Allowed Values / Range               | Definition                                                | Source / Transformation                        | Notes                            |
| -------------------- | --------------------- | ------------------- | --------- | ------- | ------------------------------------ | --------------------------------------------------------- | ---------------------------------------------- | -------------------------------- |
| `involved_companies` | `involved_company_id` | Involved Company ID | INTEGER   | N/A     | Unique positive integer              | Unique identifier for a game-company relationship.        | Renamed from IGDB `involved_companies.id`.     | Primary key.                     |
| `involved_companies` | `game_id`             | Game ID             | INTEGER   | N/A     | Must exist in `games.game_id`        | Game linked to the company.                               | Foreign key from IGDB involved company record. | Identifies the credited game.    |
| `involved_companies` | `company_id`          | Company ID          | INTEGER   | N/A     | Must exist in `companies.company_id` | Company linked to the game.                               | Foreign key from IGDB involved company record. | Identifies the credited company. |
| `involved_companies` | `developer`           | Developer Flag      | INTEGER   | Boolean | `0`, `1`, or null                    | Indicates whether the company developed the game.         | Direct IGDB boolean field.                     | `1 = yes`, `0 = no`.             |
| `involved_companies` | `publisher`           | Publisher Flag      | INTEGER   | Boolean | `0`, `1`, or null                    | Indicates whether the company published the game.         | Direct IGDB boolean field.                     | `1 = yes`, `0 = no`.             |
| `involved_companies` | `porting`             | Porting Flag        | INTEGER   | Boolean | `0`, `1`, or null                    | Indicates whether the company ported the game.            | Direct IGDB boolean field.                     | `1 = yes`, `0 = no`.             |
| `involved_companies` | `supporting`          | Supporting Flag     | INTEGER   | Boolean | `0`, `1`, or null                    | Indicates whether the company supported game development. | Direct IGDB boolean field.                     | `1 = yes`, `0 = no`.             |
| `involved_companies` | `updated_at`          | IGDB Updated Timestamp | INTEGER | Unix seconds | Valid timestamp; nullable          | Last source update time for the relationship.              | Direct IGDB field.                             | Audit field.                       |
| `involved_companies` | `updated_at_iso`      | IGDB Updated Datetime | TEXT | UTC datetime | ISO 8601 text; nullable             | Readable UTC value derived from `updated_at`.               | Derived field.                                 | Audit field.                       |

---

# 5. Release Date Tables

## Table: `release_dates`

One row represents one release date record for a game, often scoped by platform and region.

| Table           | Variable Name            | Human-Readable Name    | Data Type | Unit         | Allowed Values / Range                                                 | Definition                                           | Source / Transformation                                       | Notes                                                  |
| --------------- | ------------------------ | ---------------------- | --------- | ------------ | ---------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------ |
| `release_dates` | `release_date_id`        | Release Date ID        | INTEGER   | N/A          | Unique positive integer                                                | Unique identifier for a release date record.         | Renamed from IGDB `release_dates.id`.                         | Primary key.                                           |
| `release_dates` | `game_id`                | Game ID                | INTEGER   | N/A          | Must exist in `games.game_id`                                          | Game associated with the release date.               | Foreign key from IGDB release date record.                    | Used for game release analysis.                        |
| `release_dates` | `platform_id`            | Platform ID            | INTEGER   | N/A          | Must exist in `platforms.platform_id`; nullable                        | Platform associated with the release date.           | Foreign key from IGDB release date record.                    | Useful for platform-specific release analysis.         |
| `release_dates` | `date_timestamp`         | Release Date Timestamp | INTEGER   | Unix seconds | Valid Unix timestamp; nullable                                         | Release date as a Unix timestamp.                    | Renamed from IGDB `release_dates.date`.                       | Use `date_iso` for readability.                        |
| `release_dates` | `date_iso`               | Release Date           | TEXT      | Date         | `YYYY-MM-DD`; nullable                                                 | Human-readable release date.                         | Derived from `date_timestamp` or extracted release date data. | Useful for reporting and dashboards.                   |
| `release_dates` | `release_year`           | Release Year           | INTEGER   | Year         | Reasonable video game release year; nullable                           | Year of the release date.                            | Derived or renamed from IGDB release date year field.         | Useful for trend analysis.                             |
| `release_dates` | `release_month`          | Release Month          | INTEGER   | Month        | 1–12; nullable                                                         | Month of the release date.                           | Derived or renamed from IGDB release date month field.        | Useful for seasonal release analysis.                  |
| `release_dates` | `release_day`            | Release Day            | INTEGER   | Day of month | 1–31; nullable                                                         | Day of month of the release date.                    | Derived or extracted from date data.                          | Validate against actual calendar dates where possible. |
| `release_dates` | `date_format_id`         | Date Format ID         | INTEGER   | N/A          | Must exist in `date_formats.date_format_id`; nullable                  | Identifies the precision/format of the release date. | Foreign key from IGDB date format reference.                  | Join to `date_formats` for readable meaning.           |
| `release_dates` | `release_date_region_id` | Release Date Region ID | INTEGER   | N/A          | Must exist in `release_date_regions.release_date_region_id`; nullable  | Identifies the release region.                       | Foreign key from IGDB release region reference.               | Join to `release_date_regions` for readable meaning.   |
| `release_dates` | `release_date_status_id` | Release Date Status ID | INTEGER   | N/A          | Must exist in `release_date_statuses.release_date_status_id`; nullable | Identifies release date status.                      | Foreign key from IGDB release date status reference.          | Join to `release_date_statuses` for readable meaning.  |
| `release_dates` | `human`                  | Human Release Date     | TEXT      | N/A          | Free text; nullable                                                    | Human-readable release date text from IGDB.          | Direct IGDB field.                                            | Useful when exact dates are incomplete.                |

---

## Table: `date_formats`

One row represents one release date format or precision category.

| Table          | Variable Name    | Human-Readable Name | Data Type | Unit | Allowed Values / Range  | Definition                                       | Source / Transformation              | Notes                                                                    |
| -------------- | ---------------- | ------------------- | --------- | ---- | ----------------------- | ------------------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------ |
| `date_formats` | `date_format_id` | Date Format ID      | INTEGER   | N/A  | Unique positive integer | Unique identifier for a date format.             | From IGDB date format reference.     | Primary key.                                                             |
| `date_formats` | `format_name`    | Date Format Name    | TEXT      | N/A  | Controlled vocabulary   | Human-readable release date precision or format. | Renamed from IGDB date format field. | Examples may include exact date, year-month, year-only, quarter, or TBD. |

---

## Table: `release_date_regions`

One row represents one release region.

| Table                  | Variable Name            | Human-Readable Name    | Data Type | Unit | Allowed Values / Range  | Definition                              | Source / Transformation                  | Notes                                                              |
| ---------------------- | ------------------------ | ---------------------- | --------- | ---- | ----------------------- | --------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------ |
| `release_date_regions` | `release_date_region_id` | Release Date Region ID | INTEGER   | N/A  | Unique positive integer | Unique identifier for a release region. | From IGDB release date region reference. | Primary key.                                                       |
| `release_date_regions` | `region_name`            | Release Region Name    | TEXT      | N/A  | Controlled vocabulary   | Human-readable release region.          | Renamed from IGDB release region field.  | Examples may include worldwide, North America, Europe, Japan, etc. |

---

## Table: `release_date_statuses`

One row represents one release date status.

| Table                   | Variable Name            | Human-Readable Name      | Data Type | Unit | Allowed Values / Range  | Definition                                   | Source / Transformation                      | Notes                                                        |
| ----------------------- | ------------------------ | ------------------------ | --------- | ---- | ----------------------- | -------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `release_date_statuses` | `release_date_status_id` | Release Date Status ID   | INTEGER   | N/A  | Unique positive integer | Unique identifier for a release date status. | From IGDB release date status reference.     | Primary key.                                                 |
| `release_date_statuses` | `status_name`            | Release Date Status Name | TEXT      | N/A  | Controlled vocabulary   | Human-readable release date status.          | Renamed from IGDB release date status field. | Current values include Alpha, Beta, Early Access, Offline, Cancelled, and Full Release. |
| `release_date_statuses` | `description`            | Release Date Status Description | TEXT | N/A | Free text; nullable | IGDB explanation of the release status. | Direct IGDB field. | |

---

# 6. Media and Website Tables

## Table: `covers`

One row represents one cover image for a game.

| Table    | Variable Name | Human-Readable Name | Data Type | Unit   | Allowed Values / Range              | Definition                                  | Source / Transformation                     | Notes                                                        |
| -------- | ------------- | ------------------- | --------- | ------ | ----------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| `covers` | `cover_id`    | Cover ID            | INTEGER   | N/A    | Unique positive integer             | Unique identifier for a cover image record. | Renamed from IGDB `covers.id`.              | Primary key.                                                 |
| `covers` | `game_id`     | Game ID             | INTEGER   | N/A    | Must exist in `games.game_id`       | Game associated with the cover.             | Foreign key from IGDB cover record.         | One game may have zero or one selected cover in this schema. |
| `covers` | `image_id`    | Image ID            | TEXT      | N/A    | Free text; nullable                 | IGDB image identifier.                      | Direct IGDB field.                          | Used to construct image URLs.                                |
| `covers` | `url`         | Cover URL           | TEXT      | N/A    | Valid URL or URL fragment; nullable | Cover image URL.                            | Direct IGDB field or transformed image URL. | Useful for app cards and game detail pages.                  |
| `covers` | `width`       | Image Width         | INTEGER   | Pixels | Integer ≥ 0; nullable               | Width of the cover image.                   | Direct IGDB field.                          | Numeric measure.                                             |
| `covers` | `height`      | Image Height        | INTEGER   | Pixels | Integer ≥ 0; nullable               | Height of the cover image.                  | Direct IGDB field.                          | Numeric measure.                                             |
| `covers` | `alpha_channel` | Alpha Channel Flag | INTEGER   | Boolean | `0`, `1`, or null                  | Whether the image has an alpha channel.     | Direct IGDB field.                          | `1 = yes`, `0 = no`.                                         |
| `covers` | `animated`    | Animated Flag       | INTEGER   | Boolean | `0`, `1`, or null                  | Whether the image is animated.              | Direct IGDB field.                          | `1 = yes`, `0 = no`.                                         |

---

## Table: `screenshots`

One row represents one screenshot image for a game.

| Table         | Variable Name   | Human-Readable Name | Data Type | Unit   | Allowed Values / Range              | Definition                                 | Source / Transformation                     | Notes                                        |
| ------------- | --------------- | ------------------- | --------- | ------ | ----------------------------------- | ------------------------------------------ | ------------------------------------------- | -------------------------------------------- |
| `screenshots` | `screenshot_id` | Screenshot ID       | INTEGER   | N/A    | Unique positive integer             | Unique identifier for a screenshot record. | Renamed from IGDB `screenshots.id`.         | Primary key.                                 |
| `screenshots` | `game_id`       | Game ID             | INTEGER   | N/A    | Must exist in `games.game_id`       | Game associated with the screenshot.       | Foreign key from IGDB screenshot record.    | A game may have multiple screenshots.        |
| `screenshots` | `image_id`      | Image ID            | TEXT      | N/A    | Free text; nullable                 | IGDB image identifier.                     | Direct IGDB field.                          | Used to construct image URLs.                |
| `screenshots` | `url`           | Screenshot URL      | TEXT      | N/A    | Valid URL or URL fragment; nullable | Screenshot image URL.                      | Direct IGDB field or transformed image URL. | Useful for visual browsing and detail pages. |
| `screenshots` | `width`         | Image Width         | INTEGER   | Pixels | Integer ≥ 0; nullable               | Width of the screenshot image.             | Direct IGDB field.                          | Numeric measure.                             |
| `screenshots` | `height`        | Image Height        | INTEGER   | Pixels | Integer ≥ 0; nullable               | Height of the screenshot image.            | Direct IGDB field.                          | Numeric measure.                             |
| `screenshots` | `alpha_channel` | Alpha Channel Flag  | INTEGER   | Boolean | `0`, `1`, or null                  | Whether the image has an alpha channel.    | Direct IGDB field.                          | `1 = yes`, `0 = no`.                         |
| `screenshots` | `animated`      | Animated Flag       | INTEGER   | Boolean | `0`, `1`, or null                  | Whether the image is animated.             | Direct IGDB field.                          | `1 = yes`, `0 = no`.                         |

---

## Table: `websites`

One row represents one external website link for a game.

| Table      | Variable Name     | Human-Readable Name  | Data Type | Unit    | Allowed Values / Range                                  | Definition                                          | Source / Transformation                       | Notes                                                             |
| ---------- | ----------------- | -------------------- | --------- | ------- | ------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------- |
| `websites` | `website_id`      | Website ID           | INTEGER   | N/A     | Unique positive integer                                 | Unique identifier for a website record.             | Renamed from IGDB `websites.id`.              | Primary key.                                                      |
| `websites` | `game_id`         | Game ID              | INTEGER   | N/A     | Must exist in `games.game_id`                           | Game associated with the website link.              | Foreign key from IGDB website record.         | A game may have multiple websites.                                |
| `websites` | `website_type_id` | Website Type ID      | INTEGER   | N/A     | Must exist in `website_types.website_type_id`; nullable | Identifies the category/type of website.            | Foreign key from IGDB website type reference. | Join to `website_types` for readable meaning.                     |
| `websites` | `trusted`         | Trusted Website Flag | INTEGER   | Boolean | `0`, `1`, or null                                       | Indicates whether the website is marked as trusted. | Direct IGDB boolean field.                    | `1 = trusted`, `0 = not trusted`.                                 |
| `websites` | `url`             | Website URL          | TEXT      | N/A     | Valid URL; nullable                                     | External website URL.                               | Direct IGDB field.                            | Examples: official site, Steam page, wiki, social media, Discord. |

---

## Table: `website_types`

One row represents one website type/category.

| Table           | Variable Name     | Human-Readable Name | Data Type | Unit | Allowed Values / Range  | Definition                            | Source / Transformation               | Notes                                                                                 |
| --------------- | ----------------- | ------------------- | --------- | ---- | ----------------------- | ------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------- |
| `website_types` | `website_type_id` | Website Type ID     | INTEGER   | N/A  | Unique positive integer | Unique identifier for a website type. | From IGDB website type reference.     | Primary key.                                                                          |
| `website_types` | `type_name`       | Website Type Name   | TEXT      | N/A  | Controlled vocabulary   | Human-readable website category.      | Renamed from IGDB website type field. | Examples may include official, Steam, Reddit, YouTube, Discord, GOG, Epic Games, etc. |

---

# 7. External Game Mapping Tables

## Table: `external_games`

One row represents one mapping between an IGDB game and an external source.

| Table            | Variable Name             | Human-Readable Name     | Data Type | Unit | Allowed Values / Range                                                  | Definition                                             | Source / Transformation                              | Notes                                                 |
| ---------------- | ------------------------- | ----------------------- | --------- | ---- | ----------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------- |
| `external_games` | `external_game_id`        | External Game ID        | INTEGER   | N/A  | Unique positive integer                                                 | Unique identifier for an external game mapping record. | Renamed from IGDB `external_games.id`.               | Primary key.                                          |
| `external_games` | `game_id`                 | Game ID                 | INTEGER   | N/A  | Must exist in `games.game_id`                                           | IGDB game associated with the external record.         | Foreign key from IGDB external game record.          | Used for mapping IGDB games to other services.        |
| `external_games` | `name`                    | External Game Name      | TEXT      | N/A  | Free text; nullable                                                     | Name used by the external source.                      | Direct IGDB field.                                   | May differ from the IGDB game name.                   |
| `external_games` | `external_game_source_id` | External Game Source ID | INTEGER   | N/A  | Must exist in `external_game_sources.external_game_source_id`; nullable | Identifies the external source.                        | Foreign key from IGDB external source reference.     | Join to `external_game_sources` for readable meaning. |
| `external_games` | `game_release_format_id`  | Game Release Format ID  | INTEGER   | N/A  | Must exist in `game_release_formats.game_release_format_id`; nullable   | Identifies the release format of the external record.  | Foreign key from IGDB game release format reference. | Join to `game_release_formats` for readable meaning.  |
| `external_games` | `platform_id`             | Platform ID             | INTEGER   | N/A  | Must exist in `platforms.platform_id`; nullable                         | Platform associated with the external record.          | Foreign key from IGDB external game record.          | Useful for external store/platform matching.          |
| `external_games` | `uid`                     | External UID            | TEXT      | N/A  | Free text; nullable                                                     | Identifier used by the external source.                | Direct IGDB field.                                   | Useful for matching IGDB to Steam, GOG, Epic, etc.    |
| `external_games` | `url`                     | External Game URL       | TEXT      | N/A  | Valid URL; nullable                                                     | URL for the game on the external source.               | Direct IGDB field.                                   | Useful for navigation and enrichment.                 |
| `external_games` | `release_year`            | External Release Year   | INTEGER   | Year | Integer year; nullable                                                  | Release year recorded by the external source mapping.  | Renamed from IGDB `year`.                            | Source-specific enrichment.                           |

---

## Table: `external_game_sources`

One row represents one external source.

| Table                   | Variable Name             | Human-Readable Name     | Data Type | Unit | Allowed Values / Range  | Definition                                     | Source / Transformation                   | Notes                                                                     |
| ----------------------- | ------------------------- | ----------------------- | --------- | ---- | ----------------------- | ---------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------- |
| `external_game_sources` | `external_game_source_id` | External Game Source ID | INTEGER   | N/A  | Unique positive integer | Unique identifier for an external game source. | From IGDB external game source reference. | Primary key.                                                              |
| `external_game_sources` | `source_name`             | External Source Name    | TEXT      | N/A  | Controlled vocabulary   | Human-readable external source name.           | Renamed from IGDB external source field.  | Examples may include Steam, GOG, Epic Games, depending on data extracted. |

---

## Table: `game_release_formats`

One row represents one game release format.

| Table                  | Variable Name            | Human-Readable Name      | Data Type | Unit | Allowed Values / Range  | Definition                                   | Source / Transformation                  | Notes                                                          |
| ---------------------- | ------------------------ | ------------------------ | --------- | ---- | ----------------------- | -------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------- |
| `game_release_formats` | `game_release_format_id` | Game Release Format ID   | INTEGER   | N/A  | Unique positive integer | Unique identifier for a game release format. | From IGDB game release format reference. | Primary key.                                                   |
| `game_release_formats` | `format_name`            | Game Release Format Name | TEXT      | N/A  | Controlled vocabulary   | Human-readable release format name.          | Renamed from IGDB release format field.  | Used by `external_games` to describe the external game record. |

---

# 8. Multiplayer and Time-to-Beat Tables

## Table: `multiplayer_modes`

One row represents multiplayer support for a game, often scoped to a platform.

| Table               | Variable Name         | Human-Readable Name | Data Type | Unit    | Allowed Values / Range                          | Definition                                               | Source / Transformation                             | Notes                                     |
| ------------------- | --------------------- | ------------------- | --------- | ------- | ----------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------- |
| `multiplayer_modes` | `multiplayer_mode_id` | Multiplayer Mode ID | INTEGER   | N/A     | Unique positive integer                         | Unique identifier for a multiplayer mode record.         | Renamed from IGDB `multiplayer_modes.id`.           | Primary key.                              |
| `multiplayer_modes` | `game_id`             | Game ID             | INTEGER   | N/A     | Must exist in `games.game_id`                   | Game associated with the multiplayer support record.     | Foreign key from IGDB multiplayer mode record.      | Used for multiplayer filtering.           |
| `multiplayer_modes` | `platform_id`         | Platform ID         | INTEGER   | N/A     | Must exist in `platforms.platform_id`; nullable | Platform where the multiplayer support applies.          | Foreign key from IGDB multiplayer mode record.      | Multiplayer support may vary by platform. |
| `multiplayer_modes` | `campaign_coop`       | Campaign Co-op Flag | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether campaign co-op is supported.           | Direct IGDB boolean field, renamed for readability. | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `drop_in`             | Drop-in Flag        | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether drop-in multiplayer is supported.      | Renamed from IGDB `dropin`.                         | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `lan_coop`            | LAN Co-op Flag      | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether LAN co-op is supported.                | Renamed from IGDB `lancoop`.                        | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `offline_coop`        | Offline Co-op Flag  | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether offline/local co-op is supported.      | Direct IGDB boolean field, renamed for readability. | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `offline_coop_max`    | Offline Co-op Maximum | INTEGER | Players | Integer >= 0; nullable                          | Maximum offline co-op players.                           | Renamed from IGDB `offlinecoopmax`.                 | |
| `multiplayer_modes` | `offline_max`         | Offline Maximum     | INTEGER   | Players | Integer >= 0; nullable                          | Maximum offline multiplayer players.                     | Renamed from IGDB `offlinemax`.                     | |
| `multiplayer_modes` | `online_coop`         | Online Co-op Flag   | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether online co-op is supported.             | Direct IGDB boolean field, renamed for readability. | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `online_coop_max`     | Online Co-op Maximum | INTEGER  | Players | Integer >= 0; nullable                          | Maximum online co-op players.                            | Renamed from IGDB `onlinecoopmax`.                  | |
| `multiplayer_modes` | `online_max`          | Online Maximum      | INTEGER   | Players | Integer >= 0; nullable                          | Maximum online multiplayer players.                      | Renamed from IGDB `onlinemax`.                     | |
| `multiplayer_modes` | `split_screen`        | Split-Screen Flag   | INTEGER   | Boolean | `0`, `1`, or null                               | Indicates whether split-screen multiplayer is supported. | Direct IGDB boolean field, renamed for readability. | `1 = yes`, `0 = no`.                      |
| `multiplayer_modes` | `split_screen_online` | Online Split-Screen Flag | INTEGER | Boolean | `0`, `1`, or null                          | Indicates whether online split-screen is supported.      | Renamed from IGDB `splitscreenonline`.              | All current values are null because the field was not returned for this sample. |

---

## Table: `game_time_to_beats`

One row represents time-to-beat estimates for a game.

| Table                | Variable Name          | Human-Readable Name     | Data Type | Unit    | Allowed Values / Range        | Definition                                                   | Source / Transformation                    | Notes                                                             |
| -------------------- | ---------------------- | ----------------------- | --------- | ------- | ----------------------------- | ------------------------------------------------------------ | ------------------------------------------ | ----------------------------------------------------------------- |
| `game_time_to_beats` | `game_time_to_beat_id` | Game Time-to-Beat ID    | INTEGER   | N/A     | Unique positive integer       | Unique identifier for a time-to-beat record.                 | Renamed from IGDB `game_time_to_beats.id`. | Primary key.                                                      |
| `game_time_to_beats` | `game_id`              | Game ID                 | INTEGER   | N/A     | Must exist in `games.game_id` | Game associated with the time-to-beat estimates.             | Foreign key from IGDB time-to-beat record. | One game may have zero or one time-to-beat record in this schema. |
| `game_time_to_beats` | `hastily`              | Hastily Completion Time | INTEGER   | Seconds | Integer ≥ 0; nullable         | Estimated average time to finish the game quickly.           | Direct IGDB field.                         | Useful for “short game” recommendations.                          |
| `game_time_to_beats` | `normally`             | Normal Completion Time  | INTEGER   | Seconds | Integer ≥ 0; nullable         | Estimated average time to finish the game at a normal pace.  | Direct IGDB field.                         | Useful for playtime-based recommendations.                        |
| `game_time_to_beats` | `completely`           | Completionist Time      | INTEGER   | Seconds | Integer ≥ 0; nullable         | Estimated average time to complete most or all game content. | Direct IGDB field.                         | Useful for identifying long or completion-heavy games.            |
| `game_time_to_beats` | `count`                | Time-to-Beat Count      | INTEGER   | Count   | Integer ≥ 0; nullable         | Number of observations behind the time-to-beat estimates.    | Direct IGDB field.                         | Higher count means more reliable estimate.                        |
| `game_time_to_beats` | `updated_at`           | IGDB Updated Timestamp  | INTEGER   | Unix seconds | Valid timestamp; nullable  | Last source update time.                                      | Direct IGDB field.                         | Audit field.                                                       |
| `game_time_to_beats` | `updated_at_iso`       | IGDB Updated Datetime   | TEXT      | UTC datetime | ISO 8601 text; nullable    | Readable UTC value derived from `updated_at`.                  | Derived field.                             | Audit field.                                                       |

---

# 9. Popularity Tables

## Table: `popularity_primitives`

One row represents one popularity signal value for a game.

| Table                   | Variable Name                   | Human-Readable Name             | Data Type | Unit            | Allowed Values / Range                                                    | Definition                                          | Source / Transformation                                   | Notes                                                         |
| ----------------------- | ------------------------------- | ------------------------------- | --------- | --------------- | ------------------------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `popularity_primitives` | `popularity_primitive_id`       | Popularity Primitive ID         | INTEGER   | N/A             | Unique positive integer                                                   | Unique identifier for a popularity signal record.   | Renamed from IGDB `popularity_primitives.id`.             | Primary key.                                                  |
| `popularity_primitives` | `game_id`                       | Game ID                         | INTEGER   | N/A             | Must exist in `games.game_id`                                             | Game being measured.                                | Foreign key from IGDB popularity primitive record.        | Used for popularity and hidden-gem analysis.                  |
| `popularity_primitives` | `external_popularity_source_id` | External Popularity Source ID   | INTEGER   | N/A             | Should exist in `external_game_sources.external_game_source_id`; nullable | Source associated with the popularity signal.       | Foreign key / source reference from IGDB popularity data. | Uses `external_game_sources` as source lookup in this schema. |
| `popularity_primitives` | `popularity_type_id`            | Popularity Type ID              | INTEGER   | N/A             | Must exist in `popularity_types.popularity_type_id`; nullable             | Type of popularity signal.                          | Foreign key from IGDB popularity type reference.          | Join to `popularity_types` for readable meaning.              |
| `popularity_primitives` | `value`                         | Popularity Value                | REAL      | Signal-specific | Numeric value; nullable                                                   | Numeric value of the popularity signal.             | Direct IGDB field.                                        | Meaning depends on `popularity_type_id`.                      |
| `popularity_primitives` | `calculated_at`                 | Popularity Calculated Timestamp | INTEGER   | Unix seconds    | Valid Unix timestamp; nullable                                            | Timestamp when the popularity value was calculated. | Direct IGDB field.                                        | Convert for reporting if needed.                              |
| `popularity_primitives` | `calculated_at_iso`             | Popularity Calculated Datetime  | TEXT      | UTC datetime    | ISO 8601 text; nullable                                                   | Readable UTC value derived from `calculated_at`.     | Derived field.                                            | Snapshot audit field.                                        |
| `popularity_primitives` | `updated_at`                    | IGDB Updated Timestamp          | INTEGER   | Unix seconds    | Valid Unix timestamp; nullable                                            | Last source update time.                             | Direct IGDB field.                                        | Audit field.                                                 |
| `popularity_primitives` | `updated_at_iso`                | IGDB Updated Datetime           | TEXT      | UTC datetime    | ISO 8601 text; nullable                                                   | Readable UTC value derived from `updated_at`.        | Derived field.                                            | Audit field.                                                 |

---

## Table: `popularity_types`

One row defines one popularity signal type.

| Table              | Variable Name                   | Human-Readable Name           | Data Type | Unit | Allowed Values / Range                                                    | Definition                                         | Source / Transformation                                        | Notes                                                    |
| ------------------ | ------------------------------- | ----------------------------- | --------- | ---- | ------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| `popularity_types` | `popularity_type_id`            | Popularity Type ID            | INTEGER   | N/A  | Unique positive integer                                                   | Unique identifier for a popularity signal type.    | Renamed from IGDB `popularity_types.id`.                       | Primary key.                                             |
| `popularity_types` | `external_popularity_source_id` | External Popularity Source ID | INTEGER   | N/A  | Should exist in `external_game_sources.external_game_source_id`; nullable | Source associated with the popularity type.        | Foreign key / source reference from IGDB popularity type data. | Useful for grouping popularity signals by source.        |
| `popularity_types` | `name`                          | Popularity Type Name          | TEXT      | N/A  | Controlled vocabulary                                                     | Human-readable name of the popularity signal type. | Direct IGDB field.                                             | Explains how to interpret `popularity_primitives.value`. |

---

# 10. Recommended Data Quality Rules

## Primary Key Rules

| Rule                     | Description                                                                                          |
| ------------------------ | ---------------------------------------------------------------------------------------------------- |
| Non-null primary keys    | Every primary key should be non-null.                                                                |
| Unique primary keys      | Primary keys must be unique within each table.                                                       |
| Composite key uniqueness | Bridge tables should not contain duplicate composite keys, such as duplicate `game_id` + `genre_id`. |

## Foreign Key Rules

| Rule                      | Description                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------- |
| Valid game references     | Every `game_id` in child tables should exist in `games.game_id`.                   |
| Valid platform references | Every `platform_id` in child tables should exist in `platforms.platform_id`.       |
| Valid company references  | Every `company_id` in `involved_companies` should exist in `companies.company_id`. |
| Valid lookup references   | Lookup foreign keys should exist in their corresponding lookup tables.             |
| No orphan records         | Bridge/detail records should not point to missing parent records.                  |

## Boolean Rules

| Column Examples                                                | Valid Values      |
| -------------------------------------------------------------- | ----------------- |
| `developer`, `publisher`, `porting`, `supporting`              | `0`, `1`, or null |
| `campaign_coop`, `offline_coop`, `online_coop`, `split_screen` | `0`, `1`, or null |
| `trusted`                                                      | `0`, `1`, or null |

## Numeric Range Rules

| Column                              | Suggested Rule                            |
| ----------------------------------- | ----------------------------------------- |
| `rating`                            | Between 0 and 100 when not null.          |
| `total_rating`                      | Between 0 and 100 when not null.          |
| `rating_count`                      | Greater than or equal to 0 when not null. |
| `total_rating_count`                | Greater than or equal to 0 when not null. |
| `width`, `height`                   | Greater than or equal to 0 when not null. |
| `hastily`, `normally`, `completely` | Greater than or equal to 0 when not null. |
| `count`                             | Greater than or equal to 0 when not null. |
| `release_month`                     | Between 1 and 12 when not null.           |
| `release_day`                       | Between 1 and 31 when not null.           |

## Timestamp Rules

| Column               | Suggested Rule                                                   |
| -------------------- | ---------------------------------------------------------------- |
| `first_release_date` | Should be convertible to `first_release_date_iso` when not null. |
| `start_date`         | Should be convertible to `start_date_iso` when not null.         |
| `date_timestamp`     | Should be convertible to `date_iso` when not null.               |
| `calculated_at`      | Should be convertible to a readable datetime when not null.      |


The data dictionary should be updated whenever the database schema changes, a column is renamed, a transformation rule changes, or a new lookup/value mapping is added.
