# Diagnostic Analytics Pillar Plan
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Pillar:** Diagnostic Analytics  
**Recommended Dashboard Page:** Hidden Gems & Reception Patterns
**Current Dataset:** 15,000-game curated yearly IGDB sample
**Recommended Notebook:** `notebooks/02_diagnostic_analytics_exploration.ipynb`  
**Recommended Output Folder:** `data/analytics/diagnostic/`

---

# 1. Purpose of the Diagnostic Pillar

The diagnostic analytics pillar answers the question:

> **Why do certain games, genres, themes, platforms, or companies appear to perform better or receive more visibility than others?**

In this project, "performance" should not only mean rating score. It should include several related signals:

- Rating quality
- Rating confidence
- Rating activity
- PopScore visibility / popularity
- Hidden-gem potential
- Genre-theme fit
- Platform reach
- Metadata coverage and volume
- RAG readiness
- Developer and publisher patterns
- Gameplay and playstyle patterns

The diagnostic pillar should not claim causality. The goal is to identify
**associations, patterns, and segments** that may inform later pillars.

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
| Shows metadata completeness | Tests whether metadata components relate to reception or visibility |
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

1. Are higher-rated games also more visible according to IGDB PopScore?
2. How does rating activity differ from PopScore visibility?
3. Which games are high-rated but relatively less visible?
4. Which genres have stronger median ratings?
5. Which themes have stronger median ratings?
6. Which genre-theme combinations are associated with stronger rating outcomes?
7. Do games available on more platforms receive more rating activity?
8. Do platform families differ in rating or visibility patterns?
9. Are some developers or publishers overrepresented among high-rated games?
10. Do separate metadata coverage components relate to rating activity or visibility?
11. Do game modes, player perspectives, multiplayer support, or playtime bands relate to rating patterns?
12. Which diagnostic findings should become similarity-scoring or recommendation signals later?

---

# 4. Updated Dataset Caveat for the Curated 15,000-Game Version

The current extraction selects exactly 1,000 released main games from each year
from 2010 through 2024. Every selected game has a name, first release date, at
least one genre, at least one platform, and no version parent.

Selection uses three mutually exclusive cohorts:

```text
Quality cohort:
    total_rating >= 75
    AND total_rating_count >= 25
    ranked by Bayesian-adjusted yearly total rating

Popularity cohort:
    highest project-defined IGDB interest score
    with IGDB Visits used as a fallback

Comparison cohort:
    reproducible random sample from remaining eligible games
```

The quality and popularity cohorts are deliberately oversampled. Consequently,
the full 15,000-game sample must not be used to estimate the market prevalence
of high-rated or popular games. Use `extraction_cohorts` to stratify results.
Use the comparison cohort for population-oriented summaries, or apply a
documented sampling-aware method.

Suggested notebook/report caveat:

```markdown
The diagnostic results represent a curated 15,000-game IGDB project sample,
not the full IGDB catalog or video game market. The sample contains 1,000
released main games per year from 2010 through 2024 and deliberately includes
all games meeting the project reception rule, up to 200 PopScore-visible games
per year, and a random comparison sample from the remaining eligible games.
Because inclusion probabilities differ by cohort and year, unadjusted
high-rated shares from the full sample are not market prevalence estimates.
Analyses must report or control for `extraction_cohorts.cohort` and release
year.
```

Recommended extraction snapshot table:

| Item | Value |
|---|---:|
| Games | 15,000 |
| Database | `data/database/igdb_games.db` |
| Diagnostic output folder | `data/analytics/diagnostic/` |
| Extraction method | Curated yearly cohort sample |
| Release years | 2010–2024 |
| Games per year | 1,000 |
| Game type | Main Game |
| Games with `total_rating` | 6,278 |
| Games with `total_rating_count >= 10` | 3,828 |
| Games with `total_rating_count >= 25` | 2,498 |
| Games with `total_rating_count >= 50` | 1,525 |
| Quality cohort | 1,418 |
| Popularity cohort | 3,000 |
| Comparison cohort | 10,582 |
| Rating field | `games.total_rating` |
| Rating confidence field | `games.total_rating_count` |
| Main quality threshold | `total_rating >= 80` |
| Main visibility signal | IGDB PopScore primitives |
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
popularity_types
extraction_cohorts
game_time_to_beats
multiplayer_modes
```

Core analytical views include:

```text
vw_game_popscore_latest
vw_game_popscore_igdb_interest
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
total_rating_count >= 25
```

Create separate diagnostic datasets instead of using one filtered table for every analysis:

| Sample | Rule | Use |
|---|---|---|
| All-game base | No rating filter | Metadata coverage, RAG readiness, descriptive carryover, and feature availability |
| Rating-available sample | `total_rating IS NOT NULL` | Broad rating coverage summaries |
| Rating-reliable sample | `total_rating IS NOT NULL AND total_rating_count >= 25` | Main diagnostic analysis |
| Hidden-gem eligible sample | Rating-reliable sample, optionally `game_type_name = 'Main Game'` | Hidden-gem percentile thresholds and candidate selection |

Do not build `diagnostic_game_base` by filtering out unrated games. Build the
base at one row per game first, then create rating-specific subsets. Metadata
coverage and future-readiness summaries must retain unrated games.

## 5.4 Cohort-Aware Analysis Rule

The curated extraction has different inclusion mechanisms:

```text
quality
popularity
comparison
```

Every diagnostic game-level dataset must retain:

```text
extraction_cohort
selection_rank
release_year
```

Rules:

- Do not interpret unadjusted full-sample rating or popularity shares as market prevalence.
- Use the comparison cohort for population-oriented descriptive estimates.
- Use quality-versus-comparison analyses for reception-pattern comparisons.
- Include release year as a stratification or control variable.
- Report cohort-stratified results when using all three cohorts.

## 5.5 High-Rated Rule

Use the project rule:

```text
high_rated = 1 if total_rating >= 80
high_rated = 0 if total_rating < 80
```

Recommended diagnostic filter:

```text
total_rating IS NOT NULL
AND total_rating_count >= 25
```

## 5.6 Visibility Rule

Use the project-defined IGDB interest score as the main visibility signal:

```text
0.60 * Want to Play + 0.40 * Playing
```

Use:

```text
vw_game_popscore_igdb_interest.custom_interest_score
vw_game_popscore_igdb_interest.custom_interest_percentile
```

Interpretation:

```text
total_rating          = quality/reception
total_rating_count    = rating evidence/confidence
custom_interest_score = visibility/interest
```

Missing PopScore means:

```text
visibility unknown
```

It must not be recoded as zero or low visibility.

`total_rating_count` may still be analyzed as rating activity, but it should no
longer be labeled as the primary popularity measure.

## 5.7 Platform Availability Rule

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

## 5.8 Company Role Rule

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

## 5.9 Many-to-Many Counting Rule

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
optional Streamlit page: Hidden Gems & Reception Patterns
```

Recommended exported CSVs:

```text
diagnostic_dataset_snapshot.csv
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
quality_popscore_correlation.csv
rating_band_popscore_summary.csv
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
metadata_volume_rating_summary.csv
metadata_volume_visibility_summary.csv
rag_readiness_summary.csv
metadata_component_summary.csv
user_critic_agreement_summary.csv
user_critic_gap_games.csv
cohort_adjusted_association_summary.csv
game_mode_rating_summary.csv
player_perspective_rating_summary.csv
multiplayer_support_rating_summary.csv
playtime_rating_summary.csv
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
future_pillar_implications.csv
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
6. Quality vs PopScore visibility analysis
7. Hidden gem logic
8. User-versus-critic reception diagnostics
9. Genre rating diagnostics
10. Theme rating diagnostics
11. Genre-theme interaction diagnostics
12. Platform and reach diagnostics
13. Developer and publisher diagnostics
14. Metadata component diagnostics
15. Gameplay, player perspective, multiplayer, and playtime diagnostics
16. PopScore coverage and primitive diagnostics
17. Future-pillar implications
18. Export CSV outputs
19. Final diagnostic takeaways and limitations
```

---

# 8. Section 1 - Imports, Configuration, and Database Connection

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
MIN_RATING_COUNT = 25
HIDDEN_GEM_VISIBILITY_PERCENTILE = 0.40
MAIN_GAME_ONLY = True
MIN_CRITIC_COUNT = 5
MIN_GROUP_SIZE = 25
MIN_INTERACTION_GROUP_SIZE = 20
MIN_COMPANY_GROUP_SIZE = 10
MULTIPLE_TEST_ALPHA = 0.05
```

These constants make the notebook easier to adjust later.

---

# 9. Section 2 - Diagnostic Dataset Validation

## Purpose

Before doing diagnostic analysis, confirm that the database is healthy, that
each release year contains 1,000 games, and that every game has exactly one
`extraction_cohorts` record. Report cohort counts and rating/PopScore coverage.

Run a short validation block:

```sql
SELECT
    COUNT(*) AS total_games,
    SUM(CASE WHEN total_rating IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating,
    SUM(CASE WHEN total_rating_count IS NOT NULL THEN 1 ELSE 0 END) AS games_with_total_rating_count,
    SUM(CASE WHEN total_rating IS NOT NULL AND total_rating_count >= 25 THEN 1 ELSE 0 END) AS rating_reliable_games,
    SUM(CASE WHEN total_rating >= 80 AND total_rating_count >= 25 THEN 1 ELSE 0 END) AS high_rated_games
FROM games;
```

Add release-year and extraction-cohort checks:

```sql
SELECT
    release_year,
    COUNT(*) AS game_count
FROM games
GROUP BY release_year
ORDER BY release_year;

SELECT
    release_year,
    cohort,
    COUNT(*) AS game_count
FROM extraction_cohorts
GROUP BY release_year, cohort
ORDER BY release_year, cohort;
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

# 10. Section 3 - Build Diagnostic Game Base

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
extraction_cohort
selection_rank
adjusted_quality_score
selection_popularity_basis
selection_popularity_score
custom_interest_score
custom_interest_percentile
popscore_available_flag
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
classification_count
distribution_count
company_coverage_count
external_link_count
media_count
text_completeness_score
metadata_volume_total
metadata_volume_percentile
metadata_volume_band
rating_band
rating_available_flag
rating_reliable_flag
high_rated_flag
main_game_flag
rag_ready_flag
user_critic_gap
```

`diagnostic_game_base.csv` should keep all extracted games. Add
`log_total_rating_count`, metadata-volume percentile bands, and within-year
PopScore percentiles after loading this SQL result into pandas.

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
        xc.cohort AS extraction_cohort,
        xc.selection_rank,
        xc.adjusted_quality_score,
        xc.popularity_basis AS selection_popularity_basis,
        xc.popularity_score AS selection_popularity_score,
        psi.custom_interest_score,
        psi.custom_interest_percentile,

        CASE
            WHEN psi.game_id IS NOT NULL THEN 1
            ELSE 0
        END AS popscore_available_flag,

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
        ) AS classification_count,

        (
            COALESCE(pc.num_platforms, 0)
          + COALESCE(rc.num_release_dates, 0)
        ) AS distribution_count,

        COALESCE(cc.num_companies, 0) AS company_coverage_count,

        (
            COALESCE(wc.num_websites, 0)
          + COALESCE(ec.num_external_sources, 0)
        ) AS external_link_count,

        COALESCE(sc.num_screenshots, 0) AS media_count,

        (
            CASE WHEN g.summary IS NOT NULL AND TRIM(g.summary) <> '' THEN 1 ELSE 0 END
          + CASE WHEN g.storyline IS NOT NULL AND TRIM(g.storyline) <> '' THEN 1 ELSE 0 END
        ) AS text_completeness_score,

        (
            COALESCE(gc.num_genres, 0)
          + COALESCE(tc.num_themes, 0)
          + COALESCE(kc.num_keywords, 0)
          + COALESCE(pc.num_platforms, 0)
          + COALESCE(rc.num_release_dates, 0)
          + COALESCE(cc.num_companies, 0)
          + COALESCE(wc.num_websites, 0)
          + COALESCE(ec.num_external_sources, 0)
          + COALESCE(sc.num_screenshots, 0)
        ) AS metadata_volume_total,

        CASE
            WHEN g.rating IS NOT NULL
             AND g.aggregated_rating IS NOT NULL
            THEN g.rating - g.aggregated_rating
            ELSE NULL
        END AS user_critic_gap,

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
             AND g.total_rating_count >= 25 THEN 1
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
    JOIN extraction_cohorts xc
        ON g.game_id = xc.game_id
    LEFT JOIN vw_game_popscore_igdb_interest psi
        ON g.game_id = psi.game_id
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
SELECT *
FROM base;
```

Do not define fixed metadata-quality thresholds in SQL. `metadata_volume_total`
combines counts with different meanings and is only a volume summary. Analyze
the separate components first.

## Python-Derived Fields and Rating Subsets

After loading the SQL result into pandas, derive the log rating count and rating-specific subsets in Python:

```python
diagnostic_game_base["log_total_rating_count"] = np.log1p(
    diagnostic_game_base["total_rating_count"]
)

diagnostic_game_base["metadata_volume_percentile"] = (
    diagnostic_game_base.groupby("release_year")["metadata_volume_total"]
    .rank(pct=True, method="average")
)

diagnostic_game_base["metadata_volume_band"] = pd.cut(
    diagnostic_game_base["metadata_volume_percentile"],
    bins=[0.0, 0.25, 0.50, 0.75, 1.0],
    labels=["Low", "Moderate", "High", "Very high"],
    include_lowest=True,
)

rating_available = diagnostic_game_base[
    diagnostic_game_base["rating_available_flag"] == 1
].copy()

rating_reliable = diagnostic_game_base[
    diagnostic_game_base["rating_reliable_flag"] == 1
].copy()

hidden_gem_eligible = rating_reliable.copy()
if MAIN_GAME_ONLY:
    hidden_gem_eligible = hidden_gem_eligible[
        hidden_gem_eligible["main_game_flag"] == 1
    ].copy()

hidden_gem_eligible = hidden_gem_eligible[
    hidden_gem_eligible["popscore_available_flag"] == 1
].copy()

hidden_gem_eligible["visibility_percentile_eligible_pool"] = (
    hidden_gem_eligible.groupby("release_year")["custom_interest_score"]
    .rank(pct=True, method="average")
)
```

This prevents two common mistakes:

- Metadata coverage and future-readiness analysis should not exclude unrated games.
- Missing PopScore should remain visibility unknown.
- Hidden-gem visibility percentiles should be calculated within release year
  among reliable games with PopScore coverage.
- `extraction_cohort` must remain available for stratification and sensitivity
  analysis.

Export:

```text
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
```

---

# 11. Section 4 - Quality, Rating Activity, and PopScore Visibility

## Main Question

> Are highly rated games also the most visible according to IGDB PopScore?

## Why It Matters

Rating activity and visibility are related but distinct. `total_rating_count`
measures rating evidence, while PopScore measures current interest/activity.

## Metrics

```text
total_rating
total_rating_count
log_total_rating_count
custom_interest_score
custom_interest_percentile
popscore_available_flag
extraction_cohort
release_year
rating_band
```

## Analysis 4.1 - Quality vs PopScore

Chart:

```text
x-axis: custom_interest_percentile
y-axis: total_rating
color: extraction_cohort
facet or control: release_year
tooltip: game name, total_rating_count
```

Interpretation:

```markdown
This chart compares reception quality against IGDB interest among games with
PopScore coverage. Missing PopScore games are excluded from this chart and
reported separately as visibility unknown.
```

## Analysis 4.2 - Quality/Visibility and Quality/Activity Correlations

Calculate:

```python
popscore_df = rating_reliable[
    rating_reliable["popscore_available_flag"] == 1
].copy()

quality_popscore_spearman = popscore_df["total_rating"].corr(
    popscore_df["custom_interest_score"],
    method="spearman",
)

quality_activity_spearman = rating_reliable["total_rating"].corr(
    rating_reliable["total_rating_count"],
    method="spearman",
)
```

Export:

```text
quality_popscore_correlation.csv
quality_rating_activity_correlation.csv
```

Interpretation guide:

| Correlation | Interpretation |
|---:|---|
| Near 0 | Rating and visibility are weakly related |
| 0.20-0.40 | Mild/moderate relationship |
| 0.40-0.60 | Meaningful relationship |
| 0.60+ | Strong relationship |

Calculate correlations by cohort and release-year band as sensitivity checks.
Use Spearman as the main metric because both PopScore and rating counts are
usually skewed.

## Analysis 4.3 - Rating Band PopScore Summary

Group by:

```text
rating_band
extraction_cohort
```

Metrics:

```text
game_count
popscore_covered_games
median_custom_interest_score
median_custom_interest_percentile
median_total_rating_count
```

This answers:

```text
Do excellent games tend to have more PopScore visibility or rating activity
than merely good games, after accounting for cohort and release year?
```

Export:

```text
rating_band_popscore_summary.csv
```

## Analysis 4.4 - PopScore Coverage

Report PopScore availability by:

```text
release_year
extraction_cohort
rating_band
```

This is necessary because visibility conclusions apply only to games with
available PopScore signals.

---

# 12. Section 5 - Hidden Gem Identification

## Main Question

> Which games are high-rated but relatively less visible?

This is one of the most important diagnostic outputs because it directly supports the future recommendation engine.

## Hidden Gem Definition

Use a percentile-based definition:

```text
hidden_gem = total_rating >= 80
             AND total_rating_count >= minimum_confidence_count
             AND popscore_available_flag = 1
             AND visibility_percentile_eligible_pool <= 0.40
             AND main_game_flag = 1
```

Recommended current setting:

```text
quality_threshold = 80
minimum_confidence_count = 25
low_visibility_threshold = 40th percentile
main game only = yes
```

Calculate the 40th percentile within release year among reliable games with
PopScore coverage. Use extraction cohort as a sensitivity check. A missing
PopScore value means visibility unknown and cannot produce a hidden-gem label.

Important implementation rule:

```text
Calculate the visibility percentile after filtering to the hidden-gem eligible pool.
```

For the MVP, that pool should be:

```text
total_rating IS NOT NULL
AND total_rating_count >= 25
AND game_type_name = 'Main Game'
AND popscore_available_flag = 1
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

## Diagnostic Hidden-Gem Strength

The diagnostic pillar may export a two-dimensional strength summary:

```text
quality_percentile
inverse_visibility_percentile
```

Do not combine metadata coverage into the hidden-gem definition. A weighted
ranking score is future prescriptive work and should be clearly labeled as
such if retained in an appendix.

## Recommended Hidden Gem Table Columns

```text
game_id
name
total_rating
total_rating_count
visibility_percentile_eligible_pool
custom_interest_score
custom_interest_percentile
extraction_cohort
release_year
game_type_name
num_genres
num_themes
num_keywords
num_platforms
metadata_volume_band
genres
themes
platforms
```

## Python Skeleton

```python
hidden_gems = hidden_gem_eligible.copy()

hidden_gems["hidden_gem_flag"] = (
    (hidden_gems["total_rating"] >= QUALITY_THRESHOLD)
    & (hidden_gems["popscore_available_flag"] == 1)
    & (
        hidden_gems["visibility_percentile_eligible_pool"]
        <= HIDDEN_GEM_VISIBILITY_PERCENTILE
    )
).astype(int)
```

Use `hidden_gem_eligible` rather than the full `diagnostic_game_base`. Export
year-specific PopScore cutoffs so the label is auditable.

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

# 13. Section 6 - User-versus-Critic Reception Diagnostics

## Main Question

> Where do IGDB users and external critics agree or disagree?

Create an analysis subset:

```text
rating IS NOT NULL
aggregated_rating IS NOT NULL
rating_count >= 25
aggregated_rating_count >= 5
```

Current database coverage:

```text
Games with both user and critic ratings: 3,554
Games meeting both count thresholds: 1,300
```

Derived field:

```text
user_critic_gap = rating - aggregated_rating
```

Interpretation:

```text
positive gap = users rate the game higher
negative gap = critics rate the game higher
near zero    = broad agreement
```

Required outputs:

- Pearson and Spearman agreement between user and critic ratings.
- Median and IQR of `user_critic_gap`.
- Largest positive and negative disagreement tables.
- Gap summaries by release year, genre, theme, and extraction cohort.
- Sensitivity comparison of conclusions using `total_rating` versus
  user-only `rating`.

Exports:

```text
user_critic_agreement_summary.csv
user_critic_gap_games.csv
user_critic_gap_by_genre.csv
```

---

# 14. Section 7 - Genre Rating Diagnostics

## Main Question

> Which genres are associated with stronger rating outcomes?

Genres are broad gameplay categories and are important for both analytics and recommendation matching.

## Important Grain Rule

A game can have multiple genres. Always use:

```sql
COUNT(DISTINCT game_id)
```

## Statistical Comparison Rule

Because quality games were deliberately oversampled, genre analysis must not
rely only on full-sample high-rated shares.

Required primary comparison:

```text
outcome: quality cohort versus comparison cohort
predictors: genre indicators
controls: release year
reported effect: odds ratio with 95% confidence interval
```

Use cluster-robust or bootstrap confidence intervals where practical because
games can belong to multiple genres.

For multiple genre tests, control the false discovery rate using
Benjamini-Hochberg correction at:

```text
alpha = 0.05
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
quality_vs_comparison_odds_ratio
odds_ratio_ci_low
odds_ratio_ci_high
adjusted_p_value
```

## Recommended Minimum Group Size

Since the curated dataset has 15,000 games:

```text
genre game_count >= 25
```

For smaller genres, still export them but mark them as low-sample.

## SQL Skeleton

```sql
SELECT
    ge.name AS genre_name,
    xc.cohort AS extraction_cohort,
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
JOIN extraction_cohorts xc
    ON g.game_id = xc.game_id
WHERE g.total_rating IS NOT NULL
  AND g.total_rating_count >= 25
GROUP BY ge.name, xc.cohort
HAVING COUNT(DISTINCT g.game_id) >= 25
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

Use Python/Pandas for median and IQR if SQLite percentile functions are unavailable.
Use Python/statsmodels or equivalent for cohort-aware odds ratios, confidence
intervals, and multiple-comparison correction.

## Visuals

| Visual | Purpose |
|---|---|
| Boxplot: rating by genre | Shows distribution, not just average |
| Bar chart: median rating by genre | Easy dashboard view |
| Bar chart: cohort-stratified high-rated share by genre | Descriptive support for adjusted effects |
| Bar chart: hidden-gem share by genre | Identifies discovery-rich genres |

## Interpretation Style

```markdown
In the current curated IGDB sample, [genre] has a higher median total rating
than [genre] within [cohort or sampling-adjusted subset]. This suggests an
association in the project dataset, but it does not prove the genre causes
higher ratings.
```

Export:

```text
genre_rating_summary.csv
```

---

# 15. Section 8 - Theme Rating Diagnostics

## Main Question

> Which themes are associated with stronger rating outcomes or hidden-gem potential?

Themes are especially important because this project is about vibe-based discovery. Themes capture high-level mood, setting, or subject, such as fantasy, sci-fi, horror, survival, mystery, and comedy.

Apply the same cohort-aware odds-ratio, release-year control, confidence
interval, and false-discovery-rate rules used for genres.

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

# 16. Section 9 - Genre-Theme Combination Diagnostics

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

Since the curated dataset has 15,000 games:

```text
genre-theme game_count >= 20
```

If too many combinations disappear, lower the threshold to 5 and clearly label those outputs as exploratory.

## SQL Skeleton

```sql
SELECT
    ge.name AS genre_name,
    th.name AS theme_name,
    xc.cohort AS extraction_cohort,
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
JOIN extraction_cohorts xc
    ON g.game_id = xc.game_id
WHERE g.total_rating IS NOT NULL
  AND g.total_rating_count >= 25
GROUP BY ge.name, th.name, xc.cohort
HAVING COUNT(DISTINCT g.game_id) >= 20
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

Genre-theme combinations are exploratory high-dimensional tests. Apply
Benjamini-Hochberg correction and report effect sizes with 95% confidence
intervals. Do not rank combinations solely by raw high-rated share.

## Visuals

| Visual | Purpose |
|---|---|
| Heatmap: median rating by genre-theme | Shows strong combinations |
| Heatmap: cohort-stratified high-rated share by genre-theme | Descriptive support for adjusted effects |
| Table: top genre-theme combinations | Useful for final report |
| Table: hidden-gem rich combinations | Useful for recommender logic |

Export:

```text
genre_theme_rating_summary.csv
```

---

# 17. Section 10 - Platform and Reach Diagnostics

## Main Question

> Does platform availability relate to visibility or rating quality?

Platform is important because the final recommendation engine must respect platform constraints.

## Analysis 9.1 - Number of Platforms vs Visibility

Question:

```text
Are games available on more platforms more visible?
```

Metrics:

```text
num_platforms
custom_interest_score
custom_interest_percentile
popscore_available_flag
```

Visuals:

```text
Scatter plot: num_platforms vs custom_interest_percentile
Boxplot: custom_interest_percentile by platform reach band
```

Suggested platform reach bands:

```text
1 platform
2-3 platforms
4-6 platforms
7+ platforms
```

## Analysis 9.2 - Number of Platforms vs Rating

Question:

```text
Are multi-platform games rated differently from single-platform games?
```

Visual:

```text
Boxplot: total_rating by platform reach band
```

## Analysis 9.3 - Platform Family Patterns

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
median_custom_interest_percentile
high_rated_share
hidden_gem_share
```

## Analysis 9.4 - Platform Type Patterns

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

# 18. Section 11 - Developer and Publisher Diagnostics

## Main Question

> Which developers and publishers are associated with stronger rating outcomes or hidden-gem candidates?

## Challenge

Even with 15,000 games, company analysis can be noisy. Some developers may only appear once or twice.

## Minimum Group Size

Recommended:

```text
developer_game_count >= 10
publisher_game_count >= 10
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
    xc.cohort AS extraction_cohort,
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
JOIN extraction_cohorts xc
    ON g.game_id = xc.game_id
WHERE ic.developer = 1
  AND g.total_rating IS NOT NULL
  AND g.total_rating_count >= 25
GROUP BY c.name, xc.cohort
HAVING COUNT(DISTINCT g.game_id) >= 10
ORDER BY high_rated_share DESC, mean_total_rating DESC;
```

Company comparisons must be treated as exploratory. Report confidence
intervals and use false-discovery-rate correction when testing many companies.
Prefer quality-versus-comparison odds ratios with release-year controls over
raw full-sample high-rated shares.

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

# 19. Section 12 - Metadata Component Diagnostics

## Main Question

> How do separate metadata coverage components relate to reception and PopScore visibility?

Metadata volume can reflect documentation practices, age, platform reach, and
commercial visibility. It should not be interpreted as game quality.

## Metadata Component Fields

Use:

```text
classification_count
distribution_count
company_coverage_count
external_link_count
media_count
text_completeness_score
metadata_volume_total
metadata_volume_percentile
metadata_volume_band
summary_length
storyline_length
has_storyline
rag_ready_flag
```

Analyze components separately first. `metadata_volume_total` is a secondary
volume summary, not an objective metadata-quality score.

## Analysis 11.1 - Metadata Components vs Visibility

Question:

```text
Do games with broader metadata coverage have higher PopScore visibility?
```

Visual:

```text
Component scatter/boxplots against custom_interest_percentile
Boxplot: custom_interest_percentile by metadata_volume_band
```

Metrics:

```text
metadata_component
extraction_cohort
game_count
popscore_covered_games
median_custom_interest_percentile
```

## Analysis 11.2 - Metadata Components vs Rating

Question:

```text
Do metadata coverage components differ between quality and comparison cohorts?
```

Visual:

```text
Component distributions by extraction cohort
Boxplot: total_rating by metadata_volume_band within reliable games
```

Metrics:

```text
metadata_component
metadata_volume_band
median_total_rating
quality_vs_comparison_effect_size
confidence_interval
```

## Analysis 11.3 - Text Richness

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

## Analysis 11.4 - RAG Readiness

Suggested rule:

```text
rag_ready = summary exists
            AND num_genres >= 1
            AND num_themes >= 1
            AND num_platforms >= 1
```

Keep this as a future-use readiness summary. It is not evidence that a game is
higher quality or more visible.

Exports:

```text
metadata_component_summary.csv
metadata_volume_rating_summary.csv
metadata_volume_visibility_summary.csv
rag_readiness_summary.csv
```

---

# 20. Section 13 - Gameplay, Player Perspective, Multiplayer, and Playtime Diagnostics

## Main Question

> Do gameplay format, perspective, multiplayer support, or playtime relate to rating quality or visibility?

Compare gameplay fields against:

```text
total_rating
total_rating_count
custom_interest_percentile
high_rated_flag
hidden_gem_flag
extraction_cohort
```

## Analysis 12.1 - Game Mode Rating Patterns

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
median_custom_interest_percentile
high_rated_share
hidden_gem_share
```

## Analysis 12.2 - Player Perspective Rating Patterns

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

## Analysis 12.3 - Multiplayer Support

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
median_custom_interest_percentile
high_rated_share
hidden_gem_share
```

Important rule:

```markdown
Missing multiplayer records should mean unknown, not "no multiplayer."
```

## Analysis 12.4 - Playtime Bands

Use `game_time_to_beats.normally` as the default playtime measure and convert seconds to hours.

Suggested playtime bands:

```text
Very short: 0-5 hours
Short: 5-15 hours
Medium: 15-30 hours
Long: 30-60 hours
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

# 21. Section 14 - PopScore Coverage and Primitive Diagnostics

## Main Question

> Are IGDB popularity signals available and useful beyond rating count?

Use `vw_game_popscore_igdb_interest` as the main visibility source.

Use raw `popularity_primitives` for coverage and source/type diagnostics:

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

Required reporting:

```text
PopScore coverage by release year and extraction cohort
IGDB interest score distribution
IGDB Visits fallback coverage
correlation between PopScore, rating activity, and total rating
missing-PopScore profile
```

Useful exports:

```text
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
```

---

# 22. Section 15 - Future-Pillar Implications

This section records possible future uses. It is not a required diagnostic
modeling deliverable.

Create a table like this:

| Diagnostic Finding | Candidate Similarity/Recommendation Signal | Use? | Reason |
|---|---|---:|---|
| Rating count is skewed | `log_total_rating_count` | Conditional | Measures rating activity/confidence; avoid overpowering relevance |
| Cohort-adjusted genre association exists | Genre profile weights | Maybe | Requires later validation outside the curated sample |
| Cohort-adjusted theme association exists | Theme profile weights | Maybe | Requires later validation outside the curated sample |
| Platform reach relates to visibility | `num_platforms` | Yes | Measures distribution reach |
| Metadata components relate to visibility | Separate component variables | Maybe | Avoids conflating different relationship types |
| Storyline availability differs by rating | `has_storyline` | Maybe | Could be useful but may reflect documentation bias |
| Developer effects exist but sparse | Developer signal | Maybe | Risk of over-personalizing or over-weighting sparse data |
| Playtime bands differ by rating | Playtime band features | Maybe | Useful if coverage is strong |
| Multiplayer support differs | Multiplayer flags | Maybe | Useful for user preference matching |

Export:

```text
future_pillar_implications.csv
```

Any use in predictive/similarity or prescriptive work must be evaluated later for proxy bias,
availability at recommendation time, and sampling bias.

---

# 23. Recommended Dashboard Page: Hidden Gems & Reception Patterns

Recommended Streamlit page name:

```text
Hidden Gems & Reception Patterns
```

## Dashboard Sections

```text
Hidden Gems & Reception Patterns
|
|-- KPI Cards
|-- Rating vs Visibility
|-- Hidden Gem Explorer
|-- Genre and Theme Drivers
|-- Genre-Theme Heatmap
|-- Platform Reach Patterns
|-- User vs Critic Reception
|-- Metadata Coverage Patterns
|-- Gameplay and Playtime Patterns
\-- Diagnostic Takeaways
```

## KPI Cards

| KPI | Meaning |
|---|---|
| Diagnostic Games | Games eligible for rating diagnostics |
| High-Rated Games | Games with `total_rating >= 80` |
| Hidden Gem Candidates | Games meeting hidden-gem rule |
| Median Rating | Middle rating in diagnostic sample |
| Median Rating Count | Middle rating-evidence value |
| PopScore Coverage | Games with IGDB interest visibility |
| Median PopScore Percentile | Middle visibility among covered games |
| Top Hidden-Gem Genre | Genre with strongest hidden-gem count/share |
| Top Hidden-Gem Theme | Theme with strongest hidden-gem count/share |
| RAG-Ready Games | Games with enough metadata for game profile documents |

## Interactive Filters

```text
platform
platform family
genre
theme
release year
extraction cohort
rating band
game type
metadata volume band
playtime band
minimum rating count
hidden gem threshold
```

## Main Visuals

| Visual | Dashboard Purpose |
|---|---|
| Rating vs PopScore scatter | Shows quality versus visibility |
| Hidden gem table | Actionable discovery output |
| Genre cohort-adjusted effect chart | Reception association by genre |
| Theme hidden-gem share bar chart | Vibe discovery pattern |
| Genre-theme heatmap | Strong metadata combinations |
| Platform reach vs visibility chart | Distribution reach insight |
| User vs critic agreement chart | Reception agreement and disagreement |
| Metadata component chart | Documentation/coverage pattern |
| Gameplay/playtime summary chart | User-preference insight |

---

# 24. Implementation-Ready Notebook Checklist

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
- [ ] Validate 1,000 games per release year.
- [ ] Validate one extraction cohort per game.
- [ ] Count quality, popularity, and comparison cohorts.
- [ ] Count PopScore-covered games.
- [ ] Run integrity check or import data quality status.
- [ ] Export `diagnostic_dataset_snapshot.csv`.

## Diagnostic Base

- [ ] Build all-game `diagnostic_game_base`.
- [ ] Join extraction cohort and PopScore fields.
- [ ] Add separate metadata component counts.
- [ ] Add rating bands.
- [ ] Add high-rated flag.
- [ ] Add within-year metadata volume percentile/band.
- [ ] Add RAG readiness flag.
- [ ] Add user-critic gap.
- [ ] Add `log_total_rating_count` in pandas with `np.log1p`.
- [ ] Create rating-available and rating-reliable subsets.
- [ ] Preserve missing PopScore as visibility unknown.
- [ ] Create hidden-gem eligible subset.
- [ ] Add within-release-year PopScore percentile.
- [ ] Export `diagnostic_game_base.csv`.
- [ ] Export `diagnostic_rating_reliable_base.csv`.

## Quality vs Visibility

- [ ] Scatter plot: rating vs PopScore percentile.
- [ ] Calculate quality-PopScore Spearman correlation.
- [ ] Calculate quality-rating-activity Spearman correlation separately.
- [ ] Repeat by cohort/release-year band as sensitivity checks.
- [ ] Summarize PopScore coverage.
- [ ] Rating band visibility summary.
- [ ] Export correlation and summary CSVs.

## Hidden Gems

- [ ] Create hidden-gem flag.
- [ ] Create conservative, balanced, and broad sensitivity rules.
- [ ] Export year-specific PopScore cutoffs.
- [ ] Export hidden-gem candidate table.
- [ ] Export threshold summary.
- [ ] Export sensitivity analysis.
- [ ] Create hidden-gem scatter plot.
- [ ] Create hidden-gem by genre/theme/platform summaries.

## Genre and Theme Diagnostics

- [ ] Build genre rating summary.
- [ ] Build theme rating summary.
- [ ] Add sample-size filters.
- [ ] Estimate quality-vs-comparison odds ratios with release-year controls.
- [ ] Add 95% confidence intervals.
- [ ] Apply Benjamini-Hochberg correction.
- [ ] Create median rating visuals.
- [ ] Create high-rated share visuals.
- [ ] Create hidden-gem share visuals.

## Genre-Theme Diagnostics

- [ ] Build genre-theme combination table.
- [ ] Filter combinations with at least 20 reliable games.
- [ ] Create heatmap for median rating.
- [ ] Create heatmap or table for high-rated share.
- [ ] Export `genre_theme_rating_summary.csv`.

## Platform Diagnostics

- [ ] Build platform reach bands.
- [ ] Compare platform reach vs PopScore visibility.
- [ ] Compare platform reach vs rating.
- [ ] Build platform family summary.
- [ ] Build platform type summary.
- [ ] Export platform CSVs.

## Company Diagnostics

- [ ] Build developer summary with `developer = 1`.
- [ ] Build publisher summary with `publisher = 1`.
- [ ] Apply minimum sample-size thresholds.
- [ ] Add confidence intervals and multiple-test correction.
- [ ] Export developer and publisher summaries.
- [ ] Document company-level caveats.

## Metadata Components and Future Readiness

- [ ] Compare separate metadata components vs visibility.
- [ ] Compare separate metadata components vs rating/cohort.
- [ ] Treat total metadata volume as a secondary percentile summary.
- [ ] Compare storylines and text length against rating/rating count.
- [ ] Summarize RAG-ready games.
- [ ] Export metadata and RAG readiness summaries.

## Gameplay and Playtime

- [ ] Build game mode rating summary.
- [ ] Build player perspective rating summary.
- [ ] Build multiplayer support rating summary.
- [ ] Build playtime band rating summary.
- [ ] Export gameplay/playtime CSVs.

## PopScore and Popularity Primitives

- [ ] Summarize PopScore coverage by year and cohort.
- [ ] Use IGDB interest as the main visibility signal.
- [ ] Group by source and popularity type.
- [ ] Avoid combining incompatible popularity values.
- [ ] Compare popularity signals with rating count only within comparable groups.

## User-versus-Critic Diagnostics

- [ ] Build user/critic agreement summary.
- [ ] Calculate user-critic gap.
- [ ] Export largest disagreement cases.
- [ ] Compare total-rating findings against user-only ratings.

## Final Outputs

- [ ] Export optional `future_pillar_implications.csv`.
- [ ] Export `diagnostic_takeaways.csv`.
- [ ] Close SQLite connection.
- [ ] Write final notebook takeaways.
- [ ] Write final notebook limitations.

---

# 25. Exact CSV Output Checklist

Minimum required outputs:

```text
diagnostic_dataset_snapshot.csv
diagnostic_game_base.csv
diagnostic_rating_reliable_base.csv
quality_popscore_correlation.csv
quality_rating_activity_correlation.csv
rating_band_popscore_summary.csv
hidden_gem_candidates.csv
hidden_gem_threshold_summary.csv
hidden_gem_sensitivity_analysis.csv
user_critic_agreement_summary.csv
user_critic_gap_games.csv
genre_rating_summary.csv
theme_rating_summary.csv
genre_theme_rating_summary.csv
platform_reach_summary.csv
metadata_component_summary.csv
cohort_adjusted_association_summary.csv
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
metadata_volume_rating_summary.csv
metadata_volume_visibility_summary.csv
rag_readiness_summary.csv
game_mode_rating_summary.csv
player_perspective_rating_summary.csv
multiplayer_support_rating_summary.csv
playtime_rating_summary.csv
popularity_signal_coverage.csv
popularity_type_rating_count_correlation.csv
```

---

# 26. Exact Chart Checklist

Minimum required charts:

| Chart | Required? | Purpose |
|---|---:|---|
| Rating vs PopScore scatter | Yes | Quality versus visibility |
| Rating activity vs PopScore comparison | Yes | Separates confidence from visibility |
| Hidden gems highlighted scatter | Yes | Main diagnostic story |
| Top hidden gems table | Yes | Actionable output |
| Genre odds-ratio chart | Yes | Cohort-adjusted genre association |
| User vs critic agreement scatter | Yes | Reception agreement |
| Median rating by theme | Yes | Vibe performance |
| Genre-theme heatmap | Yes | Supports natural-language matching |
| Platform reach vs visibility | Yes | Platform distribution pattern |
| Metadata components vs PopScore | Yes | Documentation/visibility association |

Optional but valuable charts:

| Chart | Purpose |
|---|---|
| Hidden gems by theme | Vibe discovery |
| Hidden gems by platform family | Platform-specific discovery |
| Developer effect-size chart | Company pattern |
| Publisher effect-size chart | Company pattern |
| Game mode rating summary | Gameplay preference insight |
| Player perspective rating summary | Camera/view preference insight |
| Playtime band rating summary | Session-length preference insight |
| RAG readiness breakdown | Chatbot readiness |

---

# 27. Minimum Viable Diagnostic Pillar

If time becomes limited, focus on the strongest diagnostic story.

## Must-Have Analyses

1. Quality vs PopScore visibility
2. Hidden gem identification
3. User-versus-critic reception
4. Cohort-adjusted genre/theme diagnostics
5. Genre-theme combination diagnostics
6. Platform reach diagnostics
7. Metadata component diagnostics
8. Statistical effect-size and confidence-interval reporting

## Can Be Secondary

1. Developer/publisher diagnostics
2. Multiplayer support diagnostics
3. Player perspective diagnostics
4. Playtime diagnostics
5. Raw popularity primitive diagnostics beyond the main IGDB interest view

## Why These Are Secondary

Developer/publisher results can be noisy because company-level samples may be
small. Gameplay and playtime analysis are useful, but they are less central
than hidden gems, cohort-adjusted reception associations, platform constraints,
and PopScore visibility.

---

# 28. Recommended Final Diagnostic Takeaways Format

At the end of the notebook, write 5-8 takeaways using this format:

```markdown
## Diagnostic Takeaways

1. Rating quality, rating evidence, and PopScore visibility are distinct.
   - Evidence: [quality-PopScore correlation], [quality-count correlation].
   - Project implication: Keep quality, confidence, and visibility as separate signals.

2. Hidden-gem candidates exist under the balanced threshold.
   - Evidence: [number] games meet the hidden-gem rule.
   - Project implication: Hidden-gem boost can be added to the prescriptive engine.

3. Certain genres/themes have cohort-adjusted reception associations.
   - Evidence: [odds ratios, confidence intervals, adjusted p-values].
   - Project implication: These are associations, not causal quality effects.

4. Platform reach appears associated with visibility.
   - Evidence: [platform reach summary].
   - Project implication: Number of platforms can be used as a visibility/reach feature.

5. Specific metadata components appear related to visibility or cohort.
   - Evidence: [component-level summaries].
   - Project implication: Metadata volume may reflect documentation bias and
     should not be treated as game quality.
```

---

# 29. Final Report Wording

Use this paragraph in the final report or dashboard narrative:

```markdown
The diagnostic analytics pillar investigates associations between game
reception, rating evidence, IGDB PopScore visibility, genre/theme structure,
platform reach, company roles, metadata coverage, gameplay format, and
playtime. Analyses account for release year and extraction cohort. The primary
outputs are auditable hidden-gem candidates, user-versus-critic comparisons,
and cohort-adjusted association summaries.
```

For the dashboard introduction:

```markdown
This page examines reception and hidden-gem patterns in the curated IGDB
sample. It compares reliable ratings with PopScore visibility, highlights
high-rated games with lower within-year interest, examines user-versus-critic
agreement, and reports cohort-adjusted associations for genres, themes,
platform reach, metadata coverage, gameplay format, and company roles.
```

---

# 30. Key Limitations to Document

Include these limitations in the notebook and final report:

```text
The analysis is based on a curated 15,000-game yearly cohort sample, not the
full IGDB catalog. Quality and visibility cases are deliberately oversampled,
so full-sample prevalence estimates require cohort-aware analysis.
Ratings are observational and may reflect audience size, historical popularity, genre bias, or platform availability.
total_rating_count measures rating evidence/activity, not direct visibility.
Missing PopScore means visibility unknown, not low visibility.
Games can belong to multiple genres, themes, and platforms, so group counts overlap.
Company analysis may be noisy because many developers/publishers have few games in the sample.
Popularity primitive values should not be combined without normalization.
Metadata volume may reflect documentation bias rather than game quality.
Multiple category tests require effect sizes, confidence intervals, and false-discovery-rate correction.
Diagnostic findings show association, not causation.
```

---

# 31. Recommended Build Order

Now that the curated 15,000-game database works, build in this order:

## Step 1 - Re-run short descriptive sanity check

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

## Step 2 - Build `diagnostic_game_base.csv`

This is the foundation.

## Step 3 - Build quality, rating-activity, and PopScore analysis

This creates the logic for hidden gems.

## Step 4 - Build hidden gem candidates

This is the most important diagnostic artifact.

## Step 5 - Build user-versus-critic and cohort-adjusted category diagnostics

Report odds ratios, confidence intervals, and adjusted p-values.

## Step 6 - Build platform and metadata component diagnostics

Analyze separate metadata components before any total-volume summary.

## Step 7 - Add secondary diagnostics

Add developer/publisher, gameplay, multiplayer, playtime, and raw popularity
primitive analysis if time allows.

## Step 8 - Document future-pillar implications

Keep these as implications, not diagnostic implementation requirements.

---

# 32. Final Diagnostic Pillar Definition

The completed diagnostic pillar should be defined as:

```markdown
The diagnostic analytics layer identifies relationships between game ratings,
rating activity, PopScore visibility, user-versus-critic agreement,
genre/theme structure, platform reach, metadata coverage, gameplay format, and
hidden-gem potential in the curated
15,000-game IGDB project sample. Analyses must account for release year and
extraction cohort.
```

The final diagnostic page should answer:

```text
Why do some games appear more highly rated, more visible, or more discoverable than others?
```

The cleanest MVP is a **Hidden Gems & Reception Patterns** dashboard page
supported by the diagnostic notebook and exported CSVs.

