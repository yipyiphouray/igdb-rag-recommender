# IGDB Relational Database Business Rules

## Purpose

This document defines the business rules for the IGDB relational SQLite database used in the **IGDB Game Discovery & RAG Recommendation System**.

Business rules explain how the database should behave, how records should be interpreted, and how the data should be used for analytics, modeling, recommendations, and RAG outputs.

File location:

```text
docs/IGDB_ERD_BusinessRules.md
```

Related documentation files:

```text
docs/IGDB_ERD_Data_Dictionary.md
docs/IGDB_ERD_ValueMapping.md
docs/IGDB_DataQualityChecks.md
docs/IGDB_relational_ERD.md
```

---

# 1. Scope of the Database

## BR-001 — Database Purpose

The database exists to support game discovery, analytics, recommendation, and RAG-based explanation using IGDB metadata.

The database should support:

* Descriptive analytics: catalog composition, release trends, platform distribution, genre/theme distribution.
* Diagnostic analytics: rating differences, popularity versus rating, hidden-gem patterns, developer/publisher patterns.
* Predictive analytics: classification of high-rated games and user-game match scoring.
* Prescriptive analytics: recommendation ranking and filtering.
* RAG chatbot grounding: generating recommendations only from database-backed game records.

## BR-002 — Central Entity Rule

The `games` table is the central entity of the database.

Most analytical and recommendation outputs should start from `games` and join outward to supporting tables.

Core related tables include:

```text
game_types
game_statuses
genres
game_genres
themes
game_themes
keywords
game_keywords
game_modes
game_modes_bridge
player_perspectives
game_player_perspectives
platforms
game_platforms
companies
involved_companies
release_dates
```

## BR-003 — ERD Compliance Rule

Business rules must follow the current ERD.

The ERD organizes the database into:

```text
Core Catalog
Enrichment and Media
Release Date Lookups
```

Rules should not assume tables or columns that are not present in the ERD unless explicitly marked as future work.

---

# 2. Table Grain Rules

## BR-004 — Games Grain

Each row in `games` represents one IGDB game record.

The `game_id` must uniquely identify the game.

A game may have:

* Multiple genres.
* Multiple themes.
* Multiple keywords.
* Multiple platforms.
* Multiple involved companies.
* Multiple release date records.
* Multiple screenshots.
* Multiple websites.
* Multiple external game mappings.
* Multiple popularity primitives.

## BR-005 — Lookup Table Grain

Each lookup table should contain one row per lookup value.

Lookup tables include:

```text
game_types
game_statuses
genres
themes
keywords
game_modes
player_perspectives
platform_families
platform_types
date_formats
release_date_regions
release_date_statuses
website_types
external_game_sources
game_release_formats
popularity_types
```

`platforms` and `companies` are entity tables rather than simple controlled
vocabularies, although they are also used as join targets throughout the
database.

## BR-006 — Bridge Table Grain

Bridge tables represent many-to-many relationships.

Each bridge table should have one unique row per relationship pair.

Bridge tables include:

```text
game_genres
game_themes
game_keywords
game_modes_bridge
game_player_perspectives
game_platforms
```

Examples:

* One game can have many genres.
* One genre can classify many games.
* One game can be available on many platforms.
* One platform can host many games.

## BR-007 — Detail Table Grain

Detail tables represent event-like, source-specific, or relationship-specific records.

Detail tables include:

```text
involved_companies
release_dates
websites
external_games
multiplayer_modes
popularity_primitives
screenshots
```

Each row should be interpreted at its own grain:

| Table                   | Grain                                                                      |
| ----------------------- | -------------------------------------------------------------------------- |
| `involved_companies`    | One game-company relationship.                                             |
| `release_dates`         | One release-date record for a game, usually scoped by platform and region. |
| `websites`              | One website link for a game.                                               |
| `external_games`        | One external source/store/database mapping for a game.                     |
| `multiplayer_modes`     | One multiplayer support record for a game, usually scoped by platform.     |
| `popularity_primitives` | One popularity signal value for a game.                                    |
| `screenshots`           | One screenshot image for a game.                                           |

---

# 3. Game Inclusion and Exclusion Rules

## BR-008 — Minimum Game Record Rule

A game record is considered usable for the clean catalog if it has:

```text
game_id is not null
name is not null
```

Recommended SQL logic:

```sql
WHERE game_id IS NOT NULL
  AND name IS NOT NULL
  AND TRIM(name) <> ''
```

## BR-009 — Analytics-Ready Game Rule

A game is considered analytics-ready if it has enough metadata to support meaningful analysis.

Recommended minimum fields:

```text
game_id
name
release_year OR first_release_date_iso
at least one platform relationship OR at least one release date platform
at least one genre or theme when classification analysis is needed
```

Important note:

* Some valid IGDB records may have missing ratings, storylines, or summaries.
* Missing text fields should not automatically exclude a game from the database.
* Missing text fields may exclude a game from RAG-specific use.

## BR-010 — Main Game Recommendation Rule

For the MVP recommendation system, the system should prefer main games over DLCs, ports, packs, updates, and other non-main records.

Implementation:

```sql
JOIN game_types gt
  ON games.game_type_id = gt.game_type_id
```

Then filter or prioritize the relevant `type_name`.

Recommended logic:

```text
Prefer records where game type = Main Game.
Exclude or down-rank DLC, bundles, packs, updates, and editions unless the user explicitly asks for them.
```

Rationale:

* Users asking for game recommendations generally expect standalone playable games.
* DLCs and updates can confuse recommendation results if mixed with base games.

## BR-011 — Game Status Recommendation Rule

For general recommendations, the system should prefer games with evidence that
they have already been released.

Recommended logic:

```text
Require `games.first_release_date` to be on or before the recommendation date,
or require a qualifying `release_dates` row that is not in the future.

Exclude or down-rank games explicitly marked `Offline` or `Delisted` unless the
user asks for unavailable or historical titles.
```

Important distinction:

* In the current extract, `game_statuses` contains only `Offline` and
  `Delisted`, and 489 of 500 games have `game_status_id = NULL`.
* `NULL` must not automatically be interpreted as either released or
  unreleased.
* `Alpha`, `Beta`, `Early Access`, `Cancelled`, and `Full Release` are
  release-record statuses in `release_date_statuses` for the current schema.

## BR-012 — Missing Rating Rule

Games with missing ratings may remain in the database.

However:

* They should be excluded from rating-based analysis.
* They should not be labeled “highly rated.”
* They may still appear in RAG or exploratory search if other metadata is strong.

Recommended rating-based analysis filter:

```sql
WHERE total_rating IS NOT NULL
  AND total_rating_count IS NOT NULL
```

## BR-013 — Rating Reliability Rule

Rating-based analysis should use a minimum rating count threshold.

Recommended threshold:

```text
total_rating_count >= 10
```

Rationale:

* A game with a very high score but only one or two ratings may not be reliable.
* The threshold can be adjusted during analysis.

## BR-014 — High-Rated Game Rule

For predictive modeling and classification, a high-rated game is defined as:

```text
highly_rated = 1 if total_rating >= 80
highly_rated = 0 if total_rating < 80
```

Recommended additional reliability filter:

```text
total_rating_count >= 10
```

This rule follows the project proposal’s modeling direction.

---

# 4. Genre, Theme, Keyword, and Vibe Rules

## BR-015 — Genre Normalization Rule

Game genres must be stored in the `genres` lookup table and connected to games through `game_genres`.

Do not store genre arrays directly in the clean `games` table.

Correct structure:

```text
games
genres
game_genres
```

## BR-016 — Theme Normalization Rule

Game themes must be stored in the `themes` lookup table and connected to games through `game_themes`.

Correct structure:

```text
games
themes
game_themes
```

## BR-017 — Keyword Normalization Rule

Game keywords must be stored in the `keywords` lookup table and connected to games through `game_keywords`.

Correct structure:

```text
games
keywords
game_keywords
```

## BR-018 — Vibe Matching Rule

For natural-language recommendation prompts, the system should use a combination of:

```text
summary
storyline
genres
themes
keywords
player perspectives
game modes
platforms
```

Recommendation logic should not rely only on genre because user preferences are often expressed through mood, setting, tone, platform, and play style.

## BR-019 — Classification Availability Rule

A game may have zero, one, or many genres, themes, or keywords.

Rules:

* Do not delete a game only because it has no keywords.
* Do not delete a game only because it has no themes.
* For genre/theme-specific analytics, exclude games missing the relevant relationship.
* For RAG, games with richer classification metadata may be ranked more confidently.

## BR-020 — Bridge Table Duplicate Rule

Bridge tables must not contain duplicate relationship pairs.

Examples of invalid duplicates:

```text
same game_id + genre_id repeated in game_genres
same game_id + theme_id repeated in game_themes
same game_id + platform_id repeated in game_platforms
```

---

# 5. Platform Rules

## BR-021 — Platform Availability Rule

A game is considered available on a platform only if a row exists in `game_platforms` linking that `game_id` to that `platform_id`.

Correct join:

```sql
SELECT
    g.game_id,
    g.name,
    p.name AS platform_name
FROM games g
JOIN game_platforms gp
    ON g.game_id = gp.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id;
```

## BR-022 — Platform-Constrained Recommendation Rule

If a user asks for games on a specific platform, the recommendation system must only return games with a matching platform relationship.

Example:

```text
User asks: “Recommend cozy games on Nintendo Switch.”

System rule:
Only return games where platform_name = Nintendo Switch or another accepted Switch label.
```

## BR-023 — Platform Family Rule

If a user asks for a broad platform family, such as PlayStation, Xbox, or Nintendo, the system may use `platform_families`.

Example:

```text
PlayStation request → match platforms in the PlayStation platform family.
Xbox request → match platforms in the Xbox platform family.
Nintendo request → match platforms in the Nintendo platform family.
```

## BR-024 — Platform Type Rule

If a user asks for a broad platform type, the system may use `platform_types`.

Example:

```text
console games → platform_type = console
PC/computer games → platform_type = computer or operating system, depending on platform mapping
portable games → platform_type = portable console
```

## BR-025 — Platform Release Date Rule

Platform availability from `game_platforms` and platform-specific release timing from `release_dates` are related but not identical.

Rules:

* Use `game_platforms` to answer “is this game available on this platform?”
* Use `release_dates` to answer “when was this game released on this platform?”
* Do not assume the earliest game-level release date applies to every platform.

---

# 6. Company and Role Rules

## BR-026 — Involved Company Role Rule

The `involved_companies` table defines how companies are related to games.

A company can have one or more roles:

```text
developer
publisher
porting
supporting
```

Each role is stored as a boolean flag.

## BR-027 — Developer Analysis Rule

Developer analysis should only use rows where:

```sql
developer = 1
```

Do not treat every involved company as a developer.

## BR-028 — Publisher Analysis Rule

Publisher analysis should only use rows where:

```sql
publisher = 1
```

Do not treat every involved company as a publisher.

## BR-029 — Porting and Supporting Rule

Porting and supporting companies should be kept because they describe real production involvement, but they should not be mixed with developers or publishers unless the analysis intentionally uses all involved companies.

Recommended categories:

| Role Type            | Use Case                                   |
| -------------------- | ------------------------------------------ |
| Developer            | Quality/performance by creator.            |
| Publisher            | Publishing/distribution patterns.          |
| Porting              | Platform port analysis.                    |
| Supporting           | Support network or production involvement. |
| Any involved company | Broad ecosystem analysis.                  |

## BR-030 — Multiple Role Rule

A company can be both developer and publisher for the same game.

Do not enforce mutual exclusivity across the company role flags.

Example valid case:

```text
developer = 1
publisher = 1
```

---

# 7. Release Date Rules

## BR-031 — Release Date Grain Rule

Each row in `release_dates` represents one release date record connected to a game and optionally scoped by platform, region, date format, and release status.

The table may include multiple release dates for the same game.

## BR-032 — Game-Level First Release vs Release Date Records

The `games.first_release_date` field and the `release_dates` table serve different purposes.

Rules:

| Field/Table                | Use                                                             |
| -------------------------- | --------------------------------------------------------------- |
| `games.first_release_date` | Earliest known game-level release date.                         |
| `release_dates`            | Detailed releases by platform, region, date format, and status. |

Do not use `games.first_release_date` as the only source for platform-specific release analysis.

## BR-033 — Release Year Rule

For yearly trend analysis, prefer `release_year`.

Valid release years should be reasonable for video game history and project scope.

Suggested validation:

```text
release_year >= 1950
release_year <= current year + 5
```

Future years may be valid for upcoming games, but they should be treated separately from historical release analysis.

## BR-034 — Release Month Rule

If `release_month` is populated, it must be between 1 and 12.

Mapping:

| Value | Month     |
| ----: | --------- |
|     1 | January   |
|     2 | February  |
|     3 | March     |
|     4 | April     |
|     5 | May       |
|     6 | June      |
|     7 | July      |
|     8 | August    |
|     9 | September |
|    10 | October   |
|    11 | November  |
|    12 | December  |

## BR-035 — Release Day Rule

If `release_day` is populated, it must be between 1 and 31.

Additional calendar validation may be applied later to catch impossible dates such as February 31.

## BR-036 — Release Date Precision Rule

The `date_format_id` should be used to understand how precise the release date is.

Rules:

* Exact dates are best for day-level analysis.
* Year-month or year-only records are acceptable for yearly trend analysis.
* TBD records should not be treated as exact dates.
* Use `human` when displaying incomplete dates.

## BR-037 — Release Region Rule

The `release_date_region_id` should be used when region-specific release timing matters.

Rules:

* Use worldwide release dates for global catalog views when available.
* Use region-specific release dates for regional analysis.
* Do not mix regional release dates without documenting the rule.

## BR-038 — Release Date Status Rule

The `release_date_status_id` should be used to interpret the lifecycle of a
specific release record.

Rules:

* Historical release analysis should prefer `Full Release` records when status
  is populated.
* Upcoming release analysis may include `Alpha`, `Beta`, `Early Access`, or
  `Advanced Access` records separately.
* Cancelled release records should not be treated as playable releases.
* Date uncertainty such as `TBD` is represented by `date_formats`, not by
  `release_date_statuses`.

---

# 8. Media and Website Rules

## BR-039 — Cover Rule

A game may have zero or one selected cover record in the current ERD.

Rules:

* Covers are optional enrichment.
* A missing cover should not exclude a game from analytics.
* A missing cover may reduce UI quality but does not invalidate the game record.

## BR-040 — Screenshot Rule

A game may have zero or many screenshots.

Rules:

* Screenshots are optional enrichment.
* A missing screenshot should not exclude a game from analytics.
* Screenshots are useful for UI and game detail pages.

## BR-041 — Website Link Rule

A game may have zero or many website links.

Rules:

* Website links are optional enrichment.
* Website links should be categorized through `website_types`.
* Do not infer store availability unless the relevant website type or external game source supports that inference.

## BR-042 — Trusted Website Rule

The `websites.trusted` flag should be interpreted as:

```text
1 = trusted
0 = not trusted
NULL = unknown
```

Rules:

* Prefer trusted links in the UI.
* Use official/store links before social/community links when presenting external navigation.
* Do not use untrusted links as authoritative evidence in RAG explanations.

## BR-043 — Image Dimension Rule

For image fields:

```text
covers.width
covers.height
screenshots.width
screenshots.height
```

Rules:

* Values should be non-negative when present.
* Width and height are measured in pixels.
* Records with missing image dimensions may still be kept if `url` or `image_id` exists.

---

# 9. External Game Mapping Rules

## BR-044 — External Game Mapping Rule

The `external_games` table maps IGDB games to external sources, stores, platforms, or databases.

Rules:

* The external source should be interpreted through `external_game_sources`.
* The external UID should not be interpreted without knowing the source.
* External game URLs are optional enrichment.

## BR-045 — External Source Rule

The same `game_id` may map to multiple external sources.

Example:

```text
One IGDB game may have one Steam record, one GOG record, and one Epic Games record.
```

## BR-046 — External Platform Rule

If `external_games.platform_id` is populated, it should be interpreted through the `platforms` table.

Do not assume that an external source mapping applies to all platforms.

## BR-047 — Price Data Rule

The current ERD does not include price tables.

Rules:

* Do not claim current prices from this database.
* Do not forecast price or sale timing from this database.
* Price tracking is out of scope unless future tables are added.

---

# 10. Multiplayer Rules

## BR-048 — Multiplayer Support Rule

The `multiplayer_modes` table describes multiplayer support for a game, often scoped to a platform.

Rules:

* Multiplayer support should be interpreted with `platform_id` when available.
* Do not assume multiplayer support is identical across all platforms.
* Missing multiplayer records should be interpreted as unknown, not necessarily “no multiplayer.”

## BR-049 — Co-op Recommendation Rule

For co-op recommendations:

| User Intent         | Suggested Rule      |
| ------------------- | ------------------- |
| Campaign co-op      | `campaign_coop = 1` |
| Offline/local co-op | `offline_coop = 1`  |
| Online co-op        | `online_coop = 1`   |
| Split-screen        | `split_screen = 1`  |

## BR-050 — Multiplayer Boolean Rule

Valid multiplayer boolean values are:

```text
1 = yes / true
0 = no / false
NULL = unknown
```

Invalid values should be flagged during data quality checks.

---

# 11. Time-to-Beat Rules

## BR-051 — Time-to-Beat Unit Rule

The `game_time_to_beats` time fields should be interpreted in seconds:

```text
hastily
normally
completely
```

Rules:

* Convert seconds to hours for dashboard display.
* Keep seconds in the raw table to preserve the original unit.
* Use derived hour fields in analysis views if needed.

## BR-052 — Time-to-Beat Interpretation Rule

The time-to-beat fields should be interpreted as:

| Column       | Meaning                                     |
| ------------ | ------------------------------------------- |
| `hastily`    | Average quick completion time.              |
| `normally`   | Average normal completion time.             |
| `completely` | Average completionist time.                 |
| `count`      | Number of observations behind the estimate. |

The three averages are independent source values. Do not assume
`hastily <= normally <= completely` always holds; the current extract contains
exceptions.

## BR-053 — Playtime Recommendation Rule

For playtime-based recommendations, use `normally` as the default playtime measure.

Suggested project-defined labels:

| Normal Playtime | Label      |
| --------------: | ---------- |
|       0–5 hours | Very short |
|      5–15 hours | Short      |
|     15–30 hours | Medium     |
|     30–60 hours | Long       |
|       60+ hours | Very long  |

Important note:

These labels are project-defined, not official IGDB categories.

---

# 12. Popularity Rules

## BR-054 — Popularity Primitive Rule

The `popularity_primitives` table stores popularity signal values.

A popularity value must be interpreted with:

```text
game_id
external_popularity_source_id
popularity_type_id
calculated_at
```

Do not interpret `value` alone without joining to `popularity_types`.

## BR-055 — Popularity Type Rule

The `popularity_types` table defines the meaning of each popularity signal.

Rules:

* Join `popularity_primitives.popularity_type_id` to `popularity_types.popularity_type_id`.
* Join source fields to `external_game_sources` when source-level interpretation is needed.
* Do not compare popularity values across different popularity types unless normalized.

## BR-056 — Popularity Source Rule

Popularity values from different sources should not be treated as equivalent without normalization.

Example:

```text
Steam wishlist value ≠ Twitch hours watched value ≠ IGDB visits value
```

## BR-057 — Popularity Snapshot Rule

If `calculated_at` is populated, popularity values should be treated as time-sensitive snapshots.

Rules:

* Use the latest snapshot for current popularity ranking.
* Keep historical snapshots only if trend analysis is intended.
* Do not compare popularity values from different calculation dates without documenting the method.

---

# 13. Rating and Quality Rules

## BR-058 — Rating Range Rule

Ratings should be interpreted as scores out of 100.

Valid range:

```text
0 <= rating <= 100
0 <= total_rating <= 100
```

Records outside this range should be flagged.

## BR-059 — Rating Count Rule

Rating count fields should be non-negative.

Valid fields:

```text
rating_count >= 0
total_rating_count >= 0
```

## BR-060 — Total Rating Rule

Use `total_rating` as the default quality score when available.

Rules:

* Use `total_rating` for high-level quality analysis.
* Use `total_rating_count` to evaluate confidence.
* If `total_rating` is missing but `rating` exists, `rating` may be used as a fallback only if documented.

## BR-061 — Highly Rated Rule

A game is classified as highly rated when:

```text
total_rating >= 80
```

Recommended modeling version:

```text
highly_rated = 1 if total_rating >= 80 and total_rating_count >= 10
highly_rated = 0 if total_rating < 80 and total_rating_count >= 10
exclude from supervised target if total_rating is null or total_rating_count < 10
```

## BR-062 — Rating Band Rule

Project-defined rating bands:

| Rating Range | Label                       |
| -----------: | --------------------------- |
|       90–100 | Excellent                   |
|     80–89.99 | Highly rated                |
|     70–79.99 | Good                        |
|     60–69.99 | Mixed / average             |
|     Below 60 | Lower rated                 |
|         NULL | Unrated / insufficient data |

Important note:

These labels are project-defined for dashboarding and recommendations. They are not official IGDB categories.

---

# 14. Hidden Gem Rules

## BR-063 — Hidden Gem Candidate Rule

A hidden gem candidate should satisfy:

```text
high quality
sufficient rating confidence
lower relative popularity
```

Suggested first rule:

```text
total_rating >= 80
AND total_rating_count >= 10
AND normalized_popularity is below the median for comparable games
```

Current-sample limitation:

The extractor selected the 500 games with the highest `total_rating_count`
among records meeting the base filters. This is useful for schema and pipeline
development but is popularity-biased. Final hidden-gem analysis requires a
larger, less popularity-biased extraction.

## BR-064 — Comparable Group Rule

Hidden gem comparisons should be made within relevant groups when possible.

Good comparison groups:

```text
same genre
same platform family
same release decade
same game type
```

Avoid comparing:

```text
AAA console releases directly against tiny niche PC-only games without context
```

## BR-065 — Popularity Bias Mitigation Rule

The recommendation system should not rank only by popularity.

Ranking should combine:

```text
metadata match
semantic similarity
platform eligibility
rating / quality
popularity adjustment
hidden gem boost
```

## BR-066 — Hidden Gem Label Caution Rule

A hidden gem label is project-defined and should be presented as an analytical label, not an objective truth.

Suggested wording:

```text
“Hidden gem candidate”
```

Avoid wording:

```text
“This is definitely a hidden gem.”
```

---

# 15. Recommendation Engine Rules

## BR-067 — Platform Hard Filter Rule

If the user specifies a platform, platform matching should be treated as a hard filter.

Example:

```text
User asks for Nintendo Switch games.
Only games linked to Nintendo Switch through game_platforms should be returned.
```

## BR-068 — Game Type Hard Filter Rule

For general recommendations, non-main-game records should be excluded or down-ranked.

Suggested default:

```text
Prefer main games.
Exclude DLC/add-ons, updates, packs, and non-standalone records unless requested.
```

## BR-069 — Released Game Preference Rule

For general recommendations, games with a release date on or before the current
date should be prioritized.

Exceptions:

* User asks for upcoming games.
* User asks for early access games.
* User asks for unreleased or rumored games.

Do not use `game_status_id IS NULL` as proof of release. Use game-level and
platform-level release dates, then apply explicit `Offline` or `Delisted`
status exclusions where appropriate.

## BR-070 — Metadata Soft Match Rule

If the user expresses preferences for genre, theme, keyword, game mode, or player perspective, these should be used as soft ranking features unless the user clearly frames them as hard requirements.

Examples:

| User Wording                 | Rule                       |
| ---------------------------- | -------------------------- |
| “must be co-op”              | Hard filter if possible.   |
| “prefer co-op”               | Soft boost.                |
| “something cozy or relaxing” | Soft semantic/theme boost. |
| “only on PC”                 | Hard platform filter.      |

## BR-071 — Rating Soft Ranking Rule

Ratings should influence ranking but should not be the only factor.

Rules:

* Prefer higher `total_rating` when reliable.
* Avoid recommending games solely because they have high ratings.
* Consider rating confidence through `total_rating_count`.

## BR-072 — Popularity Soft Ranking Rule

Popularity should be used carefully.

Rules:

* High popularity may indicate broad appeal.
* Low popularity with high rating may indicate a hidden gem.
* Popularity should not dominate semantic match.

## BR-073 — Match Explanation Rule

Every recommendation should be explainable using database-backed attributes.

Recommended explanation components:

```text
game title
platform match
genre/theme/keyword match
rating or rating band when available
developer/publisher when available
reason it matches the prompt
```

---

# 16. RAG Grounding Rules

## BR-074 — Database-Only Grounding Rule

The RAG chatbot should only use game facts available in the database or retrieved game profile documents.

It should not invent:

```text
platform availability
developer/publisher
ratings
release dates
genres/themes
external links
playtime
multiplayer support
```

## BR-075 — Retrieved Context Rule

The chatbot should only recommend games that were retrieved from the vector database or selected through structured database filtering.

If no strong match exists, the chatbot should say that no strong match was found.

## BR-076 — Missing Metadata Disclosure Rule

If a useful field is missing, the system should avoid pretending it exists.

Examples:

```text
If total_rating is null:
Do not say the game is highly rated.

If platform data is missing:
Do not claim platform availability.

If developer data is missing:
Do not mention developer.
```

## BR-077 — RAG Profile Construction Rule

RAG game profiles should be constructed from database fields such as:

```text
games.name
games.summary
games.storyline
genres.name
themes.name
keywords.name
platforms.name
game_modes.name
player_perspectives.name
companies.name
rating fields
release_year
```

## BR-078 — RAG Hallucination Prevention Rule

The system should refuse or qualify unsupported claims.

Suggested behavior:

```text
“I do not have enough database-backed information to confirm that.”
```

---

# 17. Dashboard Rules

## BR-079 — Dashboard Filter Rule

Dashboards should make filtering transparent.

Recommended filters:

```text
release year
platform
platform family
genre
theme
game type
game status
rating count threshold
rating band
developer/publisher
```

## BR-080 — Missing Data Display Rule

Dashboards should not hide missingness entirely.

Recommended missingness views:

```text
missing summaries
missing storylines
missing ratings
missing platforms
missing release years
missing company data
```

## BR-081 — Rating Dashboard Rule

Rating dashboards should include rating count or confidence.

Do not show rating averages without showing how many ratings support them.

## BR-082 — Popularity Dashboard Rule

Popularity dashboards must separate popularity types.

Do not mix different popularity signals in one chart unless values are normalized.

## BR-083 — Release Trend Dashboard Rule

Release trend dashboards should use `release_year`.

If using `release_dates`, document whether the chart counts:

```text
game-level first release
all platform releases
worldwide releases only
regional releases
```

---

# 18. Predictive Modeling Rules

## BR-084 — Modeling Target Rule

The default predictive target is:

```text
highly_rated = total_rating >= 80
```

Recommended modeling inclusion rule:

```text
total_rating is not null
AND total_rating_count >= 10
```

## BR-085 — Feature Leakage Rule

Do not use target-derived fields as predictors.

If predicting high rating from `total_rating`, do not use:

```text
total_rating
rating
aggregated rating equivalents
rating_count as a proxy without justification
```

Potentially acceptable features:

```text
release_year
platform_count
genre_count
theme_count
keyword_count
game_type
game_status
company features
text-derived features
game mode flags
player perspective flags
```

## BR-086 — Text Feature Rule

Text-derived features from `summary`, `storyline`, genres, themes, and keywords may be used for modeling if documented.

Examples:

```text
summary length
storyline length
TF-IDF features
embedding clusters
semantic topic features
```

## BR-087 — Train/Test Split Rule

Predictive modeling should avoid random leakage where possible.

Recommended approach:

```text
Use a reproducible random seed.
Consider time-based validation if release year is central to the analysis.
Document the split strategy.
```

## BR-088 — Model Evaluation Rule

Model performance should be reported using more than accuracy.

Recommended metrics:

```text
ROC-AUC
precision
recall
F1-score
confusion matrix
class balance
```

---

# 19. Data Completeness and Missingness Rules

## BR-089 — Missing Values Rule

Missing values should be retained as nulls unless a clear transformation rule exists.

Do not fill missing ratings, dates, platforms, or company relationships with invented values.

## BR-090 — Required Fields for Final Catalog Rule

For the final cleaned game catalog, the minimum required fields are:

```text
game_id
name
```

For analytics-ready records, additional required fields depend on analysis type.

| Analysis Type     | Required Fields                                  |
| ----------------- | ------------------------------------------------ |
| Release analysis  | `release_year` or `release_dates.release_year`   |
| Rating analysis   | `total_rating`, `total_rating_count`             |
| Platform analysis | `game_platforms.platform_id`                     |
| Genre analysis    | `game_genres.genre_id`                           |
| Company analysis  | `involved_companies.company_id`                  |
| RAG               | `summary` or `storyline` or rich metadata fields |

## BR-091 — Missingness Documentation Rule

Missingness should be measured and documented for key fields:

```text
summary
storyline
first_release_date
release_year
rating
rating_count
total_rating
total_rating_count
game_type_id
game_status_id
platform relationships
genre relationships
theme relationships
company relationships
cover image
website links
```

---

# 20. Data Integrity Rules

## BR-092 — Primary Key Rule

Every table must have a non-null primary key.

For bridge tables, composite primary keys must uniquely identify the relationship.

## BR-093 — Foreign Key Rule

Every declared SQLite foreign key should point to an existing parent record.

Examples:

```text
game_genres.game_id → games.game_id
game_genres.genre_id → genres.genre_id
game_platforms.platform_id → platforms.platform_id
involved_companies.company_id → companies.company_id
release_dates.date_format_id → date_formats.date_format_id
websites.website_type_id → website_types.website_type_id
```

Some source reference fields are intentionally not declared as foreign keys in
the current schema because related parent records may fall outside the selected
500-game extraction:

```text
games.parent_game_id
games.version_parent_id
games.cover_id
companies.parent_company_id
companies.status_id
```

Treat these as optional source references. Do not assume they can always be
joined within the local database. `games.cover_id` currently resolves for all
500 games, but the relationship is not enforced by SQLite.

## BR-094 — Orphan Record Rule

No child table should contain records that point to missing parent records.

Examples of orphan records:

```text
A row in game_platforms with a game_id not found in games.
A row in release_dates with a platform_id not found in platforms.
A row in websites with a website_type_id not found in website_types.
```

## BR-095 — Duplicate Entity Rule

Primary entity tables should not contain duplicate IDs.

Tables include:

```text
games
genres
themes
keywords
platforms
companies
```

## BR-096 — Duplicate Relationship Rule

Bridge tables should not contain duplicate pairs.

Examples:

```text
game_id + genre_id
game_id + theme_id
game_id + keyword_id
game_id + platform_id
```

---

# 21. API Ingestion and Refresh Rules

## BR-097 — API Rate Limit Rule

The ingestion pipeline must respect IGDB API rate limits.

Rules:

* Use batching and pagination.
* Avoid unnecessary repeated calls.
* Cache raw JSON when appropriate.
* Retry failed calls with backoff.

## BR-098 — Raw Data Preservation Rule

Raw API responses should be saved before transformation when feasible.

Recommended storage:

```text
data/raw/
```

Do not overwrite raw files without versioning or a clear refresh process.

## BR-099 — Transformation Reproducibility Rule

All transformations from raw JSON to relational tables must be reproducible through scripts.

Recommended storage:

```text
src/extract/
src/transform/
src/load/
```

## BR-100 — Local Database Rebuild Rule

The SQLite database should be rebuildable from:

```text
raw data
SQL schema
Python ETL scripts
documentation
```

The full `.db` file does not need to be committed to GitHub if it can be regenerated.

---

# 22. GitHub and Data Storage Rules

## BR-101 — Secret Management Rule

API credentials must never be committed to GitHub.

Do not commit:

```text
.env
client_secret
access_token
API keys
```

## BR-102 — Large Data Rule

Large raw JSON dumps and full SQLite database files should generally not be committed to GitHub.

Recommended approach:

```text
Commit scripts, schema, documentation, and small sample data.
Regenerate large data locally.
```

## BR-103 — Sample Data Rule

A small sample dataset may be committed for reproducibility and teammate onboarding.

Recommended sample size:

```text
100 to 500 records
```

---

# 23. Out-of-Scope Rules

## BR-104 — Price Tracking Rule

The current database does not support live price tracking or price forecasting.

Do not claim:

```text
current game prices
sale predictions
discount timing
buy-now recommendations based on price
```

unless additional external price data is added later.

## BR-105 — User Account Rule

The current ERD does not include user account tables.

Do not claim persistent user profiles, login, saved preferences, or recommendation history unless future tables are added.

## BR-106 — Collaborative Filtering Rule

The current ERD does not include user-game interaction matrices.

Do not build or claim full collaborative filtering unless user interaction data is added later.

---

# 24. Business Rule Summary by Project Output

## Descriptive Analytics

Required rules:

```text
BR-008 Minimum Game Record Rule
BR-015 Genre Normalization Rule
BR-016 Theme Normalization Rule
BR-021 Platform Availability Rule
BR-031 Release Date Grain Rule
BR-080 Missing Data Display Rule
```

## Diagnostic Analytics

Required rules:

```text
BR-013 Rating Reliability Rule
BR-027 Developer Analysis Rule
BR-028 Publisher Analysis Rule
BR-055 Popularity Type Rule
BR-064 Comparable Group Rule
BR-081 Rating Dashboard Rule
BR-082 Popularity Dashboard Rule
```

## Predictive Analytics

Required rules:

```text
BR-014 High-Rated Game Rule
BR-084 Modeling Target Rule
BR-085 Feature Leakage Rule
BR-086 Text Feature Rule
BR-087 Train/Test Split Rule
BR-088 Model Evaluation Rule
```

## Prescriptive Recommendation

Required rules:

```text
BR-010 Main Game Recommendation Rule
BR-011 Game Status Recommendation Rule
BR-022 Platform-Constrained Recommendation Rule
BR-067 Platform Hard Filter Rule
BR-070 Metadata Soft Match Rule
BR-071 Rating Soft Ranking Rule
BR-072 Popularity Soft Ranking Rule
BR-073 Match Explanation Rule
```

## RAG Chatbot

Required rules:

```text
BR-074 Database-Only Grounding Rule
BR-075 Retrieved Context Rule
BR-076 Missing Metadata Disclosure Rule
BR-077 RAG Profile Construction Rule
BR-078 RAG Hallucination Prevention Rule
```

---

# 25. Rule Maintenance

## BR-107 — Documentation Sync Rule

This business rules document must be updated whenever:

* The ERD changes.
* A table is added or removed.
* A column is renamed.
* A new transformation rule is added.
* A recommendation rule changes.
* A new model target is defined.
* A new external data source is added.

## BR-108 — Authoritative Schema Rule

If there is a conflict between this document and the actual database schema, the authoritative source is:

```text
src/create_IGDB_relational_DB.py
data/database/igdb_games.db
```

The documentation should then be updated to match the schema.
