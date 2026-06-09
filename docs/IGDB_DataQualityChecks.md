# IGDB Relational Database Data Quality Checks

## Purpose

This document defines executable data quality checks for the IGDB relational SQLite database used in the **IGDB Game Discovery & RAG Recommendation System**.

The goal is to verify that the database is:

* Structurally valid
* Referentially consistent
* Free of duplicate primary keys and duplicate bridge relationships
* Safe for analytics, modeling, recommendation, dashboarding, and RAG grounding
* Aligned with the ERD and business rules

Database file:

```text
data/database/igdb_games.db
```

File location:

```text
docs/IGDB_DataQualityChecks.md
```

Related files:

```text
docs/IGDB_ERD_Data_Dictionary.md
docs/IGDB_ERD_ValueMapping.md
docs/IGDB_ERD_BusinessRules.md
docs/IGDB_relational_ERD.md
```

---

## Current Validation Snapshot

Validated against `data/database/igdb_games.db` on **2026-06-09**.

| Result | Current Value |
| --- | ---: |
| SQLite tables | 34 |
| Games | 500 |
| Empty tables | 0 |
| `PRAGMA integrity_check` | `ok` |
| `PRAGMA foreign_key_check` failures | 0 |
| Games with a platform | 500 |
| Games with a summary | 500 |
| Games with `total_rating` | 500 |
| Games with a genre | 500 |
| Games with a theme | 499 |
| Games with a keyword | 498 |

Documented exceptions:

* `game_time_to_beats` contains 60 rows where the average quick, normal, and
  completionist estimates are not monotonically ordered. These are retained as
  source values and treated as a warning, not a relational-integrity failure.
* Company `9254` (`Blade Games World`) has an IGDB founding timestamp outside
  Python's supported calendar range. The raw `start_date` is preserved and
  `start_date_iso` is intentionally `NULL`.
* The extraction selected 500 games ordered by `total_rating_count` descending
  and required a summary. Completeness and hidden-gem results therefore describe
  this curated sample, not the full IGDB catalog.

---

# 1. How to Read These Checks

Each check includes:

| Field           | Meaning                                      |
| --------------- | -------------------------------------------- |
| Check ID        | Unique identifier for the check.             |
| Purpose         | What the check validates.                    |
| SQL             | Query to run against the SQLite database.    |
| Expected Result | What a passing result should look like.      |
| Severity        | How serious the issue is if the check fails. |

## Severity Levels

| Severity | Meaning                                            |
| -------- | -------------------------------------------------- |
| Critical | Must fix before analysis/modeling/recommendations. |
| High     | Should fix before final deliverable.               |
| Medium   | Should investigate and document.                   |
| Low      | Nice to improve, but not blocking.                 |

---

# 2. Recommended Python Runner

You can store the SQL checks in this document, but it is also useful to run them automatically.

Example Python runner:

```python
import sqlite3
import pandas as pd

DB_PATH = "data/database/igdb_games.db"

def run_check(check_name: str, query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"\n--- {check_name} ---")
    print(f"Rows returned: {len(df)}")
    if len(df) > 0:
        print(df.head(20))
    return df
```

For most checks in this document:

```text
PASS = 0 rows returned
FAIL = 1 or more rows returned
```

Some summary checks are different and are clearly labeled.

---

# 3. Database Structure Checks

## DQ-001 — Confirm Expected Tables Exist

**Purpose:** Verify that all ERD tables exist in the SQLite database.

**Severity:** Critical

```sql
SELECT name AS table_name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

**Expected Result:**

The database should include the following tables:

```text
companies
covers
date_formats
external_game_sources
external_games
game_genres
game_keywords
game_modes
game_modes_bridge
game_platforms
game_player_perspectives
game_release_formats
game_statuses
game_themes
game_time_to_beats
game_types
games
genres
involved_companies
keywords
multiplayer_modes
platform_families
platform_types
platforms
player_perspectives
popularity_primitives
popularity_types
release_date_regions
release_date_statuses
release_dates
screenshots
themes
website_types
websites
```

**Current Result:** 34 tables.

---

## DQ-002 — Confirm Empty Tables

**Purpose:** Identify tables with zero rows.

**Severity:** Medium

```sql
SELECT 'games' AS table_name, COUNT(*) AS row_count FROM games
UNION ALL SELECT 'game_types', COUNT(*) FROM game_types
UNION ALL SELECT 'game_statuses', COUNT(*) FROM game_statuses
UNION ALL SELECT 'genres', COUNT(*) FROM genres
UNION ALL SELECT 'themes', COUNT(*) FROM themes
UNION ALL SELECT 'keywords', COUNT(*) FROM keywords
UNION ALL SELECT 'game_modes', COUNT(*) FROM game_modes
UNION ALL SELECT 'player_perspectives', COUNT(*) FROM player_perspectives
UNION ALL SELECT 'game_genres', COUNT(*) FROM game_genres
UNION ALL SELECT 'game_themes', COUNT(*) FROM game_themes
UNION ALL SELECT 'game_keywords', COUNT(*) FROM game_keywords
UNION ALL SELECT 'game_modes_bridge', COUNT(*) FROM game_modes_bridge
UNION ALL SELECT 'game_player_perspectives', COUNT(*) FROM game_player_perspectives
UNION ALL SELECT 'platforms', COUNT(*) FROM platforms
UNION ALL SELECT 'platform_families', COUNT(*) FROM platform_families
UNION ALL SELECT 'platform_types', COUNT(*) FROM platform_types
UNION ALL SELECT 'game_platforms', COUNT(*) FROM game_platforms
UNION ALL SELECT 'companies', COUNT(*) FROM companies
UNION ALL SELECT 'involved_companies', COUNT(*) FROM involved_companies
UNION ALL SELECT 'release_dates', COUNT(*) FROM release_dates
UNION ALL SELECT 'date_formats', COUNT(*) FROM date_formats
UNION ALL SELECT 'release_date_regions', COUNT(*) FROM release_date_regions
UNION ALL SELECT 'release_date_statuses', COUNT(*) FROM release_date_statuses
UNION ALL SELECT 'covers', COUNT(*) FROM covers
UNION ALL SELECT 'screenshots', COUNT(*) FROM screenshots
UNION ALL SELECT 'websites', COUNT(*) FROM websites
UNION ALL SELECT 'website_types', COUNT(*) FROM website_types
UNION ALL SELECT 'external_games', COUNT(*) FROM external_games
UNION ALL SELECT 'external_game_sources', COUNT(*) FROM external_game_sources
UNION ALL SELECT 'game_release_formats', COUNT(*) FROM game_release_formats
UNION ALL SELECT 'multiplayer_modes', COUNT(*) FROM multiplayer_modes
UNION ALL SELECT 'game_time_to_beats', COUNT(*) FROM game_time_to_beats
UNION ALL SELECT 'popularity_primitives', COUNT(*) FROM popularity_primitives
UNION ALL SELECT 'popularity_types', COUNT(*) FROM popularity_types
ORDER BY table_name;
```

**Expected Result:**

Core tables should not be empty:

```text
games
genres
themes
platforms
game_genres
game_platforms
```

Some enrichment tables may be empty depending on extraction scope, but that should be documented.

---

# 4. Primary Key Checks

## DQ-003 — Null Primary Keys

**Purpose:** Verify that no primary key is null.

**Severity:** Critical

```sql
SELECT 'games' AS table_name, COUNT(*) AS null_pk_count FROM games WHERE game_id IS NULL
UNION ALL SELECT 'game_types', COUNT(*) FROM game_types WHERE game_type_id IS NULL
UNION ALL SELECT 'game_statuses', COUNT(*) FROM game_statuses WHERE game_status_id IS NULL
UNION ALL SELECT 'genres', COUNT(*) FROM genres WHERE genre_id IS NULL
UNION ALL SELECT 'themes', COUNT(*) FROM themes WHERE theme_id IS NULL
UNION ALL SELECT 'keywords', COUNT(*) FROM keywords WHERE keyword_id IS NULL
UNION ALL SELECT 'game_modes', COUNT(*) FROM game_modes WHERE game_mode_id IS NULL
UNION ALL SELECT 'player_perspectives', COUNT(*) FROM player_perspectives WHERE player_perspective_id IS NULL
UNION ALL SELECT 'platforms', COUNT(*) FROM platforms WHERE platform_id IS NULL
UNION ALL SELECT 'platform_families', COUNT(*) FROM platform_families WHERE platform_family_id IS NULL
UNION ALL SELECT 'platform_types', COUNT(*) FROM platform_types WHERE platform_type_id IS NULL
UNION ALL SELECT 'companies', COUNT(*) FROM companies WHERE company_id IS NULL
UNION ALL SELECT 'involved_companies', COUNT(*) FROM involved_companies WHERE involved_company_id IS NULL
UNION ALL SELECT 'release_dates', COUNT(*) FROM release_dates WHERE release_date_id IS NULL
UNION ALL SELECT 'date_formats', COUNT(*) FROM date_formats WHERE date_format_id IS NULL
UNION ALL SELECT 'release_date_regions', COUNT(*) FROM release_date_regions WHERE release_date_region_id IS NULL
UNION ALL SELECT 'release_date_statuses', COUNT(*) FROM release_date_statuses WHERE release_date_status_id IS NULL
UNION ALL SELECT 'covers', COUNT(*) FROM covers WHERE cover_id IS NULL
UNION ALL SELECT 'screenshots', COUNT(*) FROM screenshots WHERE screenshot_id IS NULL
UNION ALL SELECT 'websites', COUNT(*) FROM websites WHERE website_id IS NULL
UNION ALL SELECT 'website_types', COUNT(*) FROM website_types WHERE website_type_id IS NULL
UNION ALL SELECT 'external_games', COUNT(*) FROM external_games WHERE external_game_id IS NULL
UNION ALL SELECT 'external_game_sources', COUNT(*) FROM external_game_sources WHERE external_game_source_id IS NULL
UNION ALL SELECT 'game_release_formats', COUNT(*) FROM game_release_formats WHERE game_release_format_id IS NULL
UNION ALL SELECT 'multiplayer_modes', COUNT(*) FROM multiplayer_modes WHERE multiplayer_mode_id IS NULL
UNION ALL SELECT 'game_time_to_beats', COUNT(*) FROM game_time_to_beats WHERE game_time_to_beat_id IS NULL
UNION ALL SELECT 'popularity_primitives', COUNT(*) FROM popularity_primitives WHERE popularity_primitive_id IS NULL
UNION ALL SELECT 'popularity_types', COUNT(*) FROM popularity_types WHERE popularity_type_id IS NULL;
```

**Expected Result:**

Every `null_pk_count` should be `0`.

---

## DQ-004 — Duplicate Primary Keys

**Purpose:** Verify that primary keys are unique.

**Severity:** Critical

```sql
SELECT 'games' AS table_name, game_id AS id_value, COUNT(*) AS duplicate_count
FROM games
GROUP BY game_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'genres', genre_id, COUNT(*)
FROM genres
GROUP BY genre_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'themes', theme_id, COUNT(*)
FROM themes
GROUP BY theme_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'keywords', keyword_id, COUNT(*)
FROM keywords
GROUP BY keyword_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'platforms', platform_id, COUNT(*)
FROM platforms
GROUP BY platform_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'companies', company_id, COUNT(*)
FROM companies
GROUP BY company_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'release_dates', release_date_id, COUNT(*)
FROM release_dates
GROUP BY release_date_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'covers', cover_id, COUNT(*)
FROM covers
GROUP BY cover_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'screenshots', screenshot_id, COUNT(*)
FROM screenshots
GROUP BY screenshot_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'websites', website_id, COUNT(*)
FROM websites
GROUP BY website_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'external_games', external_game_id, COUNT(*)
FROM external_games
GROUP BY external_game_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'popularity_primitives', popularity_primitive_id, COUNT(*)
FROM popularity_primitives
GROUP BY popularity_primitive_id
HAVING COUNT(*) > 1;
```

**Expected Result:**

0 rows.

---

# 5. Bridge Table Duplicate Checks

Bridge tables should not contain duplicate relationship pairs.

## DQ-005 — Duplicate Game-Genre Relationships

**Severity:** Critical

```sql
SELECT game_id, genre_id, COUNT(*) AS duplicate_count
FROM game_genres
GROUP BY game_id, genre_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

## DQ-006 — Duplicate Game-Theme Relationships

**Severity:** Critical

```sql
SELECT game_id, theme_id, COUNT(*) AS duplicate_count
FROM game_themes
GROUP BY game_id, theme_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

## DQ-007 — Duplicate Game-Keyword Relationships

**Severity:** Critical

```sql
SELECT game_id, keyword_id, COUNT(*) AS duplicate_count
FROM game_keywords
GROUP BY game_id, keyword_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

## DQ-008 — Duplicate Game-Mode Relationships

**Severity:** Critical

```sql
SELECT game_id, game_mode_id, COUNT(*) AS duplicate_count
FROM game_modes_bridge
GROUP BY game_id, game_mode_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

## DQ-009 — Duplicate Game-Player Perspective Relationships

**Severity:** Critical

```sql
SELECT game_id, player_perspective_id, COUNT(*) AS duplicate_count
FROM game_player_perspectives
GROUP BY game_id, player_perspective_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

## DQ-010 — Duplicate Game-Platform Relationships

**Severity:** Critical

```sql
SELECT game_id, platform_id, COUNT(*) AS duplicate_count
FROM game_platforms
GROUP BY game_id, platform_id
HAVING COUNT(*) > 1;
```

**Expected Result:** 0 rows.

---

# 6. Foreign Key Integrity Checks

## DQ-011 — Orphaned Game Type References

**Severity:** Critical

```sql
SELECT g.*
FROM games g
LEFT JOIN game_types gt
    ON g.game_type_id = gt.game_type_id
WHERE g.game_type_id IS NOT NULL
  AND gt.game_type_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-012 — Orphaned Game Status References

**Severity:** Critical

```sql
SELECT g.*
FROM games g
LEFT JOIN game_statuses gs
    ON g.game_status_id = gs.game_status_id
WHERE g.game_status_id IS NOT NULL
  AND gs.game_status_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-013 — Orphaned Game IDs in Bridge Tables

**Severity:** Critical

```sql
SELECT 'game_genres' AS table_name, gg.game_id
FROM game_genres gg
LEFT JOIN games g ON gg.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'game_themes', gt.game_id
FROM game_themes gt
LEFT JOIN games g ON gt.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'game_keywords', gk.game_id
FROM game_keywords gk
LEFT JOIN games g ON gk.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'game_modes_bridge', gmb.game_id
FROM game_modes_bridge gmb
LEFT JOIN games g ON gmb.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'game_player_perspectives', gpp.game_id
FROM game_player_perspectives gpp
LEFT JOIN games g ON gpp.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'game_platforms', gp.game_id
FROM game_platforms gp
LEFT JOIN games g ON gp.game_id = g.game_id
WHERE g.game_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-014 — Orphaned Lookup IDs in Bridge Tables

**Severity:** Critical

```sql
SELECT 'game_genres' AS table_name, gg.genre_id AS missing_id
FROM game_genres gg
LEFT JOIN genres ge ON gg.genre_id = ge.genre_id
WHERE ge.genre_id IS NULL

UNION ALL

SELECT 'game_themes', gt.theme_id
FROM game_themes gt
LEFT JOIN themes th ON gt.theme_id = th.theme_id
WHERE th.theme_id IS NULL

UNION ALL

SELECT 'game_keywords', gk.keyword_id
FROM game_keywords gk
LEFT JOIN keywords kw ON gk.keyword_id = kw.keyword_id
WHERE kw.keyword_id IS NULL

UNION ALL

SELECT 'game_modes_bridge', gmb.game_mode_id
FROM game_modes_bridge gmb
LEFT JOIN game_modes gm ON gmb.game_mode_id = gm.game_mode_id
WHERE gm.game_mode_id IS NULL

UNION ALL

SELECT 'game_player_perspectives', gpp.player_perspective_id
FROM game_player_perspectives gpp
LEFT JOIN player_perspectives pp ON gpp.player_perspective_id = pp.player_perspective_id
WHERE pp.player_perspective_id IS NULL

UNION ALL

SELECT 'game_platforms', gp.platform_id
FROM game_platforms gp
LEFT JOIN platforms p ON gp.platform_id = p.platform_id
WHERE p.platform_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-015 — Orphaned Platform Lookup References

**Severity:** Critical

```sql
SELECT 'platform_family_id' AS reference_type, p.platform_id, p.platform_family_id AS missing_id
FROM platforms p
LEFT JOIN platform_families pf
    ON p.platform_family_id = pf.platform_family_id
WHERE p.platform_family_id IS NOT NULL
  AND pf.platform_family_id IS NULL

UNION ALL

SELECT 'platform_type_id', p.platform_id, p.platform_type_id
FROM platforms p
LEFT JOIN platform_types pt
    ON p.platform_type_id = pt.platform_type_id
WHERE p.platform_type_id IS NOT NULL
  AND pt.platform_type_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-016 — Orphaned Company References

**Severity:** Critical

```sql
SELECT 'missing_game' AS issue_type, ic.involved_company_id, ic.game_id, ic.company_id
FROM involved_companies ic
LEFT JOIN games g
    ON ic.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'missing_company', ic.involved_company_id, ic.game_id, ic.company_id
FROM involved_companies ic
LEFT JOIN companies c
    ON ic.company_id = c.company_id
WHERE c.company_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-017 — Orphaned Release Date References

**Severity:** Critical

```sql
SELECT 'missing_game' AS issue_type, rd.release_date_id, rd.game_id AS missing_id
FROM release_dates rd
LEFT JOIN games g
    ON rd.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'missing_platform', rd.release_date_id, rd.platform_id
FROM release_dates rd
LEFT JOIN platforms p
    ON rd.platform_id = p.platform_id
WHERE rd.platform_id IS NOT NULL
  AND p.platform_id IS NULL

UNION ALL

SELECT 'missing_date_format', rd.release_date_id, rd.date_format_id
FROM release_dates rd
LEFT JOIN date_formats df
    ON rd.date_format_id = df.date_format_id
WHERE rd.date_format_id IS NOT NULL
  AND df.date_format_id IS NULL

UNION ALL

SELECT 'missing_release_region', rd.release_date_id, rd.release_date_region_id
FROM release_dates rd
LEFT JOIN release_date_regions rdr
    ON rd.release_date_region_id = rdr.release_date_region_id
WHERE rd.release_date_region_id IS NOT NULL
  AND rdr.release_date_region_id IS NULL

UNION ALL

SELECT 'missing_release_status', rd.release_date_id, rd.release_date_status_id
FROM release_dates rd
LEFT JOIN release_date_statuses rds
    ON rd.release_date_status_id = rds.release_date_status_id
WHERE rd.release_date_status_id IS NOT NULL
  AND rds.release_date_status_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-018 — Orphaned Media and Website References

**Severity:** Critical

```sql
SELECT 'covers_missing_game' AS issue_type, c.cover_id AS record_id, c.game_id AS missing_id
FROM covers c
LEFT JOIN games g
    ON c.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'screenshots_missing_game', s.screenshot_id, s.game_id
FROM screenshots s
LEFT JOIN games g
    ON s.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'websites_missing_game', w.website_id, w.game_id
FROM websites w
LEFT JOIN games g
    ON w.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'websites_missing_type', w.website_id, w.website_type_id
FROM websites w
LEFT JOIN website_types wt
    ON w.website_type_id = wt.website_type_id
WHERE w.website_type_id IS NOT NULL
  AND wt.website_type_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-019 — Orphaned External Game References

**Severity:** Critical

```sql
SELECT 'external_games_missing_game' AS issue_type, eg.external_game_id AS record_id, eg.game_id AS missing_id
FROM external_games eg
LEFT JOIN games g
    ON eg.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'external_games_missing_source', eg.external_game_id, eg.external_game_source_id
FROM external_games eg
LEFT JOIN external_game_sources egs
    ON eg.external_game_source_id = egs.external_game_source_id
WHERE eg.external_game_source_id IS NOT NULL
  AND egs.external_game_source_id IS NULL

UNION ALL

SELECT 'external_games_missing_release_format', eg.external_game_id, eg.game_release_format_id
FROM external_games eg
LEFT JOIN game_release_formats grf
    ON eg.game_release_format_id = grf.game_release_format_id
WHERE eg.game_release_format_id IS NOT NULL
  AND grf.game_release_format_id IS NULL

UNION ALL

SELECT 'external_games_missing_platform', eg.external_game_id, eg.platform_id
FROM external_games eg
LEFT JOIN platforms p
    ON eg.platform_id = p.platform_id
WHERE eg.platform_id IS NOT NULL
  AND p.platform_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-020 — Orphaned Multiplayer References

**Severity:** Critical

```sql
SELECT 'multiplayer_missing_game' AS issue_type, mm.multiplayer_mode_id AS record_id, mm.game_id AS missing_id
FROM multiplayer_modes mm
LEFT JOIN games g
    ON mm.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'multiplayer_missing_platform', mm.multiplayer_mode_id, mm.platform_id
FROM multiplayer_modes mm
LEFT JOIN platforms p
    ON mm.platform_id = p.platform_id
WHERE mm.platform_id IS NOT NULL
  AND p.platform_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-021 — Orphaned Time-to-Beat References

**Severity:** Critical

```sql
SELECT gttb.*
FROM game_time_to_beats gttb
LEFT JOIN games g
    ON gttb.game_id = g.game_id
WHERE g.game_id IS NULL;
```

**Expected Result:** 0 rows.

---

## DQ-022 — Orphaned Popularity References

**Severity:** Critical

```sql
SELECT 'popularity_missing_game' AS issue_type, pp.popularity_primitive_id AS record_id, pp.game_id AS missing_id
FROM popularity_primitives pp
LEFT JOIN games g
    ON pp.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'popularity_missing_type', pp.popularity_primitive_id, pp.popularity_type_id
FROM popularity_primitives pp
LEFT JOIN popularity_types pt
    ON pp.popularity_type_id = pt.popularity_type_id
WHERE pp.popularity_type_id IS NOT NULL
  AND pt.popularity_type_id IS NULL

UNION ALL

SELECT 'popularity_missing_source', pp.popularity_primitive_id, pp.external_popularity_source_id
FROM popularity_primitives pp
LEFT JOIN external_game_sources egs
    ON pp.external_popularity_source_id = egs.external_game_source_id
WHERE pp.external_popularity_source_id IS NOT NULL
  AND egs.external_game_source_id IS NULL;
```

**Expected Result:** 0 rows.

---

# 7. Required Field Checks

## DQ-023 — Games Missing Required Names

**Purpose:** Every usable game record should have a game name.

**Severity:** Critical

```sql
SELECT *
FROM games
WHERE name IS NULL
   OR TRIM(name) = '';
```

**Expected Result:** 0 rows for the final analytics-ready catalog.

---

## DQ-024 — Empty Lookup Names

**Purpose:** Lookup tables should have readable labels.

**Severity:** High

```sql
SELECT 'game_types' AS table_name, game_type_id AS id_value
FROM game_types
WHERE type_name IS NULL OR TRIM(type_name) = ''

UNION ALL

SELECT 'game_statuses', game_status_id
FROM game_statuses
WHERE status_name IS NULL OR TRIM(status_name) = ''

UNION ALL

SELECT 'genres', genre_id
FROM genres
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'themes', theme_id
FROM themes
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'keywords', keyword_id
FROM keywords
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'game_modes', game_mode_id
FROM game_modes
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'player_perspectives', player_perspective_id
FROM player_perspectives
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'platforms', platform_id
FROM platforms
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'platform_families', platform_family_id
FROM platform_families
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'platform_types', platform_type_id
FROM platform_types
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'companies', company_id
FROM companies
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'website_types', website_type_id
FROM website_types
WHERE type_name IS NULL OR TRIM(type_name) = ''

UNION ALL

SELECT 'external_game_sources', external_game_source_id
FROM external_game_sources
WHERE source_name IS NULL OR TRIM(source_name) = ''

UNION ALL

SELECT 'game_release_formats', game_release_format_id
FROM game_release_formats
WHERE format_name IS NULL OR TRIM(format_name) = ''

UNION ALL

SELECT 'popularity_types', popularity_type_id
FROM popularity_types
WHERE name IS NULL OR TRIM(name) = '';
```

**Expected Result:** 0 rows.

---

# 8. Boolean Value Checks

## DQ-025 — Involved Company Boolean Flags

**Severity:** High

```sql
SELECT *
FROM involved_companies
WHERE (developer IS NOT NULL AND developer NOT IN (0, 1))
   OR (publisher IS NOT NULL AND publisher NOT IN (0, 1))
   OR (porting IS NOT NULL AND porting NOT IN (0, 1))
   OR (supporting IS NOT NULL AND supporting NOT IN (0, 1));
```

**Expected Result:** 0 rows.

---

## DQ-026 — Website Trusted Boolean

**Severity:** High

```sql
SELECT *
FROM websites
WHERE trusted IS NOT NULL
  AND trusted NOT IN (0, 1);
```

**Expected Result:** 0 rows.

---

## DQ-027 — Multiplayer Boolean Flags

**Severity:** High

```sql
SELECT *
FROM multiplayer_modes
WHERE (campaign_coop IS NOT NULL AND campaign_coop NOT IN (0, 1))
   OR (offline_coop IS NOT NULL AND offline_coop NOT IN (0, 1))
   OR (online_coop IS NOT NULL AND online_coop NOT IN (0, 1))
   OR (split_screen IS NOT NULL AND split_screen NOT IN (0, 1));
```

**Expected Result:** 0 rows.

---

# 9. Rating and Count Range Checks

## DQ-028 — Rating Range Check

**Purpose:** Ratings should be scores from 0 to 100.

**Severity:** High

```sql
SELECT *
FROM games
WHERE (rating IS NOT NULL AND (rating < 0 OR rating > 100))
   OR (total_rating IS NOT NULL AND (total_rating < 0 OR total_rating > 100));
```

**Expected Result:** 0 rows.

---

## DQ-029 — Rating Count Non-Negative Check

**Severity:** High

```sql
SELECT *
FROM games
WHERE (rating_count IS NOT NULL AND rating_count < 0)
   OR (total_rating_count IS NOT NULL AND total_rating_count < 0);
```

**Expected Result:** 0 rows.

---

## DQ-030 — Rating Without Rating Count

**Purpose:** Identify records where rating exists but count is missing.

**Severity:** Medium

```sql
SELECT game_id, name, rating, rating_count, total_rating, total_rating_count
FROM games
WHERE (rating IS NOT NULL AND rating_count IS NULL)
   OR (total_rating IS NOT NULL AND total_rating_count IS NULL);
```

**Expected Result:**

Ideally 0 rows. If rows appear, document how these games will be handled in rating-based analysis.

---

## DQ-031 — High-Rated Modeling Eligibility Summary

**Purpose:** Count how many games are eligible for the predictive modeling target.

**Severity:** Medium

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating,
    SUM(CASE WHEN total_rating IS NOT NULL AND total_rating_count >= 10 THEN 1 ELSE 0 END) AS modeling_eligible_games,
    SUM(CASE WHEN total_rating >= 80 AND total_rating_count >= 10 THEN 1 ELSE 0 END) AS highly_rated_games,
    SUM(CASE WHEN total_rating < 80 AND total_rating_count >= 10 THEN 1 ELSE 0 END) AS lower_rated_games
FROM games;
```

**Expected Result:**

This is a summary check. It should return 1 row. Use the result to document modeling sample size and class balance.

---

# 10. Date and Time Checks

## DQ-032 — Release Year Range Check

**Severity:** Medium

```sql
SELECT *
FROM games
WHERE release_year IS NOT NULL
  AND (release_year < 1950 OR release_year > CAST(strftime('%Y', 'now') AS INTEGER) + 5);
```

**Expected Result:**

0 rows ideally. Future release years may be valid if the game is upcoming; investigate rather than automatically delete.

---

## DQ-033 — Release Dates Year Range Check

**Severity:** Medium

```sql
SELECT *
FROM release_dates
WHERE release_year IS NOT NULL
  AND (release_year < 1950 OR release_year > CAST(strftime('%Y', 'now') AS INTEGER) + 5);
```

**Expected Result:**

0 rows ideally. Investigate future records before excluding.

---

## DQ-034 — Release Month Validity

**Severity:** High

```sql
SELECT *
FROM release_dates
WHERE release_month IS NOT NULL
  AND (release_month < 1 OR release_month > 12);
```

**Expected Result:** 0 rows.

---

## DQ-035 — Release Day Validity

**Severity:** High

```sql
SELECT *
FROM release_dates
WHERE release_day IS NOT NULL
  AND (release_day < 1 OR release_day > 31);
```

**Expected Result:** 0 rows.

---

## DQ-036 — Impossible Calendar Dates

**Purpose:** Catch impossible combinations like February 31.

**Severity:** Medium

```sql
SELECT *
FROM release_dates
WHERE date_iso IS NOT NULL
  AND date(date_iso) IS NULL;
```

**Expected Result:** 0 rows.

**Note:** This only works if `date_iso` follows a SQLite-readable date format such as `YYYY-MM-DD`.

---

## DQ-037 — Timestamp Conversion Consistency: Games

**Purpose:** Compare `first_release_date` to `first_release_date_iso`.

**Severity:** Medium

```sql
SELECT
    game_id,
    name,
    first_release_date,
    first_release_date_iso,
    date(first_release_date, 'unixepoch') AS converted_date
FROM games
WHERE first_release_date IS NOT NULL
  AND first_release_date_iso IS NOT NULL
  AND date(first_release_date, 'unixepoch') <> first_release_date_iso;
```

**Expected Result:** 0 rows.

---

## DQ-038 — Timestamp Conversion Consistency: Companies

**Severity:** Medium

```sql
SELECT
    company_id,
    name,
    start_date,
    start_date_iso,
    date(start_date, 'unixepoch') AS converted_date
FROM companies
WHERE start_date IS NOT NULL
  AND start_date_iso IS NOT NULL
  AND date(start_date, 'unixepoch') <> start_date_iso;
```

**Expected Result:** 0 rows.

**Documented Exception:** Company `9254` has a source timestamp that cannot be
represented as a Python date. This query excludes it because its
`start_date_iso` is `NULL`. The raw timestamp remains available for audit.

---

## DQ-039 — Timestamp Conversion Consistency: Release Dates

**Severity:** Low

```sql
SELECT
    release_date_id,
    date_timestamp,
    date_iso,
    date(date_timestamp, 'unixepoch') AS converted_date
FROM release_dates
WHERE date_timestamp IS NOT NULL
  AND date_iso IS NOT NULL
  AND date(date_timestamp, 'unixepoch') <> date_iso;
```

**Expected Result:** 0 rows.

---

# 11. Media and URL Checks

## DQ-040 — Cover Image URL or Image ID Missing

**Severity:** Low

```sql
SELECT *
FROM covers
WHERE (image_id IS NULL OR TRIM(image_id) = '')
  AND (url IS NULL OR TRIM(url) = '');
```

**Expected Result:**

0 rows if covers are intended for UI display. If rows appear, they can be kept but will not be useful visually.

---

## DQ-041 — Screenshot URL or Image ID Missing

**Severity:** Low

```sql
SELECT *
FROM screenshots
WHERE (image_id IS NULL OR TRIM(image_id) = '')
  AND (url IS NULL OR TRIM(url) = '');
```

**Expected Result:**

0 rows if screenshots are intended for UI display.

---

## DQ-042 — Negative Image Dimensions

**Severity:** Medium

```sql
SELECT 'covers' AS table_name, cover_id AS record_id, width, height
FROM covers
WHERE (width IS NOT NULL AND width < 0)
   OR (height IS NOT NULL AND height < 0)

UNION ALL

SELECT 'screenshots', screenshot_id, width, height
FROM screenshots
WHERE (width IS NOT NULL AND width < 0)
   OR (height IS NOT NULL AND height < 0);
```

**Expected Result:** 0 rows.

---

## DQ-043 — Website URL Missing

**Severity:** Medium

```sql
SELECT *
FROM websites
WHERE url IS NULL
   OR TRIM(url) = '';
```

**Expected Result:**

0 rows ideally. Website records without URLs are not useful for UI or navigation.

---

## DQ-044 — External Game URL and UID Both Missing

**Severity:** Medium

```sql
SELECT *
FROM external_games
WHERE (uid IS NULL OR TRIM(uid) = '')
  AND (url IS NULL OR TRIM(url) = '');
```

**Expected Result:**

0 rows ideally. If both fields are missing, the external mapping is difficult to use.

---

# 12. Multiplayer and Time-to-Beat Checks

## DQ-045 — Time-to-Beat Non-Negative Values

**Severity:** High

```sql
SELECT *
FROM game_time_to_beats
WHERE (hastily IS NOT NULL AND hastily < 0)
   OR (normally IS NOT NULL AND normally < 0)
   OR (completely IS NOT NULL AND completely < 0)
   OR (count IS NOT NULL AND count < 0);
```

**Expected Result:** 0 rows.

---

## DQ-046 — Time-to-Beat Logical Order

**Purpose:** Usually, quick completion should be less than or equal to normal completion, and normal completion should be less than or equal to completionist time.

**Severity:** Low

```sql
SELECT *
FROM game_time_to_beats
WHERE hastily IS NOT NULL
  AND normally IS NOT NULL
  AND hastily > normally

UNION ALL

SELECT *
FROM game_time_to_beats
WHERE normally IS NOT NULL
  AND completely IS NOT NULL
  AND normally > completely;
```

**Expected Result:**

This is a heuristic warning, not a required quality gate. The current database
returns 60 rows. IGDB stores separate average estimates, so their order is not
guaranteed for every game. Retain the source values and avoid silently
reordering them.

---

## DQ-047 — Multiplayer Records With No Multiplayer Flags

**Purpose:** Identify multiplayer records that do not actually contain any known support flag.

**Severity:** Low

```sql
SELECT *
FROM multiplayer_modes
WHERE campaign_coop IS NULL
  AND drop_in IS NULL
  AND lan_coop IS NULL
  AND offline_coop IS NULL
  AND online_coop IS NULL
  AND split_screen IS NULL
  AND split_screen_online IS NULL
  AND offline_coop_max IS NULL
  AND offline_max IS NULL
  AND online_coop_max IS NULL
  AND online_max IS NULL;
```

**Expected Result:**

Ideally 0 rows. If rows appear, these records may not be useful for recommendation filters.

---

# 13. Popularity Checks

## DQ-048 — Popularity Value Missing

**Severity:** Medium

```sql
SELECT *
FROM popularity_primitives
WHERE value IS NULL;
```

**Expected Result:**

0 rows ideally. Popularity records without values are not analytically useful.

---

## DQ-049 — Popularity Value Negative

**Severity:** Medium

```sql
SELECT *
FROM popularity_primitives
WHERE value IS NOT NULL
  AND value < 0;
```

**Expected Result:**

0 rows unless a specific popularity type allows negative values. Document any exceptions.

---

## DQ-050 — Popularity Type Missing Name

**Severity:** High

```sql
SELECT *
FROM popularity_types
WHERE name IS NULL
   OR TRIM(name) = '';
```

**Expected Result:** 0 rows.

---

## DQ-051 — Popularity Snapshot Timestamp Missing

**Severity:** Low

```sql
SELECT *
FROM popularity_primitives
WHERE calculated_at IS NULL;
```

**Expected Result:**

Ideally 0 rows if popularity snapshots are time-sensitive. If missing, the popularity value may still be usable but not for trend analysis.

---

# 14. Analytics-Ready Completeness Checks

## DQ-052 — Game Classification Coverage

**Purpose:** Measure how many games have genres, themes, and keywords.

**Severity:** Summary

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN gg.game_id IS NOT NULL THEN 1 ELSE 0 END) AS games_with_genre,
    SUM(CASE WHEN gt.game_id IS NOT NULL THEN 1 ELSE 0 END) AS games_with_theme,
    SUM(CASE WHEN gk.game_id IS NOT NULL THEN 1 ELSE 0 END) AS games_with_keyword
FROM games g
LEFT JOIN (SELECT DISTINCT game_id FROM game_genres) gg
    ON g.game_id = gg.game_id
LEFT JOIN (SELECT DISTINCT game_id FROM game_themes) gt
    ON g.game_id = gt.game_id
LEFT JOIN (SELECT DISTINCT game_id FROM game_keywords) gk
    ON g.game_id = gk.game_id;
```

**Expected Result:**

This is a summary check. Use it to report metadata completeness.

---

## DQ-053 — Platform Coverage

**Purpose:** Identify games with no platform relationship.

**Severity:** High for recommendation system

```sql
SELECT g.*
FROM games g
LEFT JOIN game_platforms gp
    ON g.game_id = gp.game_id
WHERE gp.game_id IS NULL;
```

**Expected Result:**

Ideally 0 rows for recommendation-ready games. Some raw catalog records may have missing platform data.

---

## DQ-054 — Release Year Coverage

**Purpose:** Identify games missing release year.

**Severity:** Medium

```sql
SELECT *
FROM games
WHERE release_year IS NULL;
```

**Expected Result:**

Not necessarily 0 rows. Document the percentage missing because release-year coverage matters for descriptive and predictive analytics.

---

## DQ-055 — Company Coverage

**Purpose:** Identify games without involved company data.

**Severity:** Medium

```sql
SELECT g.*
FROM games g
LEFT JOIN involved_companies ic
    ON g.game_id = ic.game_id
WHERE ic.game_id IS NULL;
```

**Expected Result:**

Not necessarily 0 rows. Document missingness before developer/publisher analysis.

---

## DQ-056 — RAG Text Coverage

**Purpose:** Identify games with no useful text description.

**Severity:** High for RAG

```sql
SELECT *
FROM games
WHERE (summary IS NULL OR TRIM(summary) = '')
  AND (storyline IS NULL OR TRIM(storyline) = '');
```

**Expected Result:**

These games may stay in the relational database, but they are weak candidates for RAG embeddings unless enriched by genres, themes, keywords, and other metadata.

---

## DQ-057 — Rating Coverage Summary

**Purpose:** Measure completeness of rating data.

**Severity:** Summary

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN rating IS NOT NULL THEN 1 ELSE 0 END) AS games_with_rating,
    SUM(CASE WHEN rating_count IS NOT NULL THEN 1 ELSE 0 END) AS games_with_rating_count,
    SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating,
    SUM(CASE WHEN total_rating_count IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating_count,
    ROUND(100.0 * SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_with_total_rating
FROM games;
```

**Expected Result:**

This is a summary check. Use it in the final report to explain rating missingness.

---

# 15. Recommendation-Ready Checks

## DQ-058 — Recommendation-Ready Game Count

**Purpose:** Count games usable for recommendation MVP.

**Severity:** Summary

```sql
SELECT
    COUNT(DISTINCT g.game_id) AS recommendation_ready_games
FROM games g
JOIN game_platforms gp
    ON g.game_id = gp.game_id
LEFT JOIN game_types gt
    ON g.game_type_id = gt.game_type_id
LEFT JOIN game_statuses gs
    ON g.game_status_id = gs.game_status_id
WHERE g.name IS NOT NULL
  AND TRIM(g.name) <> ''
  AND (
        g.summary IS NOT NULL
        OR g.storyline IS NOT NULL
        OR EXISTS (SELECT 1 FROM game_genres gg WHERE gg.game_id = g.game_id)
        OR EXISTS (SELECT 1 FROM game_themes th WHERE th.game_id = g.game_id)
        OR EXISTS (SELECT 1 FROM game_keywords kw WHERE kw.game_id = g.game_id)
      );
```

**Expected Result:**

This is a summary check. It should return a meaningful number of games for the app.

---

## DQ-059 — Platform-Constrained Recommendation Coverage

**Purpose:** Confirm how many games are available per platform.

**Severity:** Summary

```sql
SELECT
    p.platform_id,
    p.name AS platform_name,
    p.abbreviation,
    COUNT(DISTINCT gp.game_id) AS game_count
FROM platforms p
LEFT JOIN game_platforms gp
    ON p.platform_id = gp.platform_id
GROUP BY p.platform_id, p.name, p.abbreviation
ORDER BY game_count DESC;
```

**Expected Result:**

This is a summary check. Use it to decide which platforms are strong enough for dashboard filters.

---

## DQ-060 — Games With No Recommendation Metadata

**Purpose:** Identify games that have no genre, theme, keyword, platform, summary, or storyline.

**Severity:** High for recommendation system

```sql
SELECT g.*
FROM games g
LEFT JOIN game_genres gg
    ON g.game_id = gg.game_id
LEFT JOIN game_themes gt
    ON g.game_id = gt.game_id
LEFT JOIN game_keywords gk
    ON g.game_id = gk.game_id
LEFT JOIN game_platforms gp
    ON g.game_id = gp.game_id
WHERE gg.game_id IS NULL
  AND gt.game_id IS NULL
  AND gk.game_id IS NULL
  AND gp.game_id IS NULL
  AND (g.summary IS NULL OR TRIM(g.summary) = '')
  AND (g.storyline IS NULL OR TRIM(g.storyline) = '');
```

**Expected Result:**

Ideally 0 rows for recommendation-ready data. These records are very weak for discovery and RAG.

---

# 16. Dashboard-Ready Checks

## DQ-061 — Dashboard Filter Coverage

**Purpose:** Check whether key dashboard filters have enough data.

**Severity:** Summary

```sql
SELECT 'release_year' AS filter_name, COUNT(DISTINCT release_year) AS distinct_values
FROM games
WHERE release_year IS NOT NULL

UNION ALL

SELECT 'platforms', COUNT(DISTINCT platform_id)
FROM platforms

UNION ALL

SELECT 'genres', COUNT(DISTINCT genre_id)
FROM genres

UNION ALL

SELECT 'themes', COUNT(DISTINCT theme_id)
FROM themes

UNION ALL

SELECT 'companies', COUNT(DISTINCT company_id)
FROM companies

UNION ALL

SELECT 'game_types', COUNT(DISTINCT game_type_id)
FROM game_types

UNION ALL

SELECT 'game_statuses', COUNT(DISTINCT game_status_id)
FROM game_statuses;
```

**Expected Result:**

This is a summary check. Use it to confirm dashboard filters are useful.

---

## DQ-062 — Rating Dashboard Eligibility

**Purpose:** Count games eligible for rating charts.

**Severity:** Summary

```sql
SELECT
    COUNT(*) AS rating_dashboard_eligible_games
FROM games
WHERE total_rating IS NOT NULL
  AND total_rating_count >= 10;
```

**Expected Result:**

This is a summary check. Use it to document the sample size behind rating dashboards.

---

## DQ-063 — Hidden Gem Candidate Pool

**Purpose:** Count potential hidden gem candidates using the project’s first-pass rule.

**Severity:** Summary

```sql
WITH ranked_games AS (
    SELECT
        game_id,
        total_rating,
        total_rating_count,
        NTILE(10) OVER (ORDER BY total_rating_count) AS rating_count_decile
    FROM games
    WHERE total_rating IS NOT NULL
      AND total_rating_count IS NOT NULL
)
SELECT
    COUNT(*) AS hidden_gem_candidate_count
FROM ranked_games
WHERE total_rating >= 80
  AND total_rating_count >= 10
  AND rating_count_decile <= 4;
```

**Expected Result:**

This is a summary check using the bottom 40% of `total_rating_count` as the
sample-relative visibility threshold.

**Important Note:**

The current 500-game sample was sorted by `total_rating_count` descending during
extraction. This makes it popularity-biased and unsuitable for a defensible
final hidden-gem analysis. Before final analysis, extract a larger and less
popularity-biased catalog. If `popularity_primitives` are used, normalize within
each popularity type and source before combining signals.

---

# 17. RAG Grounding Checks

## DQ-064 — RAG Profile Required Data

**Purpose:** Identify games that can support useful RAG profile construction.

**Severity:** Summary

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE
        WHEN name IS NOT NULL
         AND TRIM(name) <> ''
         AND (
              summary IS NOT NULL
              OR storyline IS NOT NULL
              OR EXISTS (SELECT 1 FROM game_genres gg WHERE gg.game_id = games.game_id)
              OR EXISTS (SELECT 1 FROM game_themes gt WHERE gt.game_id = games.game_id)
              OR EXISTS (SELECT 1 FROM game_keywords gk WHERE gk.game_id = games.game_id)
         )
        THEN 1 ELSE 0 END
    ) AS rag_profile_ready_games
FROM games;
```

**Expected Result:**

This is a summary check. Use it to document how many games can be embedded.

---

## DQ-065 — RAG Grounding Attribute Coverage

**Purpose:** Measure how often key grounding attributes are available.

**Severity:** Summary

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN summary IS NOT NULL AND TRIM(summary) <> '' THEN 1 ELSE 0 END) AS with_summary,
    SUM(CASE WHEN storyline IS NOT NULL AND TRIM(storyline) <> '' THEN 1 ELSE 0 END) AS with_storyline,
    SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) AS with_total_rating,
    SUM(CASE WHEN release_year IS NOT NULL THEN 1 ELSE 0 END) AS with_release_year,
    SUM(CASE WHEN EXISTS (SELECT 1 FROM game_platforms gp WHERE gp.game_id = games.game_id) THEN 1 ELSE 0 END) AS with_platforms,
    SUM(CASE WHEN EXISTS (SELECT 1 FROM involved_companies ic WHERE ic.game_id = games.game_id) THEN 1 ELSE 0 END) AS with_companies
FROM games;
```

**Expected Result:**

This is a summary check. Use it to decide which attributes are safe to mention in chatbot responses.

---

# 18. Out-of-Scope Data Checks

## DQ-066 — Confirm No Price Tables Are Present

**Purpose:** Prevent unsupported claims about prices.

**Severity:** Low

```sql
SELECT name AS table_name
FROM sqlite_master
WHERE type = 'table'
  AND (
      LOWER(name) LIKE '%price%'
      OR LOWER(name) LIKE '%sale%'
      OR LOWER(name) LIKE '%discount%'
  );
```

**Expected Result:**

0 rows unless future price tables are intentionally added.

---

## DQ-067 — Confirm No User Account Tables Are Present

**Purpose:** Prevent unsupported claims about persistent user profiles.

**Severity:** Low

```sql
SELECT name AS table_name
FROM sqlite_master
WHERE type = 'table'
  AND (
      LOWER(name) LIKE '%user%'
      OR LOWER(name) LIKE '%account%'
      OR LOWER(name) LIKE '%profile%'
      OR LOWER(name) LIKE '%feedback%'
  );
```

**Expected Result:**

0 rows unless future user-profile tables are intentionally added.

---

# 19. Final Data Quality Scorecard

Use this query style to create a simple project scorecard.

## DQ-068 — Integrity Scorecard

**Purpose:** Summarize important data quality results in one view.

**Severity:** Summary

```sql
SELECT 'games_missing_name' AS check_name, COUNT(*) AS failing_rows
FROM games
WHERE name IS NULL OR TRIM(name) = ''

UNION ALL

SELECT 'duplicate_game_genres', COUNT(*)
FROM (
    SELECT game_id, genre_id
    FROM game_genres
    GROUP BY game_id, genre_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT 'orphan_game_genres_game_id', COUNT(*)
FROM game_genres gg
LEFT JOIN games g ON gg.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'orphan_game_platforms_game_id', COUNT(*)
FROM game_platforms gp
LEFT JOIN games g ON gp.game_id = g.game_id
WHERE g.game_id IS NULL

UNION ALL

SELECT 'ratings_out_of_range', COUNT(*)
FROM games
WHERE (rating IS NOT NULL AND (rating < 0 OR rating > 100))
   OR (total_rating IS NOT NULL AND (total_rating < 0 OR total_rating > 100))

UNION ALL

SELECT 'invalid_boolean_involved_companies', COUNT(*)
FROM involved_companies
WHERE (developer IS NOT NULL AND developer NOT IN (0, 1))
   OR (publisher IS NOT NULL AND publisher NOT IN (0, 1))
   OR (porting IS NOT NULL AND porting NOT IN (0, 1))
   OR (supporting IS NOT NULL AND supporting NOT IN (0, 1))

UNION ALL

SELECT 'invalid_release_month', COUNT(*)
FROM release_dates
WHERE release_month IS NOT NULL
  AND (release_month < 1 OR release_month > 12)

UNION ALL

SELECT 'invalid_release_day', COUNT(*)
FROM release_dates
WHERE release_day IS NOT NULL
  AND (release_day < 1 OR release_day > 31);
```

**Expected Result:**

Each `failing_rows` value should be `0` for critical checks.

---

# 20. Suggested Reporting Table

After running checks, record results like this:

| Check ID | Check Name                         | Severity | Expected Result        | Actual Result | Status | Notes                       |
| -------- | ---------------------------------- | -------- | ---------------------- | ------------: | ------ | --------------------------- |
| DQ-001   | Expected tables exist              | Critical | All ERD tables present |           TBD | TBD    | Compare against schema.     |
| DQ-003   | Null primary keys                  | Critical | 0 failing rows         |           TBD | TBD    | Required before analysis.   |
| DQ-013   | Orphaned game IDs in bridge tables | Critical | 0 failing rows         |           TBD | TBD    | Required before joins.      |
| DQ-028   | Rating range check                 | High     | 0 failing rows         |           TBD | TBD    | Needed for rating analysis. |
| DQ-056   | RAG text coverage                  | High     | Document missingness   |           TBD | TBD    | Affects chatbot quality.    |

Status values:

```text
PASS
FAIL
WARNING
DOCUMENTED EXCEPTION
NOT RUN
```

---

# 21. Recommended Quality Gates

Use these gates before moving to each project phase.

## Gate 1 — Database Build Complete

Required passing checks:

```text
DQ-001
DQ-002
DQ-003
DQ-004
DQ-005 to DQ-010
DQ-011 to DQ-022
```

## Gate 2 — Analytics Ready

Required passing or documented checks:

```text
DQ-023
DQ-024
DQ-028
DQ-029
DQ-032
DQ-033
DQ-034
DQ-035
DQ-052
DQ-053
DQ-054
DQ-057
```

## Gate 3 — Recommendation Ready

Required passing or documented checks:

```text
DQ-053
DQ-056
DQ-058
DQ-059
DQ-060
```

## Gate 4 — RAG Ready

Required passing or documented checks:

```text
DQ-056
DQ-064
DQ-065
```

## Gate 5 — Final Report Ready

Required:

```text
DQ-068 scorecard completed
All Critical checks pass
All High checks either pass or have documented exceptions
Missingness rates documented
Modeling sample size documented
RAG-ready game count documented
```

---

# 22. Important Notes

## Do Not Delete Data Automatically

Failing a data quality check does not always mean the row should be deleted.

Recommended process:

```text
1. Identify the issue.
2. Determine whether it is a true error, expected missingness, or acceptable exception.
3. Fix the ETL transformation if needed.
4. Document any exception.
5. Re-run the check.
```

## Missingness Is Not Always Bad

IGDB metadata can be incomplete. Missing summaries, storylines, ratings, covers, screenshots, or company information may be normal.

The important part is to:

```text
Document missingness.
Avoid unsupported claims.
Filter missing records only when required for a specific analysis.
```

## Foreign Key Integrity Is Non-Negotiable

For the clean relational database, foreign key integrity should be treated as critical.

Examples:

```text
No game_genres row should point to a missing game.
No game_platforms row should point to a missing platform.
No release_dates row should point to a missing game.
No involved_companies row should point to a missing company.
```

## Recommendation and RAG Require Extra Checks

A game may be valid in the database but weak for recommendation or RAG.

Example:

```text
A game with a name but no summary, storyline, genres, themes, keywords, platforms, or company data is technically valid but not useful for explainable discovery.
```

Such records should be flagged, not necessarily deleted.
