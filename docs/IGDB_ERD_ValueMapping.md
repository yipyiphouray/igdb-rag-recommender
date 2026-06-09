# IGDB Relational Database Value Mappings

## Purpose

This document explains how to interpret coded, numeric, boolean, timestamp, and lookup values in the IGDB relational database.

This file should be used alongside:

```text
docs/IGDB_ERD_Data_Dictionary.md
```

The data dictionary explains what each column is.
This value mapping document explains what coded values mean.

---

# 1. Value Mapping Philosophy

Not every number in the database should be interpreted the same way.

| Numeric Value Type | Example                           | Meaning                         | How to Interpret                                     |
| ------------------ | --------------------------------- | ------------------------------- | ---------------------------------------------------- |
| Primary key        | `game_id = 1942`                  | Unique row identifier           | Do not interpret the number itself.                  |
| Foreign key        | `platform_id = 6`                 | Points to another table         | Join to the related lookup/entity table.             |
| Lookup ID          | `game_type_id = 0`                | Category stored in lookup table | Join to lookup table for readable label.             |
| Boolean            | `trusted = 1`                     | True/false flag                 | Use `1 = yes/true`, `0 = no/false`.                  |
| Timestamp          | `first_release_date = 1704067200` | Unix timestamp                  | Convert to readable date.                            |
| Measure            | `total_rating = 84.7`             | Analytical numeric value        | Interpret using unit/range.                          |
| Count              | `rating_count = 3357`             | Number of observations          | Higher count usually means more support/reliability. |

The cleanest rule is:

> If a number is an ID, join to the related table.
> If a number is a measure, interpret it using its unit.
> If a number is a boolean, interpret `1` as true and `0` as false.
> If a number is a timestamp, convert it to a readable date.

---

# 2. Global Boolean Mapping

SQLite stores booleans as integers in this project.

| Stored Value | Meaning           | Interpretation                                |
| -----------: | ----------------- | --------------------------------------------- |
|          `1` | Yes / True        | The condition applies.                        |
|          `0` | No / False        | The condition does not apply.                 |
|       `NULL` | Unknown / Missing | The value was not available or not extracted. |

Boolean columns in this ERD:

| Table                | Column          | Meaning                                        |
| -------------------- | --------------- | ---------------------------------------------- |
| `involved_companies` | `developer`     | Whether the company developed the game.        |
| `involved_companies` | `publisher`     | Whether the company published the game.        |
| `involved_companies` | `porting`       | Whether the company ported the game.           |
| `involved_companies` | `supporting`    | Whether the company supported development.     |
| `websites`           | `trusted`       | Whether the website is marked as trusted.      |
| `multiplayer_modes`  | `campaign_coop` | Whether campaign co-op is supported.           |
| `multiplayer_modes`  | `drop_in`       | Whether drop-in multiplayer is supported.      |
| `multiplayer_modes`  | `lan_coop`      | Whether LAN co-op is supported.                 |
| `multiplayer_modes`  | `offline_coop`  | Whether offline/local co-op is supported.      |
| `multiplayer_modes`  | `online_coop`   | Whether online co-op is supported.             |
| `multiplayer_modes`  | `split_screen`  | Whether split-screen multiplayer is supported. |
| `multiplayer_modes`  | `split_screen_online` | Whether online split-screen is supported. |
| `covers`              | `alpha_channel` | Whether the cover has an alpha channel.       |
| `covers`              | `animated`      | Whether the cover is animated.                 |
| `screenshots`         | `alpha_channel` | Whether the screenshot has an alpha channel.  |
| `screenshots`         | `animated`      | Whether the screenshot is animated.            |

Example query:

```sql
SELECT
    g.name,
    c.name AS company_name,
    CASE ic.developer
        WHEN 1 THEN 'Developer'
        WHEN 0 THEN 'Not Developer'
        ELSE 'Unknown'
    END AS developer_role
FROM involved_companies ic
JOIN games g
    ON ic.game_id = g.game_id
JOIN companies c
    ON ic.company_id = c.company_id;
```

---

# 3. Core Game Lookup Mappings

## 3.1 `games.game_type_id` → `game_types.game_type_id`

The `game_type_id` column identifies what kind of game record the row represents.

| Table   | Coded Column   | Lookup Table | Lookup Label |
| ------- | -------------- | ------------ | ------------ |
| `games` | `game_type_id` | `game_types` | `type_name`  |

Current loaded mappings:

| ID | Type Name |
| --: | --- |
| 0 | Main Game |
| 2 | Expansion |
| 3 | Bundle |
| 4 | Standalone Expansion |
| 8 | Remake |
| 9 | Remaster |
| 10 | Expanded Game |
| 11 | Port |

Other valid IGDB game types are absent because the lookup extraction loads only
types referenced by the selected 500 games.

Use this query to get the exact values currently loaded in your database:

```sql
SELECT
    game_type_id,
    type_name
FROM game_types
ORDER BY game_type_id;
```

Recommended analytics usage:

| Use Case              | Recommended Rule                                                                                |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| Main catalog analysis | Include main games first.                                                                       |
| DLC/edition filtering | Exclude DLC, expansions, bundles, ports, packs, and updates unless specifically analyzing them. |
| Recommendation MVP    | Prefer main games to avoid recommending DLC or editions as standalone games.                    |

Example query:

```sql
SELECT
    g.game_id,
    g.name,
    gt.type_name
FROM games g
LEFT JOIN game_types gt
    ON g.game_type_id = gt.game_type_id;
```

---

## 3.2 `games.game_status_id` → `game_statuses.game_status_id`

The `game_status_id` column identifies an explicit game availability/status
value.

| Table   | Coded Column     | Lookup Table    | Lookup Label  |
| ------- | ---------------- | --------------- | ------------- |
| `games` | `game_status_id` | `game_statuses` | `status_name` |

Current loaded mappings:

| ID | Status Name | Meaning |
| --: | --- | --- |
| 5 | Offline | Game or service is marked offline. |
| 8 | Delisted | Game is marked as removed from storefront availability. |

In the current database, 489 of 500 games have `game_status_id = NULL`. Do not
interpret null as either released or unreleased. Use release dates to determine
whether a game has already launched. Alpha, Beta, Early Access, Cancelled, and
Full Release values belong to `release_date_statuses`.

Use this query to get the exact values currently loaded in your database:

```sql
SELECT
    game_status_id,
    status_name
FROM game_statuses
ORDER BY game_status_id;
```

Recommended analytics usage:

| Use Case                  | Recommended Rule                                                                                               |
| ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| General catalog dashboard | Keep all statuses, but allow status filtering.                                                                 |
| Rating analysis           | Use release dates when release eligibility matters.                                                           |
| Recommendation engine     | Exclude or down-rank explicit Offline/Delisted records and require a qualifying past release date.             |
| Future release analysis   | Use `release_dates` and `release_date_statuses`.                                                               |

---

# 4. Game Classification Lookup Mappings

## 4.1 `game_genres.genre_id` → `genres.genre_id`

Genres are broad gameplay categories.

| Bridge Table  | Coded Column | Lookup Table | Lookup Label |
| ------------- | ------------ | ------------ | ------------ |
| `game_genres` | `genre_id`   | `genres`     | `name`       |

Use this query to get your genre mapping:

```sql
SELECT
    genre_id,
    name,
    slug
FROM genres
ORDER BY name;
```

Example join:

```sql
SELECT
    g.name AS game_name,
    ge.name AS genre_name
FROM game_genres gg
JOIN games g
    ON gg.game_id = g.game_id
JOIN genres ge
    ON gg.genre_id = ge.genre_id;
```

Recommended usage:

| Use Case              | How to Use                                    |
| --------------------- | --------------------------------------------- |
| Descriptive analytics | Count games by genre.                         |
| Diagnostic analytics  | Compare rating distributions across genres.   |
| Recommendation        | Match user genre preferences.                 |
| RAG profile           | Include genre names in the game profile text. |

---

## 4.2 `game_themes.theme_id` → `themes.theme_id`

Themes describe high-level mood, setting, or subject.

| Bridge Table  | Coded Column | Lookup Table | Lookup Label |
| ------------- | ------------ | ------------ | ------------ |
| `game_themes` | `theme_id`   | `themes`     | `name`       |

Use this query to get your theme mapping:

```sql
SELECT
    theme_id,
    name,
    slug
FROM themes
ORDER BY name;
```

Recommended usage:

| Use Case             | How to Use                                                          |
| -------------------- | ------------------------------------------------------------------- |
| Vibe-based search    | Match prompts like “dark fantasy,” “sci-fi,” “horror,” or “comedy.” |
| Diagnostic analytics | Compare ratings across themes.                                      |
| Recommendation       | Boost games with matching themes.                                   |
| RAG profile          | Include theme names in the embedded text profile.                   |

---

## 4.3 `game_keywords.keyword_id` → `keywords.keyword_id`

Keywords are fine-grained tags or concepts.

| Bridge Table    | Coded Column | Lookup Table | Lookup Label |
| --------------- | ------------ | ------------ | ------------ |
| `game_keywords` | `keyword_id` | `keywords`   | `name`       |

Use this query to get your keyword mapping:

```sql
SELECT
    keyword_id,
    name,
    slug
FROM keywords
ORDER BY name;
```

Recommended usage:

| Use Case                     | How to Use                                                             |
| ---------------------------- | ---------------------------------------------------------------------- |
| Semantic search support      | Include keywords in game profile documents.                            |
| Fine-grained recommendations | Match prompts like “zombies,” “stealth,” “open world,” or “cyberpunk.” |
| Diagnostic analytics         | Identify keyword clusters associated with high ratings.                |

---

## 4.4 `game_modes_bridge.game_mode_id` → `game_modes.game_mode_id`

Game modes describe how the game can be played.

| Bridge Table        | Coded Column   | Lookup Table | Lookup Label |
| ------------------- | -------------- | ------------ | ------------ |
| `game_modes_bridge` | `game_mode_id` | `game_modes` | `name`       |

Use this query to get your game mode mapping:

```sql
SELECT
    game_mode_id,
    name,
    slug
FROM game_modes
ORDER BY name;
```

Recommended usage:

| Use Case       | How to Use                                           |
| -------------- | ---------------------------------------------------- |
| User filtering | Match “single-player,” “multiplayer,” “co-op,” etc.  |
| Dashboard      | Show catalog split by mode.                          |
| Recommendation | Filter or boost games based on preferred play style. |

---

## 4.5 `game_player_perspectives.player_perspective_id` → `player_perspectives.player_perspective_id`

Player perspectives describe the camera or viewpoint.

| Bridge Table               | Coded Column            | Lookup Table          | Lookup Label |
| -------------------------- | ----------------------- | --------------------- | ------------ |
| `game_player_perspectives` | `player_perspective_id` | `player_perspectives` | `name`       |

Use this query to get your player perspective mapping:

```sql
SELECT
    player_perspective_id,
    name,
    slug
FROM player_perspectives
ORDER BY name;
```

Recommended usage:

| Use Case             | How to Use                                              |
| -------------------- | ------------------------------------------------------- |
| User filtering       | Match “first-person,” “third-person,” “side view,” etc. |
| Recommendation       | Boost games with preferred perspective.                 |
| Diagnostic analytics | Compare ratings by perspective.                         |

---

# 5. Platform Lookup Mappings

## 5.1 `game_platforms.platform_id` → `platforms.platform_id`

The `platform_id` identifies where a game is available.

| Bridge Table     | Coded Column  | Lookup Table | Lookup Label |
| ---------------- | ------------- | ------------ | ------------ |
| `game_platforms` | `platform_id` | `platforms`  | `name`       |

Use this query to get your platform mapping:

```sql
SELECT
    platform_id,
    name,
    abbreviation,
    generation,
    platform_family_id,
    platform_type_id
FROM platforms
ORDER BY name;
```

Example join:

```sql
SELECT
    g.name AS game_name,
    p.name AS platform_name,
    p.abbreviation
FROM game_platforms gp
JOIN games g
    ON gp.game_id = g.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id;
```

Recommended usage:

| Use Case           | How to Use                                                       |
| ------------------ | ---------------------------------------------------------------- |
| Platform filtering | Match user constraints like PC, Switch, PlayStation, Xbox.       |
| Dashboard          | Count games by platform.                                         |
| Release analysis   | Pair with `release_dates` to analyze platform-specific releases. |
| Recommendation     | Exclude games unavailable on the user’s selected platform.       |

---

## 5.2 `platforms.platform_family_id` → `platform_families.platform_family_id`

Platform families group related platforms.

| Table       | Coded Column         | Lookup Table        | Lookup Label |
| ----------- | -------------------- | ------------------- | ------------ |
| `platforms` | `platform_family_id` | `platform_families` | `name`       |

Use this query to get your platform family mapping:

```sql
SELECT
    platform_family_id,
    name,
    slug
FROM platform_families
ORDER BY name;
```

Recommended usage:

| Use Case          | How to Use                                                            |
| ----------------- | --------------------------------------------------------------------- |
| Platform grouping | Group PlayStation, Xbox, Nintendo, etc.                               |
| Dashboard         | Compare games by platform family.                                     |
| Recommendation    | Let users ask for “PlayStation games” rather than a specific console. |

---

## 5.3 `platforms.platform_type_id` → `platform_types.platform_type_id`

Platform types describe broad platform categories.

| Table       | Coded Column       | Lookup Table     | Lookup Label |
| ----------- | ------------------ | ---------------- | ------------ |
| `platforms` | `platform_type_id` | `platform_types` | `name`       |

Use this query to get your platform type mapping:

```sql
SELECT
    platform_type_id,
    name
FROM platform_types
ORDER BY platform_type_id;
```

Example meanings may include:

| Platform Type Name | Meaning                                                         |
| ------------------ | --------------------------------------------------------------- |
| Console            | Home console platform.                                          |
| Arcade             | Arcade platform.                                                |
| Operating System   | OS-level platform such as Windows, Mac, Linux, iOS, or Android. |
| Portable Console   | Handheld/portable console.                                      |
| Computer           | Computer platform.                                              |

Recommended usage:

| Use Case       | How to Use                                                        |
| -------------- | ----------------------------------------------------------------- |
| Dashboard      | Compare catalog composition by platform type.                     |
| Data cleaning  | Separate operating systems from consoles.                         |
| Recommendation | Interpret broad user requests like “PC games” or “console games.” |

---

# 6. Company Role Mappings

## 6.1 `involved_companies.company_id` → `companies.company_id`

This maps each game-company relationship to the actual company.

| Table                | Coded Column | Lookup Table | Lookup Label |
| -------------------- | ------------ | ------------ | ------------ |
| `involved_companies` | `company_id` | `companies`  | `name`       |

Use this query to get company mappings:

```sql
SELECT
    company_id,
    name,
    slug,
    country,
    start_date_iso
FROM companies
ORDER BY name;
```

---

## 6.2 Company Role Flags

Each row in `involved_companies` can contain multiple role flags.

| Column       | Stored Value | Meaning                                       |
| ------------ | -----------: | --------------------------------------------- |
| `developer`  |          `1` | Company developed the game.                   |
| `developer`  |          `0` | Company did not develop the game.             |
| `publisher`  |          `1` | Company published the game.                   |
| `publisher`  |          `0` | Company did not publish the game.             |
| `porting`    |          `1` | Company ported the game.                      |
| `porting`    |          `0` | Company did not port the game.                |
| `supporting` |          `1` | Company provided supporting development work. |
| `supporting` |          `0` | Company did not provide supporting work.      |

Important interpretation rule:

> One company can have multiple roles for the same game.

Example:

| developer | publisher | Meaning                                                      |
| --------: | --------: | ------------------------------------------------------------ |
|         1 |         0 | Developer only                                               |
|         0 |         1 | Publisher only                                               |
|         1 |         1 | Both developer and publisher                                 |
|         0 |         0 | Other role, such as porting/supporting, or role not captured |

Example query:

```sql
SELECT
    g.name AS game_name,
    c.name AS company_name,
    CASE WHEN ic.developer = 1 THEN 'Yes' ELSE 'No' END AS is_developer,
    CASE WHEN ic.publisher = 1 THEN 'Yes' ELSE 'No' END AS is_publisher,
    CASE WHEN ic.porting = 1 THEN 'Yes' ELSE 'No' END AS is_porting,
    CASE WHEN ic.supporting = 1 THEN 'Yes' ELSE 'No' END AS is_supporting
FROM involved_companies ic
JOIN games g
    ON ic.game_id = g.game_id
JOIN companies c
    ON ic.company_id = c.company_id;
```

Recommended usage:

| Use Case                   | How to Use                                        |
| -------------------------- | ------------------------------------------------- |
| Developer analysis         | Filter `developer = 1`.                           |
| Publisher analysis         | Filter `publisher = 1`.                           |
| Port analysis              | Filter `porting = 1`.                             |
| Recommendation explanation | Mention developer/publisher names when available. |

---

## 6.3 `companies.country`

The `country` column is a numeric country code.

| Table       | Column    | Meaning                                   |
| ----------- | --------- | ----------------------------------------- |
| `companies` | `country` | Country code associated with the company. |

Recommended handling:

| Option                    | Recommendation                            |
| ------------------------- | ----------------------------------------- |
| Keep as number            | Acceptable if not used in analysis.       |
| Create country mapping    | Better if analyzing companies by country. |
| Convert to readable label | Best for dashboard display.               |

Suggested future table:

```sql
CREATE TABLE country_codes (
    country_code INTEGER PRIMARY KEY,
    country_name TEXT,
    iso_alpha_2 TEXT,
    iso_alpha_3 TEXT
);
```

Until mapped, document `country` as:

```text
Numeric country code; join to an external ISO country mapping if used analytically.
```

---

## 6.4 Company Source References

`companies.status_id` and `companies.parent_company_id` are preserved IGDB
reference values, but the current schema does not include a `company_statuses`
lookup table and does not enforce the parent-company relationship.

Current behavior:

| Column | Interpretation |
| --- | --- |
| `status_id` | IGDB company-status code. Do not display it as a label until a lookup table is added. |
| `parent_company_id` | IGDB parent company ID. Join only when the referenced company exists locally. |

Of 254 non-null parent-company references, 187 currently resolve within the
550 extracted companies. Unresolved values are expected because company
extraction was scoped to companies involved with the selected games.

---

# 7. Release Date Lookup Mappings

## 7.1 `release_dates.date_format_id` → `date_formats.date_format_id`

Date format explains how precise the release date is.

| Table           | Coded Column     | Lookup Table   | Lookup Label  |
| --------------- | ---------------- | -------------- | ------------- |
| `release_dates` | `date_format_id` | `date_formats` | `format_name` |

Use this query to get your date format mapping:

```sql
SELECT
    date_format_id,
    format_name
FROM date_formats
ORDER BY date_format_id;
```

Current loaded mappings:

| ID | Format Name | Meaning |
| --: | --- | --- |
| 0 | YYYYMMDD | Exact year, month, and day. |
| 1 | YYYYMM | Year and month. |
| 2 | YYYY | Year only. |
| 3 | YYYYQ1 | First quarter. |
| 4 | YYYYQ2 | Second quarter. |
| 5 | YYYYQ3 | Third quarter. |
| 6 | YYYYQ4 | Fourth quarter. |
| 7 | TBD | Date to be determined. |

Recommended usage:

| Use Case            | How to Use                                              |
| ------------------- | ------------------------------------------------------- |
| Exact release trend | Use only exact dates if precision matters.              |
| Yearly trend        | Use `release_year`, even if exact day/month is missing. |
| Dashboard display   | Use `human` when `date_iso` is incomplete.              |
| Data quality        | Track how many records have exact vs incomplete dates.  |

---

## 7.2 `release_dates.release_date_region_id` → `release_date_regions.release_date_region_id`

Release region identifies where the release date applies.

| Table           | Coded Column             | Lookup Table           | Lookup Label  |
| --------------- | ------------------------ | ---------------------- | ------------- |
| `release_dates` | `release_date_region_id` | `release_date_regions` | `region_name` |

Use this query to get your release region mapping:

```sql
SELECT
    release_date_region_id,
    region_name
FROM release_date_regions
ORDER BY release_date_region_id;
```

Example meanings may include:

| Region Name   | Meaning                   |
| ------------- | ------------------------- |
| Worldwide     | Global/worldwide release. |
| North America | North American release.   |
| Europe        | European release.         |
| Japan         | Japanese release.         |
| Asia          | Broader Asian release.    |
| Australia     | Australian release.       |
| New Zealand   | New Zealand release.      |
| China         | Chinese release.          |
| Korea         | Korean release.           |
| Brazil        | Brazilian release.        |

Recommended usage:

| Use Case                | How to Use                                          |
| ----------------------- | --------------------------------------------------- |
| Global release analysis | Prefer worldwide releases when available.           |
| Regional analysis       | Group release dates by `region_name`.               |
| Platform analysis       | Compare release timing by platform and region.      |
| RAG explanation         | Mention region only when relevant to user question. |

---

## 7.3 `release_dates.release_date_status_id` → `release_date_statuses.release_date_status_id`

Release date status identifies the status of a specific release date.

| Table           | Coded Column             | Lookup Table            | Lookup Label  |
| --------------- | ------------------------ | ----------------------- | ------------- |
| `release_dates` | `release_date_status_id` | `release_date_statuses` | `status_name` |

Use this query to get your release date status mapping:

```sql
SELECT
    release_date_status_id,
    status_name
FROM release_date_statuses
ORDER BY release_date_status_id;
```

Current loaded mappings:

| ID | Status Name |
| --: | --- |
| 1 | Alpha |
| 2 | Beta |
| 3 | Early Access |
| 4 | Offline |
| 5 | Cancelled |
| 6 | Full Release |
| 34 | Advanced Access |
| 35 | Digital Compatibility Release |
| 36 | Next-Gen Optimization Patch Release |

`TBD` is a date-format value, not a release-status value.

Recommended usage:

| Use Case                    | How to Use                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------ |
| Historical release analysis | Prefer `Full Release` records when status is populated.                              |
| Upcoming game dashboard     | Separate Alpha, Beta, Early Access, and Advanced Access records.                     |
| Recommendation engine       | Avoid unreleased/cancelled records unless intentionally recommending upcoming games. |

---

## 7.4 Release Date Time Fields

| Table           | Column           | Stored Format  | Mapping / Interpretation                             |
| --------------- | ---------------- | -------------- | ---------------------------------------------------- |
| `release_dates` | `date_timestamp` | Unix timestamp | Convert to readable date.                            |
| `release_dates` | `date_iso`       | Text date      | Human-readable transformed date.                     |
| `release_dates` | `release_year`   | Integer year   | Year-level release feature.                          |
| `release_dates` | `release_month`  | Integer month  | `1 = January`, `2 = February`, ..., `12 = December`. |
| `release_dates` | `release_day`    | Integer day    | Day of month, usually 1–31.                          |
| `release_dates` | `human`          | Text           | Human-readable date string from source.              |

Month mapping:

| Stored Value | Month     |
| -----------: | --------- |
|            1 | January   |
|            2 | February  |
|            3 | March     |
|            4 | April     |
|            5 | May       |
|            6 | June      |
|            7 | July      |
|            8 | August    |
|            9 | September |
|           10 | October   |
|           11 | November  |
|           12 | December  |

---

# 8. Media and Website Mappings

## 8.1 `websites.website_type_id` → `website_types.website_type_id`

Website type explains what kind of external link the website is.

| Table      | Coded Column      | Lookup Table    | Lookup Label |
| ---------- | ----------------- | --------------- | ------------ |
| `websites` | `website_type_id` | `website_types` | `type_name`  |

Use this query to get your website type mapping:

```sql
SELECT
    website_type_id,
    type_name
FROM website_types
ORDER BY website_type_id;
```

Example meanings may include:

| Website Type Name | Meaning                        |
| ----------------- | ------------------------------ |
| Official          | Official website.              |
| Wikia / Fandom    | Wiki or fan documentation.     |
| Wikipedia         | Wikipedia page.                |
| Facebook          | Facebook page.                 |
| Twitter / X       | Twitter/X page.                |
| Twitch            | Twitch page.                   |
| Instagram         | Instagram page.                |
| YouTube           | YouTube page or channel.       |
| Steam             | Steam store page.              |
| Reddit            | Reddit community page.         |
| Itch.io           | Itch.io store page.            |
| Epic Games        | Epic Games Store page.         |
| GOG               | GOG store page.                |
| Discord           | Discord community/server link. |
| Bluesky           | Bluesky social page.           |

Recommended usage:

| Use Case       | How to Use                                                      |
| -------------- | --------------------------------------------------------------- |
| UI display     | Label links with readable website type.                         |
| Store matching | Use Steam, GOG, Epic, Itch.io links for store availability.     |
| RAG grounding  | Only mention links if they exist in the retrieved game context. |
| Data quality   | Prefer trusted official/store links for external navigation.    |

---

## 8.2 `websites.trusted`

| Stored Value | Meaning                            |
| -----------: | ---------------------------------- |
|          `1` | Website is trusted.                |
|          `0` | Website is not trusted.            |
|       `NULL` | Trust value is unknown or missing. |

Recommended usage:

| Use Case                   | Rule                                                |
| -------------------------- | --------------------------------------------------- |
| App display                | Prefer trusted links first.                         |
| Recommendation explanation | Avoid citing untrusted links as authoritative.      |
| Data quality               | Track the proportion of trusted vs untrusted links. |

---

## 8.3 Image Size Fields

Image tables:

| Table         | Columns           |
| ------------- | ----------------- |
| `covers`      | `width`, `height` |
| `screenshots` | `width`, `height` |

Mapping:

| Column   | Unit   | Interpretation |
| -------- | ------ | -------------- |
| `width`  | Pixels | Image width.   |
| `height` | Pixels | Image height.  |

Recommended usage:

| Use Case         | Rule                                                                     |
| ---------------- | ------------------------------------------------------------------------ |
| UI cards         | Use covers for game cards.                                               |
| Game detail page | Use screenshots for visual preview.                                      |
| Data quality     | Filter out records with missing image URLs if visual UI requires images. |

---

# 9. External Game Mapping

## 9.1 `external_games.external_game_source_id` → `external_game_sources.external_game_source_id`

External game source identifies which outside service/store/database the game record maps to.

| Table                   | Coded Column                    | Lookup Table            | Lookup Label  |
| ----------------------- | ------------------------------- | ----------------------- | ------------- |
| `external_games`        | `external_game_source_id`       | `external_game_sources` | `source_name` |
| `popularity_primitives` | `external_popularity_source_id` | `external_game_sources` | `source_name` |
| `popularity_types`      | `external_popularity_source_id` | `external_game_sources` | `source_name` |

Use this query to get your source mapping:

```sql
SELECT
    external_game_source_id,
    source_name
FROM external_game_sources
ORDER BY external_game_source_id;
```

Example source names may include:

| Source Name           | Meaning                              |
| --------------------- | ------------------------------------ |
| IGDB                  | IGDB-native source.                  |
| Steam                 | Steam-related source.                |
| GOG                   | GOG-related source.                  |
| Epic Games            | Epic-related source.                 |
| Twitch                | Twitch-related source.               |
| Other external source | Any other supported external system. |

Recommended usage:

| Use Case            | How to Use                                        |
| ------------------- | ------------------------------------------------- |
| Store matching      | Use source name to identify Steam/GOG/Epic links. |
| Popularity analysis | Group popularity signals by source.               |
| Future price data   | Use external IDs to join with non-IGDB datasets.  |

---

## 9.2 `external_games.game_release_format_id` → `game_release_formats.game_release_format_id`

Game release format identifies the format of an external game record.

| Table            | Coded Column             | Lookup Table           | Lookup Label  |
| ---------------- | ------------------------ | ---------------------- | ------------- |
| `external_games` | `game_release_format_id` | `game_release_formats` | `format_name` |

Use this query to get your release format mapping:

```sql
SELECT
    game_release_format_id,
    format_name
FROM game_release_formats
ORDER BY game_release_format_id;
```

Recommended usage:

| Use Case               | How to Use                                                           |
| ---------------------- | -------------------------------------------------------------------- |
| External game cleaning | Distinguish different release formats.                               |
| Store matching         | Check whether the external game record is relevant to the main game. |
| Future extension       | Useful if later adding price/store data.                             |

---

## 9.3 `external_games.platform_id` → `platforms.platform_id`

The platform on an external game record should be interpreted through the `platforms` table.

```sql
SELECT
    eg.external_game_id,
    eg.uid,
    egs.source_name,
    p.name AS platform_name,
    eg.url
FROM external_games eg
LEFT JOIN external_game_sources egs
    ON eg.external_game_source_id = egs.external_game_source_id
LEFT JOIN platforms p
    ON eg.platform_id = p.platform_id;
```

---

# 10. Multiplayer Mode Mappings

## 10.1 Multiplayer Boolean Flags

| Table               | Column          | Stored Value | Meaning                                    |
| ------------------- | --------------- | -----------: | ------------------------------------------ |
| `multiplayer_modes` | `campaign_coop` |          `1` | Campaign co-op is supported.               |
| `multiplayer_modes` | `campaign_coop` |          `0` | Campaign co-op is not supported.           |
| `multiplayer_modes` | `drop_in`       |          `1` | Drop-in multiplayer is supported.          |
| `multiplayer_modes` | `drop_in`       |          `0` | Drop-in multiplayer is not supported.      |
| `multiplayer_modes` | `lan_coop`      |          `1` | LAN co-op is supported.                    |
| `multiplayer_modes` | `lan_coop`      |          `0` | LAN co-op is not supported.                |
| `multiplayer_modes` | `offline_coop`  |          `1` | Offline/local co-op is supported.          |
| `multiplayer_modes` | `offline_coop`  |          `0` | Offline/local co-op is not supported.      |
| `multiplayer_modes` | `online_coop`   |          `1` | Online co-op is supported.                 |
| `multiplayer_modes` | `online_coop`   |          `0` | Online co-op is not supported.             |
| `multiplayer_modes` | `split_screen`  |          `1` | Split-screen multiplayer is supported.     |
| `multiplayer_modes` | `split_screen`  |          `0` | Split-screen multiplayer is not supported. |
| `multiplayer_modes` | `split_screen_online` | `1` | Online split-screen is supported.      |
| `multiplayer_modes` | `split_screen_online` | `0` | Online split-screen is not supported.  |

The current extract has `split_screen_online = NULL` for all 342 multiplayer
records because IGDB did not return this optional field for the selected rows.

Player-capacity columns:

| Column | Meaning |
| --- | --- |
| `offline_coop_max` | Maximum offline co-op players. |
| `offline_max` | Maximum offline multiplayer players. |
| `online_coop_max` | Maximum online co-op players. |
| `online_max` | Maximum online multiplayer players. |

These values are counts, not booleans. A value of `0` is different from
`NULL`: zero is a supplied source value, while null means no value was returned.

Important interpretation rule:

> Multiplayer support can vary by platform. Always interpret multiplayer flags together with `platform_id`.

Example query:

```sql
SELECT
    g.name AS game_name,
    p.name AS platform_name,
    mm.campaign_coop,
    mm.offline_coop,
    mm.online_coop,
    mm.split_screen
FROM multiplayer_modes mm
JOIN games g
    ON mm.game_id = g.game_id
LEFT JOIN platforms p
    ON mm.platform_id = p.platform_id;
```

Recommended usage:

| User Prompt            | Database Rule       |
| ---------------------- | ------------------- |
| “local co-op games”    | `offline_coop = 1`  |
| “online co-op games”   | `online_coop = 1`   |
| “split-screen games”   | `split_screen = 1`  |
| “co-op campaign games” | `campaign_coop = 1` |

---

# 11. Time-to-Beat Mappings

## 11.1 `game_time_to_beats` Time Fields

| Table                | Column       | Unit    | Meaning                                     |
| -------------------- | ------------ | ------- | ------------------------------------------- |
| `game_time_to_beats` | `hastily`    | Seconds | Average quick completion time.              |
| `game_time_to_beats` | `normally`   | Seconds | Average normal completion time.             |
| `game_time_to_beats` | `completely` | Seconds | Average completionist time.                 |
| `game_time_to_beats` | `count`      | Count   | Number of observations behind the estimate. |

Recommended derived fields:

```sql
SELECT
    game_id,
    hastily / 3600.0 AS hastily_hours,
    normally / 3600.0 AS normally_hours,
    completely / 3600.0 AS completely_hours,
    count
FROM game_time_to_beats;
```

Suggested interpretation:

|       Hours | Recommendation Label |
| ----------: | -------------------- |
|   0–5 hours | Very short           |
|  5–15 hours | Short                |
| 15–30 hours | Medium               |
| 30–60 hours | Long                 |
|   60+ hours | Very long            |

Use carefully: these labels are project-defined, not IGDB-defined.

Recommended usage:

| User Prompt          | Database Rule                                          |
| -------------------- | ------------------------------------------------------ |
| “short game”         | Use `normally_hours <= 15`.                            |
| “long RPG”           | Use `normally_hours >= 30` and relevant genres/themes. |
| “completionist game” | Use `completely_hours` for full-content estimates.     |

---

# 12. Popularity Mappings

## 12.1 `popularity_primitives.popularity_type_id` → `popularity_types.popularity_type_id`

Popularity type explains what the popularity value represents.

| Table                   | Coded Column         | Lookup Table       | Lookup Label |
| ----------------------- | -------------------- | ------------------ | ------------ |
| `popularity_primitives` | `popularity_type_id` | `popularity_types` | `name`       |

Use this query to get your popularity type mapping:

```sql
SELECT
    popularity_type_id,
    external_popularity_source_id,
    name
FROM popularity_types
ORDER BY external_popularity_source_id, popularity_type_id;
```

Current loaded mappings:

| ID | Source | Popularity Type |
| --: | --- | --- |
| 1 | IGDB | Visits |
| 2 | IGDB | Want to Play |
| 3 | IGDB | Playing |
| 4 | IGDB | Played |
| 5 | Steam | 24hr Peak Players |
| 6 | Steam | Postitive Reviews |
| 7 | Steam | Negative Reviews |
| 8 | Steam | Total Reviews |
| 9 | Steam | Global Top Sellers |
| 10 | Steam | Most Wishlisted Upcoming |
| 34 | Twitch | 24hr Hours Watched |

`Postitive Reviews` is the spelling currently returned by the IGDB lookup and
is preserved as source data.

Important interpretation rule:

> `popularity_primitives.value` has no universal meaning by itself. Its meaning depends on `popularity_type_id` and `external_popularity_source_id`.

Example join:

```sql
SELECT
    g.name AS game_name,
    egs.source_name,
    pt.name AS popularity_type,
    pp.value,
    pp.calculated_at
FROM popularity_primitives pp
JOIN games g
    ON pp.game_id = g.game_id
LEFT JOIN popularity_types pt
    ON pp.popularity_type_id = pt.popularity_type_id
LEFT JOIN external_game_sources egs
    ON pp.external_popularity_source_id = egs.external_game_source_id;
```

Recommended usage:

| Use Case             | How to Use                                                             |
| -------------------- | ---------------------------------------------------------------------- |
| Popularity dashboard | Group by `popularity_types.name`.                                      |
| Hidden gem scoring   | Compare high ratings against lower popularity values.                  |
| Recommendation       | Use popularity as a soft ranking feature, not the only ranking factor. |
| Trend analysis       | Use `calculated_at` if storing snapshots over time.                    |

---

## 12.2 `popularity_primitives.external_popularity_source_id` → `external_game_sources.external_game_source_id`

This field identifies the source behind the popularity value.

| Table                   | Coded Column                    | Lookup Table            | Lookup Label  |
| ----------------------- | ------------------------------- | ----------------------- | ------------- |
| `popularity_primitives` | `external_popularity_source_id` | `external_game_sources` | `source_name` |
| `popularity_types`      | `external_popularity_source_id` | `external_game_sources` | `source_name` |

Recommended usage:

| Source | How to Interpret                             |
| ------ | -------------------------------------------- |
| IGDB   | Interest/activity from IGDB.                 |
| Steam  | Store/player/review/wishlist-related signal. |
| Twitch | Viewer/watch-related signal.                 |
| Other  | Interpret according to source documentation. |

---

# 13. Rating and Count Mappings

## 13.1 Rating Fields in `games`

| Column               | Unit             | Allowed Range | Meaning                                                  |
| -------------------- | ---------------- | ------------- | -------------------------------------------------------- |
| `rating`             | Score out of 100 | 0–100         | Average IGDB user rating.                                |
| `total_rating`       | Score out of 100 | 0–100         | Combined rating score based on available rating sources. |
| `rating_count`       | Count            | 0 or greater  | Number of IGDB user ratings.                             |
| `total_rating_count` | Count            | 0 or greater  | Number of ratings behind `total_rating`.                 |

Recommended project-defined quality mapping:

| Total Rating | Suggested Label             |
| -----------: | --------------------------- |
|       90–100 | Excellent                   |
|     80–89.99 | Highly Rated                |
|     70–79.99 | Good                        |
|     60–69.99 | Mixed / Average             |
|     Below 60 | Lower Rated                 |
|         NULL | Unrated / Insufficient Data |

Project modeling rule:

```text
highly_rated = 1 if total_rating >= 80
highly_rated = 0 if total_rating < 80
```

Use caution:

> Rating labels such as “Excellent” or “Good” are project-defined interpretation bands, not official IGDB categories.

---

## 13.2 Rating Confidence Mapping

| Count Field                  | Suggested Interpretation                      |
| ---------------------------- | --------------------------------------------- |
| `rating_count = 0` or `NULL` | No or insufficient IGDB user rating evidence. |
| `rating_count < 10`          | Very low confidence.                          |
| `rating_count 10–49`         | Low confidence.                               |
| `rating_count 50–199`        | Medium confidence.                            |
| `rating_count >= 200`        | Higher confidence.                            |

Use caution:

> These confidence bands are project-defined. They are useful for filtering and analysis but are not official IGDB categories.

Recommended filter for rating-based analysis:

```sql
WHERE total_rating IS NOT NULL
  AND total_rating_count >= 10
```

---

# 14. Timestamp Mappings

## 14.1 Timestamp Fields

| Table                   | Column               | Stored Format  | Human-Readable Field       |
| ----------------------- | -------------------- | -------------- | -------------------------- |
| `games`                 | `first_release_date` | Unix timestamp | `first_release_date_iso`   |
| `games`                 | `updated_at`         | Unix timestamp | `updated_at_iso`           |
| `companies`             | `start_date`         | Unix timestamp | `start_date_iso`           |
| `companies`             | `updated_at`         | Unix timestamp | `updated_at_iso`           |
| `involved_companies`    | `updated_at`         | Unix timestamp | `updated_at_iso`           |
| `release_dates`         | `date_timestamp`     | Unix timestamp | `date_iso`                 |
| `game_time_to_beats`    | `updated_at`         | Unix timestamp | `updated_at_iso`           |
| `popularity_primitives` | `calculated_at`      | Unix timestamp | `calculated_at_iso`        |
| `popularity_primitives` | `updated_at`         | Unix timestamp | `updated_at_iso`           |

Company `9254` has a source `start_date` outside Python's supported calendar
range. Its raw timestamp is preserved and `start_date_iso` is intentionally
null.

Recommended SQLite conversion:

```sql
SELECT
    game_id,
    name,
    datetime(first_release_date, 'unixepoch') AS first_release_datetime
FROM games
WHERE first_release_date IS NOT NULL;
```

Recommended interpretation:

| Field                          | Use Case                                    |
| ------------------------------ | ------------------------------------------- |
| `first_release_date`           | Original game-level first release timing.   |
| `release_dates.date_timestamp` | Specific release timing by platform/region. |
| `release_year`                 | Yearly trends and modeling.                 |
| `release_month`                | Seasonal analysis.                          |
| `calculated_at`                | Popularity snapshot timing.                 |

---

# 15. Image and URL Mappings

## 15.1 `covers.image_id` and `screenshots.image_id`

| Column     | Meaning                                                  |
| ---------- | -------------------------------------------------------- |
| `image_id` | IGDB image hash/identifier used to construct image URLs. |
| `url`      | Stored image URL or URL fragment.                        |

Recommended usage:

| Use Case             | Rule                                                              |
| -------------------- | ----------------------------------------------------------------- |
| Streamlit game cards | Use cover images.                                                 |
| Game detail page     | Use screenshots.                                                  |
| RAG response         | Avoid making visual claims unless images are available and shown. |

---

## 15.2 URL Fields

URL columns in this ERD:

| Table            | Column | Meaning                             |
| ---------------- | ------ | ----------------------------------- |
| `websites`       | `url`  | External website for a game.        |
| `external_games` | `url`  | External source/store/database URL. |
| `covers`         | `url`  | Cover image URL.                    |
| `screenshots`    | `url`  | Screenshot image URL.               |

Recommended validation:

```sql
SELECT *
FROM websites
WHERE url IS NULL
   OR TRIM(url) = '';
```

---

# 16. Complete Lookup Mapping Checklist

Use this checklist to confirm all lookup mappings are documented.

| Mapping Area               | Coded Field                                           | Lookup Table            | Status   |
| -------------------------- | ----------------------------------------------------- | ----------------------- | -------- |
| Game type                  | `games.game_type_id`                                  | `game_types`            | Required |
| Game status                | `games.game_status_id`                                | `game_statuses`         | Required |
| Genre                      | `game_genres.genre_id`                                | `genres`                | Required |
| Theme                      | `game_themes.theme_id`                                | `themes`                | Required |
| Keyword                    | `game_keywords.keyword_id`                            | `keywords`              | Required |
| Game mode                  | `game_modes_bridge.game_mode_id`                      | `game_modes`            | Required |
| Player perspective         | `game_player_perspectives.player_perspective_id`      | `player_perspectives`   | Required |
| Platform                   | `game_platforms.platform_id`                          | `platforms`             | Required |
| Platform family            | `platforms.platform_family_id`                        | `platform_families`     | Required |
| Platform type              | `platforms.platform_type_id`                          | `platform_types`        | Required |
| Company                    | `involved_companies.company_id`                       | `companies`             | Required |
| Release date format        | `release_dates.date_format_id`                        | `date_formats`          | Required |
| Release date region        | `release_dates.release_date_region_id`                | `release_date_regions`  | Required |
| Release date status        | `release_dates.release_date_status_id`                | `release_date_statuses` | Required |
| Website type               | `websites.website_type_id`                            | `website_types`         | Required |
| External game source       | `external_games.external_game_source_id`              | `external_game_sources` | Required |
| Game release format        | `external_games.game_release_format_id`               | `game_release_formats`  | Required |
| External popularity source | `popularity_primitives.external_popularity_source_id` | `external_game_sources` | Required |
| Popularity type            | `popularity_primitives.popularity_type_id`            | `popularity_types`      | Required |

---

# 17. Recommended SQL View for Readable Game Profiles

To avoid constantly joining lookup tables manually, create a readable profile view.

```sql
CREATE VIEW IF NOT EXISTS vw_game_basic_profile AS
SELECT
    g.game_id,
    g.name,
    g.slug,
    g.summary,
    g.storyline,
    g.first_release_date_iso,
    g.release_year,
    g.rating,
    g.rating_count,
    g.total_rating,
    g.total_rating_count,
    gt.type_name AS game_type,
    gs.status_name AS game_status
FROM games g
LEFT JOIN game_types gt
    ON g.game_type_id = gt.game_type_id
LEFT JOIN game_statuses gs
    ON g.game_status_id = gs.game_status_id;
```

---

# 18. Recommended SQL View for Game Genres

```sql
CREATE VIEW IF NOT EXISTS vw_game_genres AS
SELECT
    g.game_id,
    g.name AS game_name,
    ge.genre_id,
    ge.name AS genre_name
FROM game_genres gg
JOIN games g
    ON gg.game_id = g.game_id
JOIN genres ge
    ON gg.genre_id = ge.genre_id;
```

---

# 19. Recommended SQL View for Game Platforms

```sql
CREATE VIEW IF NOT EXISTS vw_game_platforms AS
SELECT
    g.game_id,
    g.name AS game_name,
    p.platform_id,
    p.name AS platform_name,
    p.abbreviation,
    pf.name AS platform_family,
    pt.name AS platform_type
FROM game_platforms gp
JOIN games g
    ON gp.game_id = g.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id
LEFT JOIN platform_families pf
    ON p.platform_family_id = pf.platform_family_id
LEFT JOIN platform_types pt
    ON p.platform_type_id = pt.platform_type_id;
```

---

# 20. Recommended SQL View for Companies and Roles

```sql
CREATE VIEW IF NOT EXISTS vw_game_companies AS
SELECT
    g.game_id,
    g.name AS game_name,
    c.company_id,
    c.name AS company_name,
    CASE WHEN ic.developer = 1 THEN 'Yes' ELSE 'No' END AS is_developer,
    CASE WHEN ic.publisher = 1 THEN 'Yes' ELSE 'No' END AS is_publisher,
    CASE WHEN ic.porting = 1 THEN 'Yes' ELSE 'No' END AS is_porting,
    CASE WHEN ic.supporting = 1 THEN 'Yes' ELSE 'No' END AS is_supporting
FROM involved_companies ic
JOIN games g
    ON ic.game_id = g.game_id
JOIN companies c
    ON ic.company_id = c.company_id;
```

---

# 21. Recommended SQL View for Release Dates

```sql
CREATE VIEW IF NOT EXISTS vw_game_release_dates AS
SELECT
    rd.release_date_id,
    g.game_id,
    g.name AS game_name,
    p.platform_id,
    p.name AS platform_name,
    rd.date_iso,
    rd.release_year,
    rd.release_month,
    rd.release_day,
    df.format_name AS date_format,
    rdr.region_name AS release_region,
    rds.status_name AS release_status,
    rd.human
FROM release_dates rd
JOIN games g
    ON rd.game_id = g.game_id
LEFT JOIN platforms p
    ON rd.platform_id = p.platform_id
LEFT JOIN date_formats df
    ON rd.date_format_id = df.date_format_id
LEFT JOIN release_date_regions rdr
    ON rd.release_date_region_id = rdr.release_date_region_id
LEFT JOIN release_date_statuses rds
    ON rd.release_date_status_id = rds.release_date_status_id;
```

---

# 22. Recommended SQL View for Popularity Signals

```sql
CREATE VIEW IF NOT EXISTS vw_game_popularity AS
SELECT
    pp.popularity_primitive_id,
    g.game_id,
    g.name AS game_name,
    egs.source_name AS popularity_source,
    pt.name AS popularity_type,
    pp.value,
    pp.calculated_at
FROM popularity_primitives pp
JOIN games g
    ON pp.game_id = g.game_id
LEFT JOIN popularity_types pt
    ON pp.popularity_type_id = pt.popularity_type_id
LEFT JOIN external_game_sources egs
    ON pp.external_popularity_source_id = egs.external_game_source_id;
```

---

# 23. Project-Defined Analytical Mappings

These mappings are not official IGDB categories. They are project-defined labels to support analytics, dashboards, and recommendations.

## 23.1 Rating Bands

| Rule                                       | Label           |
| ------------------------------------------ | --------------- |
| `total_rating >= 90`                       | Excellent       |
| `total_rating >= 80 AND total_rating < 90` | Highly Rated    |
| `total_rating >= 70 AND total_rating < 80` | Good            |
| `total_rating >= 60 AND total_rating < 70` | Mixed / Average |
| `total_rating < 60`                        | Lower Rated     |
| `total_rating IS NULL`                     | Unrated         |

## 23.2 Rating Confidence Bands

| Rule                                                   | Label               |
| ------------------------------------------------------ | ------------------- |
| `total_rating_count IS NULL OR total_rating_count = 0` | No Rating Evidence  |
| `total_rating_count < 10`                              | Very Low Confidence |
| `total_rating_count BETWEEN 10 AND 49`                 | Low Confidence      |
| `total_rating_count BETWEEN 50 AND 199`                | Medium Confidence   |
| `total_rating_count >= 200`                            | Higher Confidence   |

## 23.3 Playtime Bands

Use `normally / 3600.0` to convert seconds to hours.

| Rule                                           | Label      |
| ---------------------------------------------- | ---------- |
| `normally_hours <= 5`                          | Very Short |
| `normally_hours > 5 AND normally_hours <= 15`  | Short      |
| `normally_hours > 15 AND normally_hours <= 30` | Medium     |
| `normally_hours > 30 AND normally_hours <= 60` | Long       |
| `normally_hours > 60`                          | Very Long  |

## 23.4 Hidden Gem Candidate Rule

A simple first version:

```text
Hidden Gem Candidate =
total_rating >= 80
AND total_rating_count >= 10
AND popularity value is below the median popularity value for comparable games
```

More advanced version:

```text
Hidden Gem Score =
normalized_total_rating
- normalized_popularity
+ niche_bonus
```

Recommended note:

> Hidden gem definitions are project-defined and should be documented in the final methodology section.

---


