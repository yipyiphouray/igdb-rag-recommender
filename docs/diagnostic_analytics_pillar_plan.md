# Diagnostic Analytics Pillar Plan
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Pillar:** Diagnostic Analytics  
**Recommended Dashboard Page:** Hidden Gems & Rating Drivers  
**Current Dataset:** 3,000-game IGDB project sample  
**Recommended Notebook:** `notebooks/02_diagnostic_analytics_exploration.ipynb`  
**Recommended Output Folder:** `data/analytics/diagnostic/`

---

# 1. Purpose of the Diagnostic Pillar

The diagnostic analytics pillar answers the question:

> **Why do certain games, genres, themes, platforms, or companies appear to perform better or receive more visibility than others?**

In this project, â€œperformanceâ€ should not only mean rating score. It should include several related signals:

- Rating quality
- Rating confidence
- Rating activity
- Visibility / popularity
- Hidden-gem potential
- Genre-theme fit
- Platform reach
- Metadata richness
- RAG readiness
- Developer and publisher patterns
- Gameplay and playstyle patterns

The diagnostic pillar should not claim causality. The goal is to identify **associations, patterns, segments, and candidate drivers** that can support the predictive and prescriptive pillars.

Use careful wording:

```text
Good: RPG games in this sample have a higher median rating than some other genres.
Bad: RPG games cause higher ratings.

Good: Games with more platform coverage tend to have higher rating activity.
Bad: Releasing on more platforms causes more popularity.
```

---

# 2. How Diagnostic Differs From Descriptive

The descriptive pillar answered:

> **What does the catalog look like?**

The diagnostic pillar answers:

> **What patterns help explain rating, visibility, and hidden-gem differences?**

| Descriptive Pillar | Diagnostic Pillar |
|---|---|
| Counts games by genre | Compares ratings and hidden-gem share by genre |
| Counts games by platform | Tests whether platform reach relates to visibility |
| Shows rating distribution | Investigates rating vs rating-count relationship |
| Shows metadata completeness | Tests whether metadata richness relates to rating activity |
| Lists top developers/publishers | Compares developer/publisher rating and hidden-gem patterns |
| Summarizes playtime bands | Tests whether playtime bands differ in ratings or visibility |

The key shift is:

```text
Descriptive = summarize
Diagnostic = compare, segment, explain, and identify patterns
```

---

# 3. Diagnostic Main Question and Supporting Questions

## Main Question

> **What factors are associated with rating quality, rating activity, visibility, and hidden-gem potential in the IGDB project sample?**

## Supporting Questions

1. Are higher-rated games also more visible?
2. Is `total_rating_count` a reasonable visibility proxy?
3. Which games are high-rated but relatively less visible?
4. Which genres have stronger median ratings?
5. Which themes have stronger median ratings?
6. Which genre-theme combinations are associated with stronger rating outcomes?
7. Do games available on more platforms receive more rating activity?
8. Do platform families differ in rating or visibility patterns?
9. Are some developers or publishers overrepresented among high-rated games?
10. Does metadata richness relate to rating activity or recommendation readiness?
11. Do game modes, player perspectives, multiplayer support, or playtime bands relate to rating patterns?
12. Which diagnostic findings should become predictive features later?

---

# 4. Updated Dataset Caveat for the 3,000-Game Version

The previous descriptive pillar originally used a 500-game sample. The database has now been rerun successfully with **3,000 games** using a broader generic IGDB pull. This improves diagnostic credibility because there is more variation across ratings, rating counts, platforms, genres, themes, developers, metadata richness, and hidden-gem candidates.

The current extraction uses `GAME_LIMIT = 3000`, sorts games by IGDB `id asc`, and does **not** pre-filter for summaries, rating availability, or rating-count thresholds. This makes the dataset less popularity-biased than the earlier 500-game descriptive sample.

However, the diagnostic results still describe the **project sample**, not the entire IGDB catalog or the full video game market. Rating-dependent analysis must still filter to games with usable rating fields.

Suggested notebook/report caveat:

```markdown
The diagnostic results represent the current 3,000-game IGDB project sample, not the full IGDB catalog or the entire video game market. The current pull is a generic project extraction sorted by IGDB game ID, with no summary, rating-availability, or rating-count pre-filter. Rating, visibility, and hidden-gem findings are therefore based only on the subset of extracted games with usable rating fields and should be interpreted as project-sample findings, not market-wide conclusions.
```

Recommended extraction snapshot table:

| Item | Value |
|---|---:|
| Games | 3,000 |
| Database | `data/database/igdb_games.db` |
| Diagnostic output folder | `data/analytics/diagnostic/` |
| Extraction method | Generic project pull |
| Base sort | `id asc` |
| Summary/rating pre-filters | None |
| Rating field | `games.total_rating` |
| Rating confidence field | `games.total_rating_count` |
| Main quality threshold | `total_rating >= 80` |
| Main visibility proxy | `total_rating_count` |
| Hidden-gem threshold | Percentile-based |

---

# 5. Required Business Rules for Diagnostic Analytics

The diagnostic pillar should follow the existing database business rules and value mappings. This protects the analysis from incorrect joins, inflated counts, and misleading interpretations.

## 5.1 Central Entity Rule

The `games` table is the central entity. Most diagnostic outputs should start from `games` and join outward to supporting tables.

Core supporting tables include:

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
websites
external_games
popularity_primitives
game_time_to_beats
multiplayer_modes
```

## 5.2 Rating-Based Analysis Rule

For rating-based diagnostic analysis, use:

```sql
WHERE total_rating IS NOT NULL
  AND total_rating_count IS NOT NULL
```

Games with missing ratings may remain in the database, but they should not be included in rating-based diagnostics or labeled as highly rated.

## 5.3 Rating Reliability Rule

Use a minimum rating-count threshold when interpreting ratings.

Recommended default:

```text
total_rating_count >= 10
```

Create separate diagnostic datasets instead of using one filtered table for every analysis:

| Sample | Rule | Use |
|---|---|---|
| All-game base | No rating filter | Metadata coverage, RAG readiness, descriptive carryover, and feature availability |
| Rating-available sample | `total_rating IS NOT NULL` | Broad rating coverage summaries |
| Rating-reliable sample | `total_rating IS NOT NULL AND total_rating_count >= 10` | Main diagnostic analysis |
| Hidden-gem eligible sample | Rating-reliable sample, optionally `game_type_name = 'Main Game'` | Hidden-gem percentile thresholds and candidate selection |

Do not build `diagnostic_game_base` by filtering out unrated games. Build the base at one row per game first, then create rating-specific subsets from it. Otherwise, RAG readiness and metadata richness analysis would silently exclude games that are useful for recommendation but do not have rating data.

## 5.4 High-Rated Rule

Use the project rule:

```text
high_rated = 1 if total_rating >= 80
high_rated = 0 if total_rating < 80
```

Recommended diagnostic filter:

```text
total_rating IS NOT NULL
AND total_rating_count >= 10
```

## 5.5 Platform Availability Rule

Use `game_platforms` to determine platform availability.

Correct logic:

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

Do not infer platform availability from `release_dates` alone. Use `release_dates` for platform-specific release timing, not availability.

## 5.6 Company Role Rule

Only use:

```sql
developer = 1
```

for developer analysis.

Only use:

```sql
publisher = 1
```

for publisher analysis.

Do not treat every involved company as a developer or publisher. A company can also have multiple roles for the same game.

## 5.7 Many-to-Many Counting Rule

Games can have multiple genres, themes, keywords, platforms, modes, perspectives, companies, and release dates.

For group-level counts, use:

```sql
COUNT(DISTINCT game_id)
```

Do not sum category counts as if categories are mutually exclusive.

---

# 6. Recommended Diagnostic Deliverables

By the end of the diagnostic pillar, produce:

```text
notebooks/02_diagnostic_analytics_exploration.ipynb
data/analytics/diagnostic/*.csv
docs/diagnostic_analytics_pillar_plan.md
optional Streamlit page: Hidden Gems & Rating Drivers
```

Recommended exported CSVs:

```text
diagnostic_dataset_snapshot.csv
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
rating_visibility_correlation.csv
rating_band_visibility_summary.csv
hidden_gem_candidates.csv
hidden_gem_threshold_summary.csv
hidden_gem_sensitivity_analysis.csv
hidden_gem_by_genre.csv
hidden_gem_by_theme.csv
hidden_gem_by_platform_family.csv
genre_rating_summary.csv
theme_rating_summary.csv
genre_theme_rating_summary.csv
platform_reach_summary.csv
platform_family_rating_summary.csv
platform_type_rating_summary.csv
developer_rating_summary.csv
publisher_rating_summary.csv
metadata_richness_rating_summary.csv
metadata_richness_visibility_summary.csv
rag_readiness_summary.csv
game_mode_rating_summary.csv
player_perspective_rating_summary.csv
multiplayer_support_rating_summary.csv
playtime_rating_summary.csv
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
diagnostic_feature_recommendations.csv
diagnostic_takeaways.csv
```

---

# 7. Recommended Notebook Structure

Notebook path:

```text
notebooks/02_diagnostic_analytics_exploration.ipynb
```

Recommended sections:

```text
1. Imports and configuration
2. Connect to SQLite database
3. Validate diagnostic dataset
4. Build all-game diagnostic base table
5. Derive rating-available, rating-reliable, and hidden-gem eligible samples
6. Rating vs visibility analysis
7. Hidden gem logic
8. Genre rating diagnostics
9. Theme rating diagnostics
10. Genre-theme interaction diagnostics
11. Platform and reach diagnostics
12. Developer and publisher diagnostics
13. Metadata richness and RAG readiness diagnostics
14. Gameplay, player perspective, multiplayer, and playtime diagnostics
15. Popularity primitive diagnostics
16. Diagnostic-to-predictive feature recommendations
17. Export CSV outputs
18. Final diagnostic takeaways and limitations
```

---

# 8. Section 1 â€” Imports, Configuration, and Database Connection

## Purpose

Set up the notebook cleanly and make it reproducible.

Recommended Python setup:

```python
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DB_PATH = Path("../data/database/igdb_games.db")
OUTPUT_DIR = Path("../data/analytics/diagnostic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
```

Recommended notebook constants:

```python
QUALITY_THRESHOLD = 80
MIN_RATING_COUNT = 10
HIDDEN_GEM_VISIBILITY_PERCENTILE = 0.40
MAIN_GAME_ONLY = True
```

These constants make the notebook easier to adjust later.

---

# 9. Section 2 â€” Diagnostic Dataset Validation

## Purpose

Before doing diagnostic analysis, confirm that the database is healthy and that the 3,000-game sample has enough usable records.

Run a short validation block:

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating,
    SUM(CASE WHEN total_rating_count IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating_count,
    SUM(CASE WHEN total_rating IS NOT NULL AND total_rating_count >= 10 THEN 1 ELSE 0 END) AS rating_reliable_games,
    SUM(CASE WHEN total_rating >= 80 AND total_rating_count >= 10 THEN 1 ELSE 0 END) AS high_rated_games
FROM games;
```

Also run or reference the existing data quality checks:

- SQLite integrity check
- Foreign key check
- Empty core table check
- Duplicate primary key check
- Duplicate bridge relationship check
- Required game name check
- Rating range check
- Non-negative rating count check
- Release month/day validity check

Export:

```text
diagnostic_dataset_snapshot.csv
```

---

# 10. Section 3 â€” Build Diagnostic Game Base

## Purpose

Create one row per game with derived fields needed across the diagnostic notebook.

This is the most important diagnostic artifact.

## Grain

```text
One row per game
```

## Fields to Include

```text
game_id
name
release_year
total_rating
total_rating_count
rating
rating_count
aggregated_rating
aggregated_rating_count
game_type_name
game_status_name
num_genres
num_themes
num_keywords
num_platforms
num_companies
num_release_dates
num_websites
num_external_sources
num_screenshots
has_storyline
summary_length
storyline_length
relationship_count
metadata_richness_band
rating_band
rating_available_flag
rating_reliable_flag
high_rated_flag
main_game_flag
rag_ready_flag
```

`diagnostic_game_base.csv` should keep all extracted games. Add `log_total_rating_count` and hidden-gem visibility percentiles after loading this SQL result into pandas.

## SQL

```sql
WITH genre_counts AS (
    SELECT game_id, COUNT(DISTINCT genre_id) AS num_genres
    FROM game_genres
    GROUP BY game_id
),
theme_counts AS (
    SELECT game_id, COUNT(DISTINCT theme_id) AS num_themes
    FROM game_themes
    GROUP BY game_id
),
keyword_counts AS (
    SELECT game_id, COUNT(DISTINCT keyword_id) AS num_keywords
    FROM game_keywords
    GROUP BY game_id
),
platform_counts AS (
    SELECT game_id, COUNT(DISTINCT platform_id) AS num_platforms
    FROM game_platforms
    GROUP BY game_id
),
company_counts AS (
    SELECT game_id, COUNT(DISTINCT company_id) AS num_companies
    FROM involved_companies
    GROUP BY game_id
),
release_counts AS (
    SELECT game_id, COUNT(DISTINCT release_date_id) AS num_release_dates
    FROM release_dates
    GROUP BY game_id
),
website_counts AS (
    SELECT game_id, COUNT(DISTINCT website_id) AS num_websites
    FROM websites
    GROUP BY game_id
),
external_counts AS (
    SELECT game_id, COUNT(DISTINCT external_game_id) AS num_external_sources
    FROM external_games
    GROUP BY game_id
),
screenshot_counts AS (
    SELECT game_id, COUNT(DISTINCT screenshot_id) AS num_screenshots
    FROM screenshots
    GROUP BY game_id
),
base AS (
    SELECT
        g.game_id,
        g.name,
        g.release_year,
        g.total_rating,
        g.total_rating_count,
        g.rating,
        g.rating_count,
        g.aggregated_rating,
        g.aggregated_rating_count,
        gt.type_name AS game_type_name,
        gs.status_name AS game_status_name,

        COALESCE(gc.num_genres, 0) AS num_genres,
        COALESCE(tc.num_themes, 0) AS num_themes,
        COALESCE(kc.num_keywords, 0) AS num_keywords,
        COALESCE(pc.num_platforms, 0) AS num_platforms,
        COALESCE(cc.num_companies, 0) AS num_companies,
        COALESCE(rc.num_release_dates, 0) AS num_release_dates,
        COALESCE(wc.num_websites, 0) AS num_websites,
        COALESCE(ec.num_external_sources, 0) AS num_external_sources,
        COALESCE(sc.num_screenshots, 0) AS num_screenshots,

        CASE 
            WHEN g.storyline IS NOT NULL AND TRIM(g.storyline) <> '' THEN 1 
            ELSE 0 
        END AS has_storyline,

        LENGTH(g.summary) AS summary_length,
        LENGTH(g.storyline) AS storyline_length,

        (
            COALESCE(gc.num_genres, 0)
          + COALESCE(tc.num_themes, 0)
          + COALESCE(kc.num_keywords, 0)
          + COALESCE(pc.num_platforms, 0)
          + COALESCE(cc.num_companies, 0)
          + COALESCE(rc.num_release_dates, 0)
          + COALESCE(wc.num_websites, 0)
          + COALESCE(ec.num_external_sources, 0)
          + COALESCE(sc.num_screenshots, 0)
        ) AS relationship_count,

        CASE
            WHEN g.total_rating IS NULL THEN 'Unrated'
            WHEN g.total_rating >= 90 THEN 'Excellent'
            WHEN g.total_rating >= 80 THEN 'Highly rated'
            WHEN g.total_rating >= 70 THEN 'Good'
            WHEN g.total_rating >= 60 THEN 'Mixed / average'
            ELSE 'Lower rated'
        END AS rating_band,

        CASE
            WHEN g.total_rating IS NOT NULL
             AND g.total_rating_count IS NOT NULL THEN 1
            ELSE 0
        END AS rating_available_flag,

        CASE
            WHEN g.total_rating IS NOT NULL
             AND g.total_rating_count >= 10 THEN 1
            ELSE 0
        END AS rating_reliable_flag,

        CASE
            WHEN g.total_rating IS NULL THEN NULL
            WHEN g.total_rating >= 80 THEN 1
            ELSE 0
        END AS high_rated_flag,

        CASE
            WHEN gt.type_name = 'Main Game' THEN 1
            ELSE 0
        END AS main_game_flag,

        CASE
            WHEN g.summary IS NOT NULL AND TRIM(g.summary) <> ''
             AND COALESCE(gc.num_genres, 0) >= 1
             AND COALESCE(tc.num_themes, 0) >= 1
             AND COALESCE(pc.num_platforms, 0) >= 1
            THEN 1
            ELSE 0
        END AS rag_ready_flag

    FROM games g
    LEFT JOIN game_types gt
        ON g.game_type_id = gt.game_type_id
    LEFT JOIN game_statuses gs
        ON g.game_status_id = gs.game_status_id
    LEFT JOIN genre_counts gc
        ON g.game_id = gc.game_id
    LEFT JOIN theme_counts tc
        ON g.game_id = tc.game_id
    LEFT JOIN keyword_counts kc
        ON g.game_id = kc.game_id
    LEFT JOIN platform_counts pc
        ON g.game_id = pc.game_id
    LEFT JOIN company_counts cc
        ON g.game_id = cc.game_id
    LEFT JOIN release_counts rc
        ON g.game_id = rc.game_id
    LEFT JOIN website_counts wc
        ON g.game_id = wc.game_id
    LEFT JOIN external_counts ec
        ON g.game_id = ec.game_id
    LEFT JOIN screenshot_counts sc
        ON g.game_id = sc.game_id
)
SELECT
    *,
    CASE
        WHEN relationship_count < 50 THEN 'Lean relationship profile'
        WHEN relationship_count BETWEEN 50 AND 99 THEN 'Moderate relationship profile'
        WHEN relationship_count BETWEEN 100 AND 149 THEN 'Rich relationship profile'
        ELSE 'Very rich relationship profile'
    END AS metadata_richness_band

FROM base;
```

## Python-Derived Fields and Rating Subsets

After loading the SQL result into pandas, derive the log rating count and rating-specific subsets in Python:

```python
diagnostic_game_base["log_total_rating_count"] = np.log1p(
    diagnostic_game_base["total_rating_count"]
)

rating_available = diagnostic_game_base[
    diagnostic_game_base["rating_available_flag"] == 1
].copy()

rating_reliable = diagnostic_game_base[
    diagnostic_game_base["rating_reliable_flag"] == 1
].copy()

def percent_rank(series):
    if len(series) <= 1:
        return pd.Series(0.0, index=series.index)
    return (series.rank(method="min") - 1) / (len(series) - 1)

rating_reliable["visibility_percentile_rating_reliable"] = percent_rank(
    rating_reliable["total_rating_count"]
)

hidden_gem_eligible = rating_reliable.copy()
if MAIN_GAME_ONLY:
    hidden_gem_eligible = hidden_gem_eligible[
        hidden_gem_eligible["main_game_flag"] == 1
    ].copy()

hidden_gem_eligible["visibility_percentile_eligible_pool"] = percent_rank(
    hidden_gem_eligible["total_rating_count"]
)
```

This prevents two common mistakes:

- RAG readiness and metadata richness analysis should not exclude unrated games.
- Rating-vs-visibility percentiles should be calculated within the rating-reliable pool.
- Hidden-gem visibility percentiles should be recalculated within the hidden-gem eligible pool, not reused from every extracted game.

Export:

```text
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
```

---

# 11. Section 4 â€” Rating vs Visibility Analysis

## Main Question

> Are highly rated games also the most visible games?

## Why It Matters

The project problem includes popularity bias. If visibility and quality are not identical, the recommendation system should not simply rank by rating count or popularity.

## Metrics

```text
total_rating
total_rating_count
log_total_rating_count
visibility_percentile_rating_reliable
rating_band
```

## Analysis 4.1 â€” Scatter Plot: Rating vs Rating Count

Chart:

```text
x-axis: log_total_rating_count
y-axis: total_rating
color: rating_band
tooltip: game name
```

Interpretation:

```markdown
This chart compares rating quality against rating activity. It helps show whether high ratings and high visibility are the same thing or whether some games have strong ratings despite lower rating activity.
```

## Analysis 4.2 â€” Correlation

Calculate:

```python
pearson_corr = df["total_rating"].corr(df["log_total_rating_count"], method="pearson")
spearman_corr = df["total_rating"].corr(df["total_rating_count"], method="spearman")
```

Export:

```text
rating_visibility_correlation.csv
```

Interpretation guide:

| Correlation | Interpretation |
|---:|---|
| Near 0 | Rating and visibility are weakly related |
| 0.20â€“0.40 | Mild/moderate relationship |
| 0.40â€“0.60 | Meaningful relationship |
| 0.60+ | Strong relationship |

Use Spearman as the main discussion metric because rating counts are usually skewed.

## Analysis 4.3 â€” Rating Band Visibility Summary

Group by:

```text
rating_band
```

Metrics:

```text
game_count
median_total_rating_count
mean_total_rating_count
p75_total_rating_count
max_total_rating_count
```

This answers:

```text
Do excellent games tend to have more rating activity than merely good games?
```

Export:

```text
rating_band_visibility_summary.csv
```

---

# 12. Section 5 â€” Hidden Gem Identification

## Main Question

> Which games are high-rated but relatively less visible?

This is one of the most important diagnostic outputs because it directly supports the future recommendation engine.

## Hidden Gem Definition

Use a percentile-based definition:

```text
hidden_gem = total_rating >= 80
             AND total_rating_count >= minimum_confidence_count
             AND visibility_percentile_eligible_pool <= 0.40
             AND main_game_flag = 1
```

Recommended current setting:

```text
quality_threshold = 80
minimum_confidence_count = 10
low_visibility_threshold = 40th percentile
main game only = yes
```

Because the database now contains 3,000 games, the 40th percentile is more meaningful than it was with 500 games.

Important implementation rule:

```text
Calculate the visibility percentile after filtering to the hidden-gem eligible pool.
```

For the MVP, that pool should be:

```text
total_rating IS NOT NULL
AND total_rating_count >= 10
AND game_type_name = 'Main Game'
```

This keeps "bottom 40% visibility" meaningful among the games that could actually become hidden-gem candidates.

## Hidden Gem Variants

Create a sensitivity table:

| Version | Rule | Purpose |
|---|---|---|
| Conservative | `total_rating >= 85` and visibility <= 25th percentile | Smallest, strongest list |
| Balanced | `total_rating >= 80` and visibility <= 40th percentile | Main MVP definition |
| Broad | `total_rating >= 75` and visibility <= 50th percentile | Discovery-friendly version |

Use **Balanced** as the main project definition.

## Hidden Gem Score

Create a continuous score:

```text
hidden_gem_score =
    0.60 * normalized_rating_score
  + 0.30 * inverse_visibility_score
  + 0.10 * metadata_readiness_score
```

Where:

```text
normalized_rating_score = total_rating / 100
inverse_visibility_score = 1 - visibility_percentile_eligible_pool
metadata_readiness_score = scaled relationship_count
```

The binary flag is good for reporting. The score is better for future ranking.

## Recommended Hidden Gem Table Columns

```text
game_id
name
total_rating
total_rating_count
visibility_percentile_eligible_pool
hidden_gem_score
release_year
game_type_name
num_genres
num_themes
num_keywords
num_platforms
metadata_richness_band
genres
themes
platforms
```

## Python Skeleton

```python
hidden_gems = hidden_gem_eligible.copy()

hidden_gems["normalized_rating_score"] = hidden_gems["total_rating"] / 100.0
hidden_gems["inverse_visibility_score"] = (
    1.0 - hidden_gems["visibility_percentile_eligible_pool"]
)
hidden_gems["metadata_readiness_score"] = np.select(
    [
        hidden_gems["relationship_count"] >= 150,
        hidden_gems["relationship_count"] >= 100,
        hidden_gems["relationship_count"] >= 50,
    ],
    [1.0, 0.75, 0.50],
    default=0.25,
)

hidden_gems["hidden_gem_score"] = (
    0.60 * hidden_gems["normalized_rating_score"]
    + 0.30 * hidden_gems["inverse_visibility_score"]
    + 0.10 * hidden_gems["metadata_readiness_score"]
)

hidden_gems["hidden_gem_flag"] = (
    (hidden_gems["total_rating"] >= QUALITY_THRESHOLD)
    & (
        hidden_gems["visibility_percentile_eligible_pool"]
        <= HIDDEN_GEM_VISIBILITY_PERCENTILE
    )
).astype(int)
```

Use `hidden_gem_eligible` rather than the full `diagnostic_game_base` so the percentile threshold is calculated on the same population used for candidate selection.

## Visuals

| Visual | Purpose |
|---|---|
| Scatter plot with hidden gems highlighted | Shows high-rating/low-visibility candidates |
| Top hidden gems table | Actionable game discovery output |
| Hidden gems by genre | Shows where hidden gems cluster |
| Hidden gems by theme | Connects to vibe-based discovery |
| Hidden gems by platform family | Useful for platform-constrained recommendations |

## Exports

```text
hidden_gem_candidates.csv
hidden_gem_threshold_summary.csv
hidden_gem_sensitivity_analysis.csv
hidden_gem_by_genre.csv
hidden_gem_by_theme.csv
hidden_gem_by_platform_family.csv
```

---

# 13. Section 6 â€” Genre Rating Diagnostics

## Main Question

> Which genres are associated with stronger rating outcomes?

Genres are broad gameplay categories and are important for both analytics and recommendation matching.

## Important Grain Rule

A game can have multiple genres. Always use:

```sql
COUNT(DISTINCT game_id)
```

## Metrics by Genre

```text
genre_name
game_count
median_total_rating
mean_total_rating
rating_iqr
median_total_rating_count
high_rated_count
high_rated_share
hidden_gem_count
hidden_gem_share
```

## Recommended Minimum Group Size

Since the dataset now has 3,000 games:

```text
genre game_count >= 25
```

For smaller genres, still export them but mark them as low-sample.

## SQL Skeleton

```sql
SELECT
    ge.name AS genre_name,
    COUNT(DISTINCT g.game_id) AS game_count,
    AVG(g.total_rating) AS mean_total_rating,
    AVG(g.total_rating_count) AS mean_total_rating_count,
    SUM(CASE WHEN g.total_rating >= 80 THEN 1 ELSE 0 END) AS high_rated_count,
    SUM(CASE WHEN g.total_rating >= 80 THEN 1 ELSE 0 END) * 1.0
        / COUNT(DISTINCT g.game_id) AS high_rated_share
FROM games g
JOIN game_genres gg
    ON g.game_id = gg.game_id
JOIN genres ge
    ON gg.genre_id = ge.genre_id
WHERE g.total_rating IS NOT NULL
  AND g.total_rating_count IS NOT NULL
GROUP BY ge.name
HAVING COUNT(DISTINCT g.game_id) >= 25
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

Use Python/Pandas for median and IQR if SQLite percentile functions are unavailable.

## Visuals

| Visual | Purpose |
|---|---|
| Boxplot: rating by genre | Shows distribution, not just average |
| Bar chart: median rating by genre | Easy dashboard view |
| Bar chart: high-rated share by genre | Better than mean alone |
| Bar chart: hidden-gem share by genre | Identifies discovery-rich genres |

## Interpretation Style

```markdown
In the current 3,000-game IGDB sample, [genre] has a higher median total rating than [genre]. This suggests the genre may be associated with stronger rating outcomes in the project dataset, but this does not prove the genre causes higher ratings.
```

Export:

```text
genre_rating_summary.csv
```

---

# 14. Section 7 â€” Theme Rating Diagnostics

## Main Question

> Which themes are associated with stronger rating outcomes or hidden-gem potential?

Themes are especially important because this project is about vibe-based discovery. Themes capture high-level mood, setting, or subject, such as fantasy, sci-fi, horror, survival, mystery, and comedy.

## Metrics by Theme

```text
theme_name
game_count
median_total_rating
mean_total_rating
median_total_rating_count
high_rated_count
high_rated_share
hidden_gem_count
hidden_gem_share
```

## Minimum Group Size

```text
theme game_count >= 25
```

## Visuals

| Visual | Purpose |
|---|---|
| Boxplot: rating by theme | Compare rating distributions |
| Bar chart: high-rated share by theme | Identify themes with stronger quality patterns |
| Bar chart: hidden-gem share by theme | Identify themes with discovery opportunity |
| Scatter: theme median rating vs median rating count | Quality vs visibility by theme |

## Diagnostic Interpretation

This section should connect strongly to the RAG chatbot. If certain themes have high hidden-gem shares, those themes could receive a small boost in the recommendation engine when they match user prompts.

Export:

```text
theme_rating_summary.csv
hidden_gem_by_theme.csv
```

---

# 15. Section 8 â€” Genre-Theme Combination Diagnostics

## Main Question

> Which genre-theme combinations are associated with stronger ratings or hidden-gem potential?

This is one of the most valuable diagnostic sections because users rarely ask for only a genre. They ask for combinations like:

```text
cozy adventure
dark fantasy RPG
sci-fi exploration
horror survival
relaxing puzzle game
```

## Recommended Grain

```text
One row per game-genre-theme relationship
```

## Metrics

```text
genre_name
theme_name
game_count
median_total_rating
mean_total_rating
high_rated_share
hidden_gem_share
median_total_rating_count
```

## Minimum Group Size

Since the dataset now has 3,000 games:

```text
genre-theme game_count >= 10
```

If too many combinations disappear, lower the threshold to 5 and clearly label those outputs as exploratory.

## SQL Skeleton

```sql
SELECT
    ge.name AS genre_name,
    th.name AS theme_name,
    COUNT(DISTINCT g.game_id) AS game_count,
    AVG(g.total_rating) AS mean_total_rating,
    SUM(CASE WHEN g.total_rating >= 80 THEN 1 ELSE 0 END) * 1.0
        / COUNT(DISTINCT g.game_id) AS high_rated_share
FROM games g
JOIN game_genres gg
    ON g.game_id = gg.game_id
JOIN genres ge
    ON gg.genre_id = ge.genre_id
JOIN game_themes gt
    ON g.game_id = gt.game_id
JOIN themes th
    ON gt.theme_id = th.theme_id
WHERE g.total_rating IS NOT NULL
  AND g.total_rating_count IS NOT NULL
GROUP BY ge.name, th.name
HAVING COUNT(DISTINCT g.game_id) >= 10
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

## Visuals

| Visual | Purpose |
|---|---|
| Heatmap: median rating by genre-theme | Shows strong combinations |
| Heatmap: high-rated share by genre-theme | Better for classification framing |
| Table: top genre-theme combinations | Useful for final report |
| Table: hidden-gem rich combinations | Useful for recommender logic |

Export:

```text
genre_theme_rating_summary.csv
```

---

# 16. Section 9 â€” Platform and Reach Diagnostics

## Main Question

> Does platform availability relate to visibility or rating quality?

Platform is important because the final recommendation engine must respect platform constraints.

## Analysis 9.1 â€” Number of Platforms vs Visibility

Question:

```text
Are games available on more platforms more visible?
```

Metrics:

```text
num_platforms
total_rating_count
log_total_rating_count
```

Visuals:

```text
Scatter plot: num_platforms vs log_total_rating_count
Boxplot: log_total_rating_count by platform reach band
```

Suggested platform reach bands:

```text
1 platform
2â€“3 platforms
4â€“6 platforms
7+ platforms
```

## Analysis 9.2 â€” Number of Platforms vs Rating

Question:

```text
Are multi-platform games rated differently from single-platform games?
```

Visual:

```text
Boxplot: total_rating by platform reach band
```

## Analysis 9.3 â€” Platform Family Patterns

Group by platform family:

```text
PlayStation
Xbox
Nintendo
Other / Unknown
```

Also consider PC/computer platforms using platform type or specific platform labels.

Metrics:

```text
platform_family
game_count
median_total_rating
median_total_rating_count
high_rated_share
hidden_gem_share
```

## Analysis 9.4 â€” Platform Type Patterns

Group by:

```text
Console
Computer
Operating System
Portable Console
Arcade
Unknown
```

## Caveat

```markdown
Platform groups overlap because one game can appear on multiple platforms or platform families. These counts represent platform relationships and should not be summed as unique games across all categories.
```

Exports:

```text
platform_reach_summary.csv
platform_family_rating_summary.csv
platform_type_rating_summary.csv
hidden_gem_by_platform_family.csv
```

---

# 17. Section 10 â€” Developer and Publisher Diagnostics

## Main Question

> Which developers and publishers are associated with stronger rating outcomes or hidden-gem candidates?

## Challenge

Even with 3,000 games, company analysis can be noisy. Some developers may only appear once or twice.

## Minimum Group Size

Recommended:

```text
developer_game_count >= 5
publisher_game_count >= 5
```

For an exploratory appendix:

```text
company_game_count >= 3
```

## Developer Metrics

```text
developer_name
game_count
median_total_rating
mean_total_rating
median_total_rating_count
high_rated_count
high_rated_share
hidden_gem_count
hidden_gem_share
example_titles
```

## Publisher Metrics

Use the same structure as developer metrics.

## SQL: Developer Summary

```sql
SELECT
    c.name AS developer_name,
    COUNT(DISTINCT g.game_id) AS game_count,
    AVG(g.total_rating) AS mean_total_rating,
    AVG(g.total_rating_count) AS mean_total_rating_count,
    SUM(CASE WHEN g.total_rating >= 80 THEN 1 ELSE 0 END) AS high_rated_count,
    SUM(CASE WHEN g.total_rating >= 80 THEN 1 ELSE 0 END) * 1.0
        / COUNT(DISTINCT g.game_id) AS high_rated_share
FROM games g
JOIN involved_companies ic
    ON g.game_id = ic.game_id
JOIN companies c
    ON ic.company_id = c.company_id
WHERE ic.developer = 1
  AND g.total_rating IS NOT NULL
  AND g.total_rating_count IS NOT NULL
GROUP BY c.name
HAVING COUNT(DISTINCT g.game_id) >= 5
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

## Visuals

| Visual | Purpose |
|---|---|
| Bar chart: high-rated share by developer | Shows developer quality pattern |
| Bar chart: high-rated share by publisher | Shows publisher pattern |
| Table: hidden gems by developer | Useful for recommendation storytelling |
| Scatter: company game count vs median rating | Avoids overclaiming small samples |

## Interpretation Caveat

```markdown
Company-level results are exploratory because the number of games per company varies widely. Developers or publishers with small sample sizes should not be interpreted as consistently stronger performers.
```

Exports:

```text
developer_rating_summary.csv
publisher_rating_summary.csv
```

---

# 18. Section 11 â€” Metadata Richness and RAG Readiness Diagnostics

## Main Question

> Are metadata-rich games more visible, more highly rated, or more useful for RAG?

This is very important because the recommendation system and RAG chatbot depend on strong metadata.

## Metadata Richness Fields

Use:

```text
relationship_count
metadata_richness_band
num_genres
num_themes
num_keywords
num_platforms
num_companies
num_websites
num_external_sources
summary_length
storyline_length
has_storyline
rag_ready_flag
```

## Analysis 11.1 â€” Metadata Richness vs Visibility

Question:

```text
Do metadata-rich games have higher rating activity?
```

Visual:

```text
Boxplot: log_total_rating_count by metadata_richness_band
```

Metrics:

```text
metadata_richness_band
game_count
median_total_rating_count
mean_total_rating_count
p75_total_rating_count
```

## Analysis 11.2 â€” Metadata Richness vs Rating

Question:

```text
Do metadata-rich games have higher ratings?
```

Visual:

```text
Boxplot: total_rating by metadata_richness_band
```

Metrics:

```text
metadata_richness_band
median_total_rating
high_rated_share
hidden_gem_share
```

## Analysis 11.3 â€” Text Richness

Compare:

```text
has_storyline = 1 vs 0
summary length bands
storyline length bands
```

Against:

```text
total_rating
total_rating_count
high_rated_flag
hidden_gem_flag
```

## Analysis 11.4 â€” RAG Readiness

Suggested rule:

```text
rag_ready = summary exists
            AND num_genres >= 1
            AND num_themes >= 1
            AND num_platforms >= 1
```

This directly supports the later game profile document and vector embedding layer.

Exports:

```text
metadata_richness_rating_summary.csv
metadata_richness_visibility_summary.csv
rag_readiness_summary.csv
```

---

# 19. Section 12 â€” Gameplay, Player Perspective, Multiplayer, and Playtime Diagnostics

## Main Question

> Do gameplay format, perspective, multiplayer support, or playtime relate to rating quality or visibility?

Compare gameplay fields against:

```text
total_rating
total_rating_count
high_rated_flag
hidden_gem_flag
```

## Analysis 12.1 â€” Game Mode Rating Patterns

Game modes may include:

```text
Single player
Multiplayer
Co-operative
Split screen
MMO
Battle Royale
```

Metrics:

```text
game_mode_name
game_count
median_total_rating
median_total_rating_count
high_rated_share
hidden_gem_share
```

## Analysis 12.2 â€” Player Perspective Rating Patterns

Player perspectives may include:

```text
Third person
First person
Bird view / Isometric
Side view
Virtual Reality
Text
Auditory
```

Minimum group size:

```text
game_count >= 20
```

## Analysis 12.3 â€” Multiplayer Support

Compare:

```text
has_campaign_coop
has_online_coop
has_offline_coop
has_split_screen
has_multiplayer_detail
```

Against:

```text
median_total_rating
median_total_rating_count
high_rated_share
hidden_gem_share
```

Important rule:

```markdown
Missing multiplayer records should mean unknown, not â€œno multiplayer.â€
```

## Analysis 12.4 â€” Playtime Bands

Use `game_time_to_beats.normally` as the default playtime measure and convert seconds to hours.

Suggested playtime bands:

```text
Very short: 0â€“5 hours
Short: 5â€“15 hours
Medium: 15â€“30 hours
Long: 30â€“60 hours
Very long: 60+ hours
Unknown
```

Metrics:

```text
playtime_band
game_count
median_total_rating
median_total_rating_count
high_rated_share
hidden_gem_share
```

Caveat:

```markdown
Playtime analysis should be interpreted carefully because live-service and open-ended games can create extreme playtime outliers.
```

Exports:

```text
game_mode_rating_summary.csv
player_perspective_rating_summary.csv
multiplayer_support_rating_summary.csv
playtime_rating_summary.csv
```

---

# 20. Section 13 â€” Popularity Primitive Diagnostics

## Main Question

> Are IGDB popularity signals available and useful beyond rating count?

Use `total_rating_count` as the main visibility proxy for MVP diagnostic analysis.

Use `popularity_primitives` only as a secondary analysis:

```text
availability by popularity type
availability by source
latest popularity snapshot per game
correlation with total_rating_count, if comparable within type/source
```

Do **not** create one combined popularity score by simply averaging all popularity primitive values.

Popularity primitive values must be interpreted with:

```text
game_id
external_popularity_source_id
popularity_type_id
calculated_at
```

Different sources or popularity types should not be treated as equivalent without normalization.

Useful exports:

```text
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
```

---

# 21. Section 14 â€” Diagnostic-to-Predictive Feature Recommendations

This section bridges the diagnostic pillar to the predictive pillar.

Create a table like this:

| Diagnostic Finding | Candidate Predictive Feature | Use? | Reason |
|---|---|---:|---|
| Rating count is skewed | `log_total_rating_count` | Conditional | Useful for visibility/recommendation scoring, but avoid as a quality predictor if the model is meant to score games before rating activity exists |
| Genre high-rated share differs | Genre one-hot encoding | Yes | Captures structured quality pattern |
| Theme high-rated share differs | Theme one-hot encoding | Yes | Supports vibe-based quality patterns |
| Platform reach relates to visibility | `num_platforms` | Yes | Measures distribution reach |
| Metadata richness relates to visibility | `relationship_count` | Yes | Captures documentation/completeness |
| Storyline availability differs by rating | `has_storyline` | Maybe | Could be useful but may reflect documentation bias |
| Developer effects exist but sparse | Developer features | Maybe | Risk of high-cardinality overfitting |
| Playtime bands differ by rating | Playtime band features | Maybe | Useful if coverage is strong |
| Multiplayer support differs | Multiplayer flags | Maybe | Useful for user preference matching |

Export:

```text
diagnostic_feature_recommendations.csv
```

This shows that the predictive pillar is informed by diagnostic evidence.

---

# 22. Recommended Dashboard Page: Hidden Gems & Rating Drivers

Recommended Streamlit page name:

```text
Hidden Gems & Rating Drivers
```

## Dashboard Sections

```text
Hidden Gems & Rating Drivers
â”‚
â”œâ”€â”€ KPI Cards
â”œâ”€â”€ Rating vs Visibility
â”œâ”€â”€ Hidden Gem Explorer
â”œâ”€â”€ Genre and Theme Drivers
â”œâ”€â”€ Genre-Theme Heatmap
â”œâ”€â”€ Platform Reach Patterns
â”œâ”€â”€ Metadata Richness and RAG Readiness
â”œâ”€â”€ Gameplay and Playtime Patterns
â””â”€â”€ Diagnostic Takeaways
```

## KPI Cards

| KPI | Meaning |
|---|---|
| Diagnostic Games | Games eligible for rating diagnostics |
| High-Rated Games | Games with `total_rating >= 80` |
| Hidden Gem Candidates | Games meeting hidden-gem rule |
| Median Rating | Middle rating in diagnostic sample |
| Median Rating Count | Middle visibility/confidence value |
| Top Hidden-Gem Genre | Genre with strongest hidden-gem count/share |
| Top Hidden-Gem Theme | Theme with strongest hidden-gem count/share |
| RAG-Ready Games | Games with enough metadata for game profile documents |

## Interactive Filters

```text
platform
platform family
genre
theme
release decade
rating band
game type
metadata richness band
playtime band
minimum rating count
hidden gem threshold
```

## Main Visuals

| Visual | Dashboard Purpose |
|---|---|
| Rating vs rating count scatter | Shows popularity bias and hidden gems |
| Hidden gem table | Actionable discovery output |
| Genre high-rated share bar chart | Rating pattern by genre |
| Theme hidden-gem share bar chart | Vibe discovery pattern |
| Genre-theme heatmap | Strong metadata combinations |
| Platform reach vs visibility chart | Distribution reach insight |
| Metadata richness vs rating count chart | RAG readiness insight |
| Gameplay/playtime summary chart | User-preference insight |

---

# 23. Implementation-Ready Notebook Checklist

Use this as the build checklist in Codex or your notebook.

## Setup

- [ ] Import libraries.
- [ ] Define `DB_PATH`.
- [ ] Define `OUTPUT_DIR`.
- [ ] Create output directory.
- [ ] Connect to SQLite.
- [ ] Define thresholds: rating, rating count, hidden-gem percentile.

## Validation

- [ ] Count total games.
- [ ] Count games with `total_rating`.
- [ ] Count games with `total_rating_count`.
- [ ] Count rating-reliable games.
- [ ] Count high-rated games.
- [ ] Run integrity check or import data quality status.
- [ ] Export `diagnostic_dataset_snapshot.csv`.

## Diagnostic Base

- [ ] Build all-game `diagnostic_game_base`.
- [ ] Add relationship counts.
- [ ] Add rating bands.
- [ ] Add high-rated flag.
- [ ] Add metadata richness band.
- [ ] Add RAG readiness flag.
- [ ] Add `log_total_rating_count` in pandas with `np.log1p`.
- [ ] Create rating-available and rating-reliable subsets.
- [ ] Add visibility percentile within the rating-reliable pool.
- [ ] Create hidden-gem eligible subset.
- [ ] Add visibility percentile within the hidden-gem eligible pool.
- [ ] Export `diagnostic_game_base.csv`.
- [ ] Export `diagnostic_rating_reliable_base.csv`.

## Rating vs Visibility

- [ ] Scatter plot: rating vs log rating count.
- [ ] Pearson correlation.
- [ ] Spearman correlation.
- [ ] Rating band visibility summary.
- [ ] Export correlation and summary CSVs.

## Hidden Gems

- [ ] Create hidden-gem flag.
- [ ] Create hidden-gem score.
- [ ] Create conservative, balanced, and broad sensitivity rules.
- [ ] Export hidden-gem candidate table.
- [ ] Export threshold summary.
- [ ] Export sensitivity analysis.
- [ ] Create hidden-gem scatter plot.
- [ ] Create hidden-gem by genre/theme/platform summaries.

## Genre and Theme Diagnostics

- [ ] Build genre rating summary.
- [ ] Build theme rating summary.
- [ ] Add sample-size filters.
- [ ] Create median rating visuals.
- [ ] Create high-rated share visuals.
- [ ] Create hidden-gem share visuals.

## Genre-Theme Diagnostics

- [ ] Build genre-theme combination table.
- [ ] Filter combinations with at least 10 games.
- [ ] Create heatmap for median rating.
- [ ] Create heatmap or table for high-rated share.
- [ ] Export `genre_theme_rating_summary.csv`.

## Platform Diagnostics

- [ ] Build platform reach bands.
- [ ] Compare platform reach vs rating count.
- [ ] Compare platform reach vs rating.
- [ ] Build platform family summary.
- [ ] Build platform type summary.
- [ ] Export platform CSVs.

## Company Diagnostics

- [ ] Build developer summary with `developer = 1`.
- [ ] Build publisher summary with `publisher = 1`.
- [ ] Apply minimum sample-size thresholds.
- [ ] Export developer and publisher summaries.
- [ ] Document company-level caveats.

## Metadata and RAG Readiness

- [ ] Compare metadata richness vs visibility.
- [ ] Compare metadata richness vs rating.
- [ ] Compare storylines and text length against rating/rating count.
- [ ] Summarize RAG-ready games.
- [ ] Export metadata and RAG readiness summaries.

## Gameplay and Playtime

- [ ] Build game mode rating summary.
- [ ] Build player perspective rating summary.
- [ ] Build multiplayer support rating summary.
- [ ] Build playtime band rating summary.
- [ ] Export gameplay/playtime CSVs.

## Popularity Primitives

- [ ] Summarize popularity signal coverage.
- [ ] Group by source and popularity type.
- [ ] Avoid combining incompatible popularity values.
- [ ] Compare popularity signals with rating count only within comparable groups.

## Final Outputs

- [ ] Export `diagnostic_feature_recommendations.csv`.
- [ ] Export `diagnostic_takeaways.csv`.
- [ ] Close SQLite connection.
- [ ] Write final notebook takeaways.
- [ ] Write final notebook limitations.

---

# 24. Exact CSV Output Checklist

Minimum required outputs:

```text
diagnostic_dataset_snapshot.csv
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
rating_visibility_correlation.csv
rating_band_visibility_summary.csv
hidden_gem_candidates.csv
hidden_gem_threshold_summary.csv
hidden_gem_sensitivity_analysis.csv
genre_rating_summary.csv
theme_rating_summary.csv
genre_theme_rating_summary.csv
platform_reach_summary.csv
metadata_richness_visibility_summary.csv
diagnostic_feature_recommendations.csv
diagnostic_takeaways.csv
```

Strong full diagnostic outputs:

```text
hidden_gem_by_genre.csv
hidden_gem_by_theme.csv
hidden_gem_by_platform_family.csv
platform_family_rating_summary.csv
platform_type_rating_summary.csv
developer_rating_summary.csv
publisher_rating_summary.csv
metadata_richness_rating_summary.csv
rag_readiness_summary.csv
game_mode_rating_summary.csv
player_perspective_rating_summary.csv
multiplayer_support_rating_summary.csv
playtime_rating_summary.csv
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
```

---

# 25. Exact Chart Checklist

Minimum required charts:

| Chart | Required? | Purpose |
|---|---:|---|
| Rating vs log rating count scatter | Yes | Popularity bias / quality vs visibility |
| Rating band visibility bar/table | Yes | Shows rating-count differences by quality band |
| Hidden gems highlighted scatter | Yes | Main diagnostic story |
| Top hidden gems table | Yes | Actionable output |
| Median rating by genre | Yes | Genre performance |
| High-rated share by genre | Yes | Predictive feature support |
| Median rating by theme | Yes | Vibe performance |
| Genre-theme heatmap | Yes | Supports natural-language matching |
| Platform reach vs visibility | Yes | Platform distribution pattern |
| Metadata richness vs rating count | Yes | RAG readiness / documentation bias |

Optional but valuable charts:

| Chart | Purpose |
|---|---|
| Hidden gems by theme | Vibe discovery |
| Hidden gems by platform family | Platform-specific discovery |
| Developer high-rated share | Company pattern |
| Publisher high-rated share | Company pattern |
| Game mode rating summary | Gameplay preference insight |
| Player perspective rating summary | Camera/view preference insight |
| Playtime band rating summary | Session-length preference insight |
| RAG readiness breakdown | Chatbot readiness |

---

# 26. Minimum Viable Diagnostic Pillar

If time becomes limited, focus on the strongest diagnostic story.

## Must-Have Analyses

1. Rating vs visibility
2. Hidden gem identification
3. Genre rating diagnostics
4. Theme rating diagnostics
5. Genre-theme combination diagnostics
6. Platform reach diagnostics
7. Metadata richness / RAG readiness diagnostics
8. Diagnostic-to-predictive feature recommendations

## Can Be Secondary

1. Developer/publisher diagnostics
2. Multiplayer support diagnostics
3. Player perspective diagnostics
4. Playtime diagnostics
5. Popularity primitive diagnostics

## Why These Are Secondary

Developer/publisher results can be noisy because company-level samples may be small. Gameplay and playtime analysis are useful, but they are less central than hidden gems, rating drivers, platform constraints, and metadata richness. Popularity primitives require careful normalization and should not distract from the MVP.

---

# 27. Recommended Final Diagnostic Takeaways Format

At the end of the notebook, write 5â€“8 takeaways using this format:

```markdown
## Diagnostic Takeaways

1. Rating quality and rating activity are related but not identical.
   - Evidence: [correlation result], rating-vs-count scatter.
   - Project implication: Recommendation logic should not rank only by popularity.

2. Hidden-gem candidates exist under the balanced threshold.
   - Evidence: [number] games meet the hidden-gem rule.
   - Project implication: Hidden-gem boost can be added to the prescriptive engine.

3. Certain genres/themes show stronger high-rated shares.
   - Evidence: [top genres/themes].
   - Project implication: Genre/theme metadata should be included in predictive features and recommendation explanations.

4. Platform reach appears associated with visibility.
   - Evidence: [platform reach summary].
   - Project implication: Number of platforms can be used as a visibility/reach feature.

5. Metadata richness appears related to rating activity or RAG readiness.
   - Evidence: [metadata richness summary].
   - Project implication: Relationship-count features can support model quality and RAG filtering.
```

---

# 28. Final Report Wording

Use this paragraph in the final report or dashboard narrative:

```markdown
The diagnostic analytics pillar investigates why certain games in the IGDB project sample appear more highly rated, more visible, or more discoverable than others. The analysis compares rating quality, rating activity, genre/theme structure, platform reach, developer/publisher roles, metadata richness, gameplay format, and playtime patterns. The main outputs are hidden-gem candidates, rating-driver summaries, and diagnostic findings that inform the predictive model and future hybrid recommendation engine.
```

For the dashboard introduction:

```markdown
This page examines rating drivers and hidden-gem opportunities in the current IGDB project sample. It compares rating quality against visibility, highlights games that are highly rated but less visible, and explores how genre, theme, platform reach, metadata richness, gameplay format, and company roles relate to rating outcomes. These findings support the next project layers: predictive modeling and recommendation scoring.
```

---

# 29. Key Limitations to Document

Include these limitations in the notebook and final report:

```text
The analysis is based on a 3,000-game project sample, not the full IGDB catalog.
Ratings are observational and may reflect audience size, historical popularity, genre bias, or platform availability.
total_rating_count is a proxy for visibility, not a perfect popularity measure.
Games can belong to multiple genres, themes, and platforms, so group counts overlap.
Company analysis may be noisy because many developers/publishers have few games in the sample.
Popularity primitive values should not be combined without normalization.
Metadata richness may reflect documentation bias rather than game quality.
Diagnostic findings show association, not causation.
```

---

# 30. Recommended Build Order

Now that the 3,000-game database works, build in this order:

## Step 1 â€” Re-run short descriptive sanity check

Update only the basic KPIs:

```text
total games
rating coverage
summary coverage
genre/theme/platform coverage
storyline coverage
database integrity
foreign key check
```

## Step 2 â€” Build `diagnostic_game_base.csv`

This is the foundation.

## Step 3 â€” Build rating vs visibility analysis

This creates the logic for hidden gems.

## Step 4 â€” Build hidden gem candidates

This is the most important diagnostic artifact.

## Step 5 â€” Build genre/theme/platform diagnostics

These feed predictive and recommendation logic.

## Step 6 â€” Build metadata richness and RAG readiness diagnostics

This connects directly to the chatbot and vector search layer.

## Step 7 â€” Add secondary diagnostics

Add developer/publisher, gameplay, multiplayer, playtime, and popularity primitive analysis if time allows.

## Step 8 â€” Build diagnostic-to-predictive recommendations

This closes the pillar and prepares the predictive pillar.

---

# 31. Final Diagnostic Pillar Definition

The completed diagnostic pillar should be defined as:

```markdown
The diagnostic analytics layer identifies relationships between game ratings, rating activity, genre/theme structure, platform reach, metadata richness, gameplay format, and hidden-gem potential in the current 3,000-game IGDB project sample. The key output is a hidden-gem definition and a set of rating/visibility driver analyses that inform both the predictive model and the future hybrid recommendation engine.
```

The final diagnostic page should answer:

```text
Why do some games appear more highly rated, more visible, or more discoverable than others?
```

The cleanest MVP is a **Hidden Gems & Rating Drivers** dashboard page supported by the diagnostic notebook and exported CSVs.
