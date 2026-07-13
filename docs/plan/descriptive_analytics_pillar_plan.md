# Descriptive Analytics Pillar Plan  
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Pillar:** Descriptive Analytics  
**Dashboard Page:** Catalog Overview  

---

# 1. Purpose of the Descriptive Pillar

The descriptive analytics pillar answers the question:

> **What does the IGDB game catalog look like?**

This pillar should summarize the structure, coverage, composition, and data quality of the project database before moving into diagnostic, predictive, and prescriptive analytics.

The goal is not to explain why games perform better, predict ratings, or recommend games yet. Instead, this stage gives the audience a clear understanding of:

- How many games are in the catalog.
- Which genres, themes, platforms, and companies are represented.
- How games are distributed across release years.
- How ratings and rating counts are distributed.
- Which fields are complete or missing.
- What limitations exist in the current dataset.

---

# 2. Descriptive Analytics Main Question

## Main Question

> **What does the game catalog look like?**

## Supporting Questions

1. How many games, platforms, genres, themes, keywords, and companies are represented?
2. Which genres and themes are most common?
3. Which platforms and platform families are most represented?
4. How are games distributed across release years and decades?
5. What does the rating distribution look like?
6. How skewed are rating counts, and which popularity signals are available by source/type?
7. Which developers and publishers appear most frequently?
8. How complete is the metadata?
9. What data quality limitations should be considered before deeper analysis?

---

# 3. Position Within the Four-Pillar Framework

The descriptive pillar should be positioned as the foundation for the other analytics pillars.

| Pillar | Main Question | Role in Project |
|---|---|---|
| Descriptive | What does the catalog look like? | Summarize dataset composition, coverage, and quality. |
| Diagnostic | Why do patterns exist? | Investigate ratings, popularity bias, hidden gems, and genre/theme performance. |
| Predictive | Can we estimate future or unknown match potential? | Score game similarity to user preferences or reference games using cosine similarity. |
| Prescriptive | What should the user do? | Recommend games using filters, scoring, cosine similarity, and RAG-grounded explanations. |

The descriptive pillar should avoid making causal claims. It should provide clean, trustworthy summaries that support the later pillars.

---

# 4. Data Foundation Needed Before Visualization

Because the IGDB database is relational and normalized, many tables have one-to-many or many-to-many relationships. For example:

- One game can have multiple genres.
- One game can have multiple themes.
- One game can appear on multiple platforms.
- One game can have multiple companies.
- One game can have multiple release date records.

Because of this, the descriptive analytics layer should not join every table into one large flat dataset. That would duplicate games and inflate counts.

Instead, create separate analytics views for each descriptive purpose.

The descriptive layer should use the normalized SQLite database tables and descriptive SQL views. It should not depend on predictive-layer artifacts such as similarity profiles, nearest-neighbor outputs, or persona evaluation results. Those assets belong to the predictive/similarity pillar and can be used later when the project moves into match scoring.

---

# 5. Recommended Analytics Views

These views are descriptive reporting views. They should preserve the correct table grain and should be built from the normalized relational schema.

## 5.1 `vw_game_base`

### Grain

One row per game.

### Purpose

Use this view for game-level metrics, KPI cards, rating distribution, release year trends, and metadata completeness.

### Suggested Fields

```text
game_id
name
slug
summary
storyline
first_release_date
first_release_date_iso
release_year
rating
rating_count
aggregated_rating
aggregated_rating_count
total_rating
total_rating_count
game_type_id
game_type_name
game_status_id
game_status_name
cover_id
updated_at_iso
```

### Lookup Labels

Use exact schema joins for readable labels:

```sql
LEFT JOIN game_types
    ON games.game_type_id = game_types.game_type_id

LEFT JOIN game_statuses
    ON games.game_status_id = game_statuses.game_status_id
```

Readable labels should come from:

```text
game_types.type_name
game_statuses.status_name
```

### Use Cases

- Total games.
- Games with ratings.
- Games with summaries.
- Games with storylines.
- Games with release year.
- Rating distribution.
- Rating count distribution.
- Release trend by year.
- Game type breakdown.
- Game status breakdown.

---

## 5.2 `vw_game_genre`

### Grain

One row per game-genre relationship.

### Purpose

Use this view for genre distribution and genre coverage.

### Suggested Fields

```text
game_id
game_name
genre_id
genre_name
total_rating
total_rating_count
release_year
```

### Use Cases

- Top genres by unique game count.
- Genre coverage.
- Genre share of catalog.
- Genre filters in dashboard.

### Important Note

A game can have multiple genres. Genre counts should be counted using:

```sql
COUNT(DISTINCT game_id)
```

---

## 5.3 `vw_game_theme`

### Grain

One row per game-theme relationship.

### Purpose

Use this view to summarize themes and support the “vibe-based discovery” framing of the project.

### Suggested Fields

```text
game_id
game_name
theme_id
theme_name
total_rating
total_rating_count
release_year
```

### Use Cases

- Top themes by unique game count.
- Theme coverage.
- Theme filters in dashboard.
- Support for later vibe-based recommendation logic.

---

## 5.4 `vw_game_keyword`

### Grain

One row per game-keyword relationship.

### Purpose

Use this view for fine-grained tag exploration.

### Suggested Fields

```text
game_id
game_name
keyword_id
keyword_name
total_rating
total_rating_count
release_year
```

### Use Cases

- Top keywords.
- Searchable keyword table.
- RAG profile enrichment.
- Fine-grained preference analysis later.

### Important Note

Keywords may be sparse and highly granular. They may work better as a searchable table than as a large chart.

---

## 5.5 `vw_game_platform`

### Grain

One row per game-platform relationship.

### Purpose

Use this view for platform coverage and platform availability analysis.

### Suggested Fields

```text
game_id
game_name
platform_id
platform_name
platform_abbreviation
platform_family_id
platform_family_name
platform_type_id
platform_type_name
release_year
total_rating
total_rating_count
```

### Lookup Labels

Readable platform labels should come from:

```text
platforms.name
platforms.abbreviation
platform_families.name
platform_types.name
```

### Use Cases

- Top platforms.
- Platform family distribution.
- Platform type distribution.
- Console vs PC vs operating system coverage.
- Platform filters for future recommendation logic.

### Important Note

Platform counts are relationship counts. Because one game can appear on multiple platforms, platform totals will usually exceed the number of unique games.

---

## 5.6 `vw_game_company_roles`

### Grain

One row per game-company relationship.

### Purpose

Use this view for developer and publisher summaries.

### Suggested Fields

```text
game_id
game_name
company_id
company_name
developer
publisher
porting
supporting
```

### Use Cases

- Top developers by unique game count.
- Top publishers by unique game count.
- Company role coverage.
- Developer/publisher filters.

### Important Note

Company role fields are boolean flags. Use:

```text
1 = Yes / True
0 = No / False
NULL = Unknown / Missing
```

A company can also have multiple roles for the same game. For example, one company can be both the developer and publisher.

---

## 5.7 `vw_game_mode`

### Grain

One row per game-mode relationship.

### Purpose

Use this view to summarize broad play-style support such as single-player, multiplayer, co-op, split-screen, MMO, and battle royale.

### Suggested Fields

```text
game_id
game_name
game_mode_id
game_mode_name
release_year
total_rating
total_rating_count
```

### Use Cases

- Games by game mode.
- Single-player versus multiplayer coverage.
- Co-op and split-screen coverage.
- Filters for future recommendation logic.

### Important Note

Game mode labels come from the `game_modes` lookup table and the `game_modes_bridge` relationship table. A game can have multiple game modes, so counts should use:

```sql
COUNT(DISTINCT game_id)
```

---

## 5.8 `vw_multiplayer_player_support`

### Grain

One row per game after summarizing available multiplayer detail records.

### Purpose

Use this view to summarize detailed multiplayer support and max-player metadata.

### Suggested Fields

```text
game_id
game_name
has_multiplayer_detail
has_campaign_coop
has_drop_in
has_lan_coop
has_offline_coop
has_online_coop
has_split_screen
max_offline_coop_players
max_offline_players
max_online_coop_players
max_online_players
```

### Use Cases

- Multiplayer detail coverage.
- Local/offline co-op coverage.
- Online co-op coverage.
- Split-screen coverage.
- Maximum online/offline player count distributions.

### Important Note

`multiplayer_modes` records can be platform-specific. A game may support different player counts on different platforms. Missing multiplayer detail should not automatically be interpreted as single-player only.

---

# 6. Dashboard Page Structure

The descriptive dashboard page should be called:

```text
Catalog Overview
```

## Recommended Page Sections

```text
Catalog Overview
│
├── Section 1: Dataset Snapshot
├── Section 2: Catalog Composition
├── Section 3: Platform Coverage
├── Section 4: Release Timeline
├── Section 5: Rating and Popularity Overview
├── Section 6: Developer and Publisher Overview
├── Section 7: Metadata Completeness and Data Quality
└── Section 8: Key Takeaways
```

---

# 7. Section 1 — Dataset Snapshot

## Purpose

Give the audience an immediate high-level understanding of the dataset.

## KPI Cards

| KPI | Description |
|---|---|
| Total Games | Number of unique games in the catalog. |
| Total Platforms | Number of platforms represented. |
| Total Genres | Number of genres represented. |
| Total Themes | Number of themes represented. |
| Total Keywords | Number of keywords represented. |
| Total Companies | Number of companies represented. |
| Games With Ratings | Number and percentage of games with `total_rating`. |
| Games With Rating Counts | Number and percentage of games with `total_rating_count`. |
| Games With Summaries | Number and percentage of games with a summary. |
| Games With Storylines | Number and percentage of games with a storyline. |
| Games With Release Year | Number and percentage of games with release year. |
| Games With Covers | Number and percentage of games with cover metadata. |

## Suggested Dashboard Text

```markdown
This page summarizes the current IGDB game catalog used by the project. It provides a descriptive overview of catalog size, game classifications, platform coverage, release trends, ratings, and metadata completeness. These summaries establish the data foundation for later diagnostic, predictive, and prescriptive analytics.
```

## Important Caveat

If the current dataset is still a curated sample, clearly state that the results describe the extracted sample, not the full IGDB catalog.

The current extraction targeted 50,000 released main games from 2010 through
2024 and selected 47,835 games because the earliest years did not have enough
eligible records to fill the configured yearly target. Every selected game has
a name, release date, genre, and platform.

The sample deliberately combines quality, lower-rated, PopScore visibility,
low-known-visibility, and random residual comparison cohorts. It is designed
for analytical contrast but is not a random sample of the complete IGDB catalog.

The current selection applies:

```text
main games only
name, release date, genre, and platform required
quality cohort: total_rating >= 75 and total_rating_count >= 25
lower-rated cohort: total_rating <= 60 and total_rating_count >= 25
popularity cohort: IGDB PopScore interest / Visits
low-visibility cohort: low known IGDB interest / Visits
comparison cohort: reproducible random sample of remaining games
```

If the extraction target or base extraction filters change, rerun the
extraction, rebuild the database, rerun this descriptive notebook, and update
the caveat in the dashboard/report.

Suggested wording:

```markdown
The current descriptive results represent a curated 47,835-game IGDB sample,
not the full IGDB catalog or video game market. The extraction targeted 50,000
released main games from 2010 through 2024 and selected 47,835 because the
earliest years had fewer eligible records than the configured yearly target.
The sample deliberately includes quality, lower-rated, popularity,
low-visibility, and comparison cohorts. Use `extraction_cohorts` to report
sample composition. Full-sample quality, lower-rated, popularity, or
low-visibility shares must not be interpreted as market prevalence.
```

---

# 8. Section 2 — Catalog Composition

## Purpose

Answer:

> What kinds of games are represented in the catalog?

---

## Visual 1: Top Genres

### Chart Type

Horizontal bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Top Genres by Number of Games
```

### Interpretation

This chart shows the most common broad gameplay categories in the catalog.

### Dashboard Note

```markdown
Games can belong to multiple genres, so genre counts represent game-genre relationships and should not be summed as unique games.
```

---

## Visual 2: Top Themes

### Chart Type

Horizontal bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Top Themes by Number of Games
```

### Interpretation

This chart shows common high-level moods, settings, or thematic categories in the catalog.

### Why It Matters

Themes are important for the project because the recommendation system is designed to support natural-language, vibe-based game discovery.

---

## Visual 3: Top Keywords

### Chart Type

Horizontal bar chart or searchable table.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Most Common Keywords
```

### Interpretation

Keywords provide more granular information than genres or themes. They can help support semantic search and RAG explanations later.

### Recommendation

Use a searchable table if the number of keywords is too large or sparse.

---

## Visual 4: Game Type Breakdown

### Chart Type

Bar chart or donut chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Game Type Breakdown
```

### Categories

Examples may include:

- Main Game
- Expansion
- Bundle
- Standalone Expansion
- Remake
- Remaster
- Expanded Game
- Port

### Interpretation

This chart helps identify whether the catalog is mostly standalone games or whether it includes many expansions, ports, remasters, and bundles.

### Why It Matters

For the recommendation engine, general game recommendations should usually prioritize standalone main games unless the user specifically asks for DLC, ports, remasters, or expansions.

---

# 9. Section 3 — Platform Coverage

## Purpose

Answer:

> Where can the games in the catalog be played?

---

## Visual 1: Top Platforms

### Chart Type

Horizontal bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Top Platforms by Number of Games
```

### Interpretation

This chart shows the platforms most represented in the catalog.

### Dashboard Note

```markdown
Platform counts are based on game-platform relationships. Because a single game can be available on multiple platforms, platform counts should not be summed as unique games.
```

---

## Visual 2: Platform Family Distribution

### Chart Type

Bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Games by Platform Family
```

### Example Families

- PlayStation
- Xbox
- Nintendo
- Other / Unknown

### Why It Matters

Users often ask for broad platform families rather than exact platform names. This view supports later recommendation filtering.

---

## Visual 3: Platform Type Distribution

### Chart Type

Bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Games by Platform Type
```

### Example Types

- Console
- Computer
- Operating System
- Portable Console
- Arcade

### Interpretation

This chart helps explain whether the dataset is console-heavy, PC-heavy, or broadly distributed.

---

# 10. Section 4 — Release Timeline

## Purpose

Answer:

> When were the games in the catalog released?

---

## Visual 1: Games by Release Year

### Chart Type

Line chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Games by Release Year
```

### Filter

```sql
WHERE release_year IS NOT NULL
```

### Interpretation

This chart shows the historical distribution of games in the catalog.

---

## Visual 2: Games by Release Decade

### Chart Type

Bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Games by Release Decade
```

### Example Bins

```text
1980s
1990s
2000s
2010s
2020s
Unknown
Upcoming / Future
```

### Why It Matters

Decade-level grouping makes the timeline easier to interpret when the year-by-year chart is noisy.

---

## Visual 3: Release Year by Platform Type

### Chart Type

Stacked bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Release Decade by Platform Type
```

### Use Case

This can show how platform representation changes over time.

### Important Caveat

Game-level release year and platform-specific release dates are not the same thing. Use `games.release_year` for general trends and `release_dates` for platform-specific timing.

---

# 11. Section 5 — Rating and Popularity Overview

## Purpose

Answer:

> What does the rating profile of the catalog look like?

## Important Popularity Caveat

Use `total_rating_count` as the primary descriptive proxy for rating confidence and catalog visibility. If using `popularity_primitives`, do not combine all popularity values into one chart or score by default. Each popularity value has a meaning defined by `popularity_type_id` and `external_popularity_source_id`, so popularity signals should be grouped by source/type or normalized before comparison.

---

## Visual 1: Total Rating Distribution

### Chart Type

Histogram.

### Metric

```text
total_rating
```

### Suggested Title

```text
Distribution of Total Ratings
```

### Suggested Bins

```text
0–59
60–69
70–79
80–89
90–100
Unrated
```

### Interpretation

This chart shows how quality scores are distributed across the catalog.

---

## Visual 2: Rating Band Distribution

### Chart Type

Bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Games by Rating Band
```

### Project-Defined Rating Bands

| Rating Range | Label |
|---:|---|
| 90–100 | Excellent |
| 80–89.99 | Highly rated |
| 70–79.99 | Good |
| 60–69.99 | Mixed / average |
| Below 60 | Lower rated |
| NULL | Unrated / insufficient data |

### Important Note

These are project-defined dashboard labels, not official IGDB categories.

---

## Visual 3: Rating Count Distribution

### Chart Type

Histogram.

### Metric

```text
total_rating_count
```

### Suggested Title

```text
Distribution of Rating Counts
```

### Recommendation

Use a log scale if the distribution is highly skewed.

### Interpretation

Rating count is a proxy for rating confidence and visibility within the project sample. A high rating with very few ratings should be interpreted more cautiously than a high rating with many ratings.

---

## Visual 4: Rating Coverage Summary

### Chart Type

KPI cards or table.

### Metrics

```text
% games with total_rating
% games with total_rating_count
% games with rating
% games with rating_count
% games with aggregated_rating
% games with aggregated_rating_count
```

### Why It Matters

Rating-dependent analysis should exclude games with missing ratings. This chart helps explain how much of the catalog can be used for rating-based analysis and modeling.

---

## Visual 5: Popularity Signal Availability

### Chart Type

Table or grouped bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Suggested Title

```text
Popularity Signals by Source and Type
```

### Recommended Grouping

```text
external_popularity_source_id
popularity_type_id
popularity_type_name
```

### Important Note

Popularity values from different sources and signal types should not be directly compared unless they are normalized. For the descriptive pillar, this view should focus on availability and coverage of popularity signals, not a combined popularity score.

---

# 12. Section 6 — Developer and Publisher Overview

## Purpose

Answer:

> Which companies appear most often in the catalog?

---

## Visual 1: Top Developers

### Chart Type

Horizontal bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Filter

```sql
WHERE developer = 1
```

### Suggested Title

```text
Top Developers by Number of Games
```

### Important Note

Only companies where `developer = 1` should be treated as developers. Do not treat every involved company as a developer.

---

## Visual 2: Top Publishers

### Chart Type

Horizontal bar chart.

### Metric

```sql
COUNT(DISTINCT game_id)
```

### Filter

```sql
WHERE publisher = 1
```

### Suggested Title

```text
Top Publishers by Number of Games
```

### Important Note

Only companies where `publisher = 1` should be treated as publishers.

---

## Visual 3: Company Role Coverage

### Chart Type

Bar chart.

### Metric

Count of game-company relationships by role.

### Suggested Title

```text
Company Role Coverage
```

### Roles

```text
Developer
Publisher
Porting
Supporting
```

### Important Note

A company can have multiple roles for the same game, so role counts may overlap.

---

# 13. Section 7 — Metadata Completeness and Data Quality

## Purpose

Answer:

> How complete and trustworthy is the dataset for analytics, modeling, recommendations, and RAG?

---

## Visual 1: Field Completeness Table

### Chart Type

Table.

### Fields to Check

```text
name
summary
storyline
release_year
rating
rating_count
aggregated_rating
aggregated_rating_count
total_rating
total_rating_count
game_type_id
game_status_id
cover_id
```

### Columns

```text
field_name
total_records
non_null_count
missing_count
completion_rate
```

### Why It Matters

This protects the project from overclaiming. For example, if storylines are missing for many games, RAG responses should rely more heavily on summaries, genres, themes, and keywords.

---

## Visual 2: Relationship Coverage Table

### Chart Type

Table or KPI cards.

### Metrics

```text
% games with at least one genre
% games with at least one theme
% games with at least one keyword
% games with at least one platform
% games with at least one company
% games with at least one release date
% games with at least one cover
% games with at least one website
```

### Why It Matters

This shows which parts of the relational database are strong enough to support later analytics and recommendations.

---

## Visual 3: Data Quality Status Cards

### Chart Type

Status cards.

### Suggested Checks

| Check | Expected Result |
|---|---|
| SQLite integrity check | `ok` |
| Foreign key failures | 0 |
| Empty core tables | 0 |
| Duplicate primary keys | 0 |
| Duplicate bridge relationships | 0 |
| Invalid rating ranges | 0 |
| Negative rating counts | 0 |
| Missing required game names | 0 |
| Invalid release months | 0 |
| Invalid release days | 0 |

### Severity Guidance

| Severity | Meaning |
|---|---|
| Critical | Must fix before analysis, modeling, recommendation, or RAG. |
| High | Should fix before final deliverable. |
| Medium | Investigate and document. |
| Low | Nice to improve, not blocking. |

---

# 14. Suggested SQL Queries

## 14.1 Total KPI Snapshot

```sql
SELECT
    COUNT(DISTINCT game_id) AS total_games,
    COUNT(DISTINCT CASE WHEN total_rating IS NOT NULL THEN game_id END) AS games_with_total_rating,
    COUNT(DISTINCT CASE WHEN total_rating_count IS NOT NULL THEN game_id END) AS games_with_total_rating_count,
    COUNT(DISTINCT CASE WHEN summary IS NOT NULL AND TRIM(summary) <> '' THEN game_id END) AS games_with_summary,
    COUNT(DISTINCT CASE WHEN storyline IS NOT NULL AND TRIM(storyline) <> '' THEN game_id END) AS games_with_storyline,
    COUNT(DISTINCT CASE WHEN release_year IS NOT NULL THEN game_id END) AS games_with_release_year,
    COUNT(DISTINCT CASE WHEN cover_id IS NOT NULL THEN game_id END) AS games_with_cover
FROM games;
```

---

## 14.2 Top Genres

```sql
SELECT
    ge.name AS genre_name,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_genres gg
    ON g.game_id = gg.game_id
JOIN genres ge
    ON gg.genre_id = ge.genre_id
GROUP BY ge.name
ORDER BY game_count DESC;
```

---

## 14.3 Top Themes

```sql
SELECT
    th.name AS theme_name,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_themes gt
    ON g.game_id = gt.game_id
JOIN themes th
    ON gt.theme_id = th.theme_id
GROUP BY th.name
ORDER BY game_count DESC;
```

---

## 14.4 Top Keywords

```sql
SELECT
    kw.name AS keyword_name,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_keywords gk
    ON g.game_id = gk.game_id
JOIN keywords kw
    ON gk.keyword_id = kw.keyword_id
GROUP BY kw.name
ORDER BY game_count DESC;
```

---

## 14.5 Top Platforms

```sql
SELECT
    p.name AS platform_name,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_platforms gp
    ON g.game_id = gp.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id
GROUP BY p.name
ORDER BY game_count DESC;
```

---

## 14.6 Platform Family Distribution

```sql
SELECT
    COALESCE(pf.name, 'Unknown / No Family') AS platform_family,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_platforms gp
    ON g.game_id = gp.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id
LEFT JOIN platform_families pf
    ON p.platform_family_id = pf.platform_family_id
GROUP BY COALESCE(pf.name, 'Unknown / No Family')
ORDER BY game_count DESC;
```

---

## 14.7 Platform Type Distribution

```sql
SELECT
    COALESCE(pt.name, 'Unknown / No Type') AS platform_type,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
JOIN game_platforms gp
    ON g.game_id = gp.game_id
JOIN platforms p
    ON gp.platform_id = p.platform_id
LEFT JOIN platform_types pt
    ON p.platform_type_id = pt.platform_type_id
GROUP BY COALESCE(pt.name, 'Unknown / No Type')
ORDER BY game_count DESC;
```

---

## 14.8 Games by Release Year

```sql
SELECT
    release_year,
    COUNT(DISTINCT game_id) AS game_count
FROM games
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year;
```

---

## 14.9 Games by Release Decade

```sql
WITH decade_bins AS (
    SELECT
        game_id,
        CASE
            WHEN release_year IS NULL THEN 'Unknown'
            WHEN release_year < 1980 THEN 'Before 1980'
            WHEN release_year BETWEEN 1980 AND 1989 THEN '1980s'
            WHEN release_year BETWEEN 1990 AND 1999 THEN '1990s'
            WHEN release_year BETWEEN 2000 AND 2009 THEN '2000s'
            WHEN release_year BETWEEN 2010 AND 2019 THEN '2010s'
            WHEN release_year BETWEEN 2020 AND 2029 THEN '2020s'
            ELSE 'Future / Other'
        END AS release_decade,
        CASE
            WHEN release_year IS NULL THEN 99
            WHEN release_year < 1980 THEN 1
            WHEN release_year BETWEEN 1980 AND 1989 THEN 2
            WHEN release_year BETWEEN 1990 AND 1999 THEN 3
            WHEN release_year BETWEEN 2000 AND 2009 THEN 4
            WHEN release_year BETWEEN 2010 AND 2019 THEN 5
            WHEN release_year BETWEEN 2020 AND 2029 THEN 6
            ELSE 7
        END AS sort_order
    FROM games
)
SELECT
    release_decade,
    COUNT(DISTINCT game_id) AS game_count
FROM decade_bins
GROUP BY release_decade, sort_order
ORDER BY sort_order;
```

---

## 14.10 Rating Bands

```sql
SELECT
    CASE
        WHEN total_rating IS NULL THEN 'Unrated / insufficient data'
        WHEN total_rating >= 90 THEN 'Excellent'
        WHEN total_rating >= 80 THEN 'Highly rated'
        WHEN total_rating >= 70 THEN 'Good'
        WHEN total_rating >= 60 THEN 'Mixed / average'
        ELSE 'Lower rated'
    END AS rating_band,
    COUNT(DISTINCT game_id) AS game_count
FROM games
GROUP BY rating_band
ORDER BY
    CASE rating_band
        WHEN 'Excellent' THEN 1
        WHEN 'Highly rated' THEN 2
        WHEN 'Good' THEN 3
        WHEN 'Mixed / average' THEN 4
        WHEN 'Lower rated' THEN 5
        ELSE 6
    END;
```

---

## 14.11 Game Type Breakdown

```sql
SELECT
    COALESCE(gt.type_name, 'Unknown / No Type') AS game_type,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
LEFT JOIN game_types gt
    ON g.game_type_id = gt.game_type_id
GROUP BY COALESCE(gt.type_name, 'Unknown / No Type')
ORDER BY game_count DESC;
```

---

## 14.12 Game Status Breakdown

```sql
SELECT
    COALESCE(gs.status_name, 'Unknown / No Explicit Status') AS game_status,
    COUNT(DISTINCT g.game_id) AS game_count
FROM games g
LEFT JOIN game_statuses gs
    ON g.game_status_id = gs.game_status_id
GROUP BY COALESCE(gs.status_name, 'Unknown / No Explicit Status')
ORDER BY game_count DESC;
```

Important note:

```text
In the current schema, game status is an explicit availability/status value such as Offline or Delisted. A NULL game_status_id should not be interpreted as proof that a game is released or unreleased.
```

---

## 14.13 Top Developers

```sql
SELECT
    c.name AS developer_name,
    COUNT(DISTINCT ic.game_id) AS game_count
FROM involved_companies ic
JOIN companies c
    ON ic.company_id = c.company_id
WHERE ic.developer = 1
GROUP BY c.name
ORDER BY game_count DESC
LIMIT 15;
```

---

## 14.14 Top Publishers

```sql
SELECT
    c.name AS publisher_name,
    COUNT(DISTINCT ic.game_id) AS game_count
FROM involved_companies ic
JOIN companies c
    ON ic.company_id = c.company_id
WHERE ic.publisher = 1
GROUP BY c.name
ORDER BY game_count DESC
LIMIT 15;
```

---

## 14.15 Metadata Completeness

```sql
SELECT 'summary' AS field_name,
       COUNT(*) AS total_games,
       SUM(CASE WHEN summary IS NOT NULL AND TRIM(summary) <> '' THEN 1 ELSE 0 END) AS non_null_count,
       SUM(CASE WHEN summary IS NULL OR TRIM(summary) = '' THEN 1 ELSE 0 END) AS missing_count,
       ROUND(100.0 * SUM(CASE WHEN summary IS NOT NULL AND TRIM(summary) <> '' THEN 1 ELSE 0 END) / COUNT(*), 2) AS completion_rate
FROM games

UNION ALL

SELECT 'storyline',
       COUNT(*),
       SUM(CASE WHEN storyline IS NOT NULL AND TRIM(storyline) <> '' THEN 1 ELSE 0 END),
       SUM(CASE WHEN storyline IS NULL OR TRIM(storyline) = '' THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN storyline IS NOT NULL AND TRIM(storyline) <> '' THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM games

UNION ALL

SELECT 'total_rating',
       COUNT(*),
       SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN total_rating IS NULL THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM games

UNION ALL

SELECT 'release_year',
       COUNT(*),
       SUM(CASE WHEN release_year IS NOT NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN release_year IS NULL THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN release_year IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM games;
```

---

## 14.16 Relationship Coverage

```sql
WITH
genre_games AS (
    SELECT DISTINCT game_id FROM game_genres
),
theme_games AS (
    SELECT DISTINCT game_id FROM game_themes
),
keyword_games AS (
    SELECT DISTINCT game_id FROM game_keywords
),
platform_games AS (
    SELECT DISTINCT game_id FROM game_platforms
),
company_games AS (
    SELECT DISTINCT game_id FROM involved_companies
),
release_date_games AS (
    SELECT DISTINCT game_id FROM release_dates
),
cover_games AS (
    SELECT DISTINCT game_id FROM covers
),
website_games AS (
    SELECT DISTINCT game_id FROM websites
)
SELECT
    COUNT(DISTINCT g.game_id) AS total_games,
    COUNT(DISTINCT gg.game_id) AS games_with_genre,
    COUNT(DISTINCT tg.game_id) AS games_with_theme,
    COUNT(DISTINCT kg.game_id) AS games_with_keyword,
    COUNT(DISTINCT pg.game_id) AS games_with_platform,
    COUNT(DISTINCT cg.game_id) AS games_with_company,
    COUNT(DISTINCT rdg.game_id) AS games_with_release_date,
    COUNT(DISTINCT cov.game_id) AS games_with_cover,
    COUNT(DISTINCT wg.game_id) AS games_with_website
FROM games g
LEFT JOIN genre_games gg
    ON g.game_id = gg.game_id
LEFT JOIN theme_games tg
    ON g.game_id = tg.game_id
LEFT JOIN keyword_games kg
    ON g.game_id = kg.game_id
LEFT JOIN platform_games pg
    ON g.game_id = pg.game_id
LEFT JOIN company_games cg
    ON g.game_id = cg.game_id
LEFT JOIN release_date_games rdg
    ON g.game_id = rdg.game_id
LEFT JOIN cover_games cov
    ON g.game_id = cov.game_id
LEFT JOIN website_games wg
    ON g.game_id = wg.game_id;
```

---

## 14.17 Popularity Signal Availability

```sql
SELECT
    COALESCE(egs.source_name, 'Unknown Source') AS popularity_source,
    COALESCE(pt.name, 'Unknown Popularity Type') AS popularity_type,
    COUNT(DISTINCT pp.game_id) AS games_with_signal,
    COUNT(*) AS signal_records
FROM popularity_primitives pp
LEFT JOIN popularity_types pt
    ON pp.popularity_type_id = pt.popularity_type_id
LEFT JOIN external_game_sources egs
    ON pp.external_popularity_source_id = egs.external_game_source_id
GROUP BY
    COALESCE(egs.source_name, 'Unknown Source'),
    COALESCE(pt.name, 'Unknown Popularity Type')
ORDER BY games_with_signal DESC, signal_records DESC;
```

Important note:

```text
This query describes popularity signal coverage. It does not create a combined popularity score.
```

---

## 14.18 Game Mode Distribution

```sql
SELECT
    gm.name AS game_mode,
    COUNT(DISTINCT gmb.game_id) AS game_count
FROM game_modes_bridge gmb
JOIN game_modes gm
    ON gmb.game_mode_id = gm.game_mode_id
GROUP BY gm.name
ORDER BY game_count DESC, gm.name;
```

Important note:

```text
A game can have multiple game modes. Counts are not mutually exclusive and should not be summed as unique games.
```

---

## 14.19 Multiplayer Support Coverage

```sql
WITH total AS (
    SELECT COUNT(DISTINCT game_id) AS total_games
    FROM games
),
multiplayer_by_game AS (
    SELECT
        game_id,
        MAX(CASE WHEN campaign_coop = 1 THEN 1 ELSE 0 END) AS has_campaign_coop,
        MAX(CASE WHEN drop_in = 1 THEN 1 ELSE 0 END) AS has_drop_in,
        MAX(CASE WHEN lan_coop = 1 THEN 1 ELSE 0 END) AS has_lan_coop,
        MAX(CASE WHEN offline_coop = 1 THEN 1 ELSE 0 END) AS has_offline_coop,
        MAX(CASE WHEN online_coop = 1 THEN 1 ELSE 0 END) AS has_online_coop,
        MAX(CASE WHEN split_screen = 1 THEN 1 ELSE 0 END) AS has_split_screen,
        MAX(CASE
            WHEN COALESCE(offline_coop_max, 0) >= COALESCE(offline_max, 0)
                THEN COALESCE(offline_coop_max, 0)
            ELSE COALESCE(offline_max, 0)
        END) AS max_offline_players,
        MAX(CASE
            WHEN COALESCE(online_coop_max, 0) >= COALESCE(online_max, 0)
                THEN COALESCE(online_coop_max, 0)
            ELSE COALESCE(online_max, 0)
        END) AS max_online_players
    FROM multiplayer_modes
    GROUP BY game_id
)
SELECT 'Games with game mode labels' AS metric,
       COUNT(DISTINCT gmb.game_id) AS game_count,
       (SELECT total_games FROM total) AS total_games,
       ROUND(100.0 * COUNT(DISTINCT gmb.game_id) / (SELECT total_games FROM total), 2) AS pct_of_games
FROM game_modes_bridge gmb

UNION ALL

SELECT 'Games with detailed multiplayer records',
       COUNT(DISTINCT game_id),
       (SELECT total_games FROM total),
       ROUND(100.0 * COUNT(DISTINCT game_id) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with campaign co-op',
       SUM(has_campaign_coop),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_campaign_coop) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with drop-in multiplayer',
       SUM(has_drop_in),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_drop_in) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with LAN co-op',
       SUM(has_lan_coop),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_lan_coop) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with offline/local co-op',
       SUM(has_offline_coop),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_offline_coop) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with online co-op',
       SUM(has_online_coop),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_online_coop) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with split-screen',
       SUM(has_split_screen),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(has_split_screen) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with offline player max above 0',
       SUM(CASE WHEN max_offline_players > 0 THEN 1 ELSE 0 END),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(CASE WHEN max_offline_players > 0 THEN 1 ELSE 0 END) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game

UNION ALL

SELECT 'Games with online player max above 0',
       SUM(CASE WHEN max_online_players > 0 THEN 1 ELSE 0 END),
       (SELECT total_games FROM total),
       ROUND(100.0 * SUM(CASE WHEN max_online_players > 0 THEN 1 ELSE 0 END) / (SELECT total_games FROM total), 2)
FROM multiplayer_by_game;
```

Important note:

```text
Coverage is counted at the game level after summarizing platform-specific multiplayer records. Missing multiplayer detail should be reported as unknown, not as no multiplayer support.
```

---

## 14.20 Player Count Distribution

```sql
WITH multiplayer_by_game AS (
    SELECT
        game_id,
        MAX(CASE
            WHEN COALESCE(offline_coop_max, 0) >= COALESCE(offline_max, 0)
                THEN COALESCE(offline_coop_max, 0)
            ELSE COALESCE(offline_max, 0)
        END) AS max_offline_players,
        MAX(CASE
            WHEN COALESCE(online_coop_max, 0) >= COALESCE(online_max, 0)
                THEN COALESCE(online_coop_max, 0)
            ELSE COALESCE(online_max, 0)
        END) AS max_online_players
    FROM multiplayer_modes
    GROUP BY game_id
),
player_count_long AS (
    SELECT
        'Offline / local max players' AS player_count_type,
        max_offline_players AS max_players
    FROM multiplayer_by_game
    WHERE max_offline_players > 0

    UNION ALL

    SELECT
        'Online max players' AS player_count_type,
        max_online_players AS max_players
    FROM multiplayer_by_game
    WHERE max_online_players > 0
)
SELECT
    player_count_type,
    CASE
        WHEN max_players = 1 THEN '1 player'
        WHEN max_players = 2 THEN '2 players'
        WHEN max_players BETWEEN 3 AND 4 THEN '3-4 players'
        WHEN max_players BETWEEN 5 AND 8 THEN '5-8 players'
        WHEN max_players BETWEEN 9 AND 16 THEN '9-16 players'
        ELSE '17+ players'
    END AS player_count_band,
    COUNT(*) AS game_count
FROM player_count_long
GROUP BY
    player_count_type,
    CASE
        WHEN max_players = 1 THEN '1 player'
        WHEN max_players = 2 THEN '2 players'
        WHEN max_players BETWEEN 3 AND 4 THEN '3-4 players'
        WHEN max_players BETWEEN 5 AND 8 THEN '5-8 players'
        WHEN max_players BETWEEN 9 AND 16 THEN '9-16 players'
        ELSE '17+ players'
    END
ORDER BY
    player_count_type,
    CASE player_count_band
        WHEN '1 player' THEN 1
        WHEN '2 players' THEN 2
        WHEN '3-4 players' THEN 3
        WHEN '5-8 players' THEN 4
        WHEN '9-16 players' THEN 5
        ELSE 6
    END;
```

Important note:

```text
Player-count values represent available IGDB multiplayer metadata. They should not be treated as complete for every game in the sample.
```

---

## 14.21 Player Perspective Distribution

```sql
SELECT
    pp.name AS player_perspective,
    COUNT(DISTINCT gpp.game_id) AS game_count
FROM game_player_perspectives gpp
JOIN player_perspectives pp
    ON gpp.player_perspective_id = pp.player_perspective_id
GROUP BY pp.name
ORDER BY game_count DESC, pp.name;
```

---

## 14.22 Time-to-Beat Coverage and Playtime Bands

```sql
SELECT
    g.game_id,
    g.name,
    ROUND(gtb.hastily / 3600.0, 2) AS hastily_hours,
    ROUND(gtb.normally / 3600.0, 2) AS normally_hours,
    ROUND(gtb.completely / 3600.0, 2) AS completely_hours,
    gtb."count" AS time_to_beat_submission_count
FROM game_time_to_beats gtb
JOIN games g
    ON gtb.game_id = g.game_id
WHERE gtb.normally IS NOT NULL
  AND gtb.normally > 0
ORDER BY normally_hours DESC, g.name;
```

Important note:

```text
Time-to-beat coverage may be sparse, and playtime values can contain extreme outliers. Missing playtime should be reported as unknown, not as zero-length games. For final visuals, use band counts plus median/p95/max hours and a separate outlier-review table instead of relying on average hours.
```

---

## 14.23 Website Type and External Source Coverage

```sql
SELECT
    COALESCE(wt.type_name, 'Unknown Website Type') AS website_type,
    COUNT(*) AS website_records,
    COUNT(DISTINCT w.game_id) AS games_with_website_type
FROM websites w
LEFT JOIN website_types wt
    ON w.website_type_id = wt.website_type_id
GROUP BY COALESCE(wt.type_name, 'Unknown Website Type')
ORDER BY games_with_website_type DESC, website_records DESC;
```

```sql
SELECT
    COALESCE(egs.source_name, 'Unknown External Source') AS external_source,
    COUNT(*) AS external_game_records,
    COUNT(DISTINCT eg.game_id) AS games_with_external_source
FROM external_games eg
LEFT JOIN external_game_sources egs
    ON eg.external_game_source_id = egs.external_game_source_id
GROUP BY COALESCE(egs.source_name, 'Unknown External Source')
ORDER BY games_with_external_source DESC, external_game_records DESC;
```

---

## 14.24 Release Date Precision, Status, and Region Coverage

```sql
SELECT
    COALESCE(df.format_name, 'Unknown Date Format') AS date_format,
    COUNT(*) AS release_date_records,
    COUNT(DISTINCT rd.game_id) AS games_with_date_format
FROM release_dates rd
LEFT JOIN date_formats df
    ON rd.date_format_id = df.date_format_id
GROUP BY COALESCE(df.format_name, 'Unknown Date Format')
ORDER BY games_with_date_format DESC, release_date_records DESC;
```

```sql
SELECT
    COALESCE(rds.status_name, 'Unknown Release Status') AS release_status,
    COUNT(*) AS release_date_records,
    COUNT(DISTINCT rd.game_id) AS games_with_release_status
FROM release_dates rd
LEFT JOIN release_date_statuses rds
    ON rd.release_date_status_id = rds.release_date_status_id
GROUP BY COALESCE(rds.status_name, 'Unknown Release Status')
ORDER BY games_with_release_status DESC, release_date_records DESC;
```

```sql
SELECT
    COALESCE(rdr.region_name, 'Unknown Release Region') AS release_region,
    COUNT(*) AS release_date_records,
    COUNT(DISTINCT rd.game_id) AS games_with_release_region
FROM release_dates rd
LEFT JOIN release_date_regions rdr
    ON rd.release_date_region_id = rdr.release_date_region_id
GROUP BY COALESCE(rdr.region_name, 'Unknown Release Region')
ORDER BY games_with_release_region DESC, release_date_records DESC;
```

---

## 14.25 Text Length and Relationship Richness

```sql
SELECT
    game_id,
    name,
    LENGTH(COALESCE(summary, '')) AS summary_length,
    LENGTH(COALESCE(storyline, '')) AS storyline_length
FROM games;
```

```sql
WITH relationship_counts AS (
    SELECT
        g.game_id,
        g.name,
        (SELECT COUNT(*) FROM game_genres gg WHERE gg.game_id = g.game_id) AS genre_count,
        (SELECT COUNT(*) FROM game_themes gt WHERE gt.game_id = g.game_id) AS theme_count,
        (SELECT COUNT(*) FROM game_keywords gk WHERE gk.game_id = g.game_id) AS keyword_count,
        (SELECT COUNT(*) FROM game_platforms gp WHERE gp.game_id = g.game_id) AS platform_count,
        (SELECT COUNT(*) FROM involved_companies ic WHERE ic.game_id = g.game_id) AS company_count,
        (SELECT COUNT(*) FROM websites w WHERE w.game_id = g.game_id) AS website_count,
        (SELECT COUNT(*) FROM screenshots s WHERE s.game_id = g.game_id) AS screenshot_count
    FROM games g
)
SELECT *
FROM relationship_counts;
```

---

## 14.26 Metadata Richness Bands

```sql
WITH relationship_counts AS (
    SELECT
        g.game_id,
        g.name,
        (SELECT COUNT(*) FROM game_genres gg WHERE gg.game_id = g.game_id) AS genre_count,
        (SELECT COUNT(*) FROM game_themes gt WHERE gt.game_id = g.game_id) AS theme_count,
        (SELECT COUNT(*) FROM game_keywords gk WHERE gk.game_id = g.game_id) AS keyword_count,
        (SELECT COUNT(*) FROM game_platforms gp WHERE gp.game_id = g.game_id) AS platform_count,
        (SELECT COUNT(*) FROM involved_companies ic WHERE ic.game_id = g.game_id) AS company_count,
        (SELECT COUNT(*) FROM game_modes_bridge gmb WHERE gmb.game_id = g.game_id) AS game_mode_count,
        (SELECT COUNT(*) FROM game_player_perspectives gpp WHERE gpp.game_id = g.game_id) AS player_perspective_count,
        (SELECT COUNT(*) FROM websites w WHERE w.game_id = g.game_id) AS website_count,
        (SELECT COUNT(*) FROM external_games eg WHERE eg.game_id = g.game_id) AS external_source_count,
        (SELECT COUNT(*) FROM screenshots s WHERE s.game_id = g.game_id) AS screenshot_count
    FROM games g
),
scored AS (
    SELECT
        *,
        genre_count + theme_count + keyword_count + platform_count + company_count +
        game_mode_count + player_perspective_count + website_count + external_source_count +
        screenshot_count AS metadata_relationship_count
    FROM relationship_counts
)
SELECT
    CASE
        WHEN metadata_relationship_count < 50 THEN 'Lean relationship profile (<50 links)'
        WHEN metadata_relationship_count < 100 THEN 'Moderate relationship profile (50-99 links)'
        WHEN metadata_relationship_count < 150 THEN 'Rich relationship profile (100-149 links)'
        ELSE 'Very rich relationship profile (150+ links)'
    END AS metadata_richness_band,
    COUNT(*) AS game_count,
    MIN(metadata_relationship_count) AS min_relationship_count,
    AVG(metadata_relationship_count) AS avg_relationship_count,
    MAX(metadata_relationship_count) AS max_relationship_count
FROM scored
GROUP BY metadata_richness_band
ORDER BY min_relationship_count;
```

Important note:

```text
A simple yes/no metadata signal score may be too coarse for this 47,835-game
sample. Relationship-count summaries measure linked metadata volume, but their
thresholds should be derived from the observed distribution rather than assumed
to represent objective metadata quality.
```

---

## 14.27 Keyword Cleanup Candidate Table

```sql
SELECT
    kw.name AS keyword_name,
    COUNT(DISTINCT gk.game_id) AS game_count,
    CASE
        WHEN LOWER(kw.name) LIKE '%steam%' THEN 'Store/platform term'
        WHEN LOWER(kw.name) LIKE '%achievement%' THEN 'Achievement/meta term'
        WHEN LOWER(kw.name) LIKE '%troph%' THEN 'Achievement/meta term'
        WHEN LOWER(kw.name) LIKE '%distribution%' THEN 'Store/platform term'
        WHEN LOWER(kw.name) LIKE '%video%' THEN 'Technical/media term'
        WHEN LOWER(kw.name) LIKE '%wasd%' THEN 'Control/input term'
        ELSE 'Potentially semantic term'
    END AS keyword_review_category
FROM game_keywords gk
JOIN keywords kw
    ON gk.keyword_id = kw.keyword_id
GROUP BY kw.name
ORDER BY game_count DESC, kw.name;
```

Important note:

```text
This is a review aid, not a deletion rule. Keywords should not be removed automatically without manual inspection.
```

---

## 14.28 Media Availability and Image Dimension Coverage

```sql
WITH media_by_game AS (
    SELECT
        g.game_id,
        g.name,
        CASE WHEN c.cover_id IS NOT NULL THEN 1 ELSE 0 END AS has_cover_record,
        CASE WHEN c.width IS NOT NULL AND c.height IS NOT NULL THEN 1 ELSE 0 END AS has_cover_dimensions,
        COUNT(s.screenshot_id) AS screenshot_count,
        SUM(CASE WHEN s.width IS NOT NULL AND s.height IS NOT NULL THEN 1 ELSE 0 END) AS screenshots_with_dimensions
    FROM games g
    LEFT JOIN covers c
        ON g.game_id = c.game_id
    LEFT JOIN screenshots s
        ON g.game_id = s.game_id
    GROUP BY g.game_id, g.name, c.cover_id, c.width, c.height
)
SELECT *
FROM media_by_game;
```

---

# 15. Recommended Visuals by Priority

## 15.1 Must-Have Visuals

| Priority | Visual | Purpose |
|---|---|---|
| 1 | KPI cards | Show dataset size and immediate catalog snapshot. |
| 2 | Games by release year | Show historical release coverage. |
| 3 | Top genres | Show broad catalog composition. |
| 4 | Top platforms | Show platform coverage. |
| 5 | Rating distribution | Show quality score profile. |
| 6 | Rating count distribution | Show visibility and rating-confidence skew. |
| 7 | Metadata completeness table | Show limitations and data readiness. |
| 8 | Top developers/publishers | Show company representation. |

## 15.2 Nice-to-Have Visuals

| Visual | Use Case |
|---|---|
| Platform family breakdown | Useful for broad platform filtering. |
| Platform type breakdown | Useful for console vs PC/computer discussion. |
| Game type breakdown | Useful to separate main games from remakes, remasters, ports, and expansions. |
| Theme distribution | Useful for vibe-based recommendation framing. |
| Keyword table | Useful for RAG and semantic discovery. |
| Popularity signal availability | Useful for documenting which source/type popularity signals are present without mixing them into one score. |
| Game mode distribution | Useful for broad play-style coverage such as single-player, multiplayer, co-op, MMO, and battle royale. |
| Multiplayer support coverage | Useful for documenting online co-op, offline/local co-op, split-screen, LAN co-op, and player-count metadata availability. |
| Player count distribution | Useful for showing available max online/offline player counts without treating missing values as no support. |
| Player perspective distribution | Useful for first-person, third-person, side-view, bird-view, and similar play-perspective filtering. |
| Time-to-beat coverage and playtime bands | Useful for documenting whether playtime metadata exists and how long available games usually take. |
| Cover availability | Useful for UI readiness. |
| Website/store link availability | Useful for future external navigation. |
| External source coverage | Useful for understanding which store or external catalog identifiers are available. |
| Release-date precision/status/region coverage | Useful for avoiding overclaims when release metadata is partial or region-specific. |
| Release decade distribution | Easier to interpret than a noisy year-by-year line chart. |
| Text length distribution | Useful for understanding summary/storyline readiness for RAG. |
| Relationship-count richness bands | Useful for separating rich versus sparse game profiles before dashboard or RAG use. |
| Keyword cleanup categories | Useful for reviewing noisy platform, store, technical, or compound keywords. |
| Screenshot count and image dimension coverage | Useful for assessing media readiness for game detail pages. |

---

# 16. Optional Add-On Questions

The current descriptive plan supports both an MVP `Catalog Overview` page and a broader descriptive appendix. The MVP dashboard should still prioritize the clearest visuals first, but the notebook can explore the fuller list below because each question remains descriptive and supports later dashboard, RAG, or recommendation work.

## Recommended Optional Questions

1. Which game modes are most represented?
2. How many games have detailed multiplayer support records?
3. How many games support online co-op, offline/local co-op, split-screen, LAN co-op, campaign co-op, or drop-in multiplayer?
4. What max online/offline player counts are represented when player-count metadata is available?
5. Which player perspectives are most represented?
6. How much time-to-beat metadata is available, and what playtime bands appear?
7. Which website/link types are available for games?
8. Which external source identifiers are available for games?
9. Which release-date statuses, date precisions, and regions appear in the sample?
10. How long are summaries and storylines?
11. Which games have rich versus sparse metadata profiles?
12. Which keywords look like cleanup/review candidates?
13. How many games have screenshots in addition to covers?
14. How complete are cover and screenshot dimensions/URLs?

## Recommended Optional Visuals

| Optional Visual | Why It Helps |
|---|---|
| Game mode distribution | Supports later filters such as single-player, multiplayer, co-op, and MMO. |
| Multiplayer support coverage | Supports later filters for online co-op, offline co-op, split-screen, LAN, and drop-in multiplayer. |
| Player count distribution | Supports later prompts such as two-player co-op, four-player online, or large multiplayer games. |
| Player perspective distribution | Supports later natural-language matching for first-person, third-person, side-view, etc. |
| Time-to-beat coverage and playtime bands | Shows whether playtime data is available and how the available durations are distributed. |
| Website type coverage | Shows whether external navigation/store/social links are available for the UI. |
| External source coverage | Shows which external catalogs or stores can support linking or filtering. |
| Screenshot availability | Helps assess whether game detail pages can include richer media. |
| Screenshot count distribution | Shows whether game detail pages can rely on multiple screenshots or only one/no image. |
| Image dimension coverage | Checks whether media records are ready for consistent UI rendering. |
| Release-date precision/status/region table | Prevents overclaiming exact release dates when IGDB only provides year/month/TBD-style or regional values. |
| Text length distribution | Shows whether summaries/storylines are long enough to support RAG-style retrieval. |
| Relationship-count richness bands | Identifies games with broad versus sparse descriptive metadata. |
| Keyword cleanup categories | Provides a review queue for noisy keywords before they are used as filters or retrieval terms. |

## Scope Guardrail

Avoid adding descriptive charts that try to answer why ratings differ, which genres perform best, or what should be recommended. Those belong to the diagnostic and prescriptive pillars.

---
