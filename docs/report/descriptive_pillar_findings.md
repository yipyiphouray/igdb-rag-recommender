# Descriptive Analytics Pillar Findings

## IGDB Game Discovery Project

**Pillar:** Descriptive Analytics  
**Dataset:** Refreshed curated IGDB analytical sample  
**Current game count:** 47,835 games  
**Release years:** 2010-2024  
**Primary notebook:** [`01_descriptive_analytics_exploration.ipynb`](../../notebooks/01_descriptive_analytics_exploration.ipynb)  
**Analysis plan:** [`descriptive_analytics_pillar_plan.md`](../plan/descriptive_analytics_pillar_plan.md)  
**Descriptive outputs:** [`data/analytics/descriptive/`](../../data/analytics/descriptive/)

---

## 1. Notebook Review Status

The refreshed descriptive notebook completed successfully after the new IGDB extraction and database rebuild.

The descriptive outputs now reflect a broader curated sample of 47,835 released main games from 2010 through 2024. The extraction target was 50,000 games, but the final selected count is lower because the early years did not have enough eligible records to fill the configured yearly target.

The descriptive notebook exports show:

- SQLite integrity check passed.
- Foreign-key check reported no failures.
- The `games` table contains 47,835 records.
- The `extraction_cohorts` table contains 47,835 records.
- Every selected game has a release year, game type, name, genre, platform, and release-date relationship.
- All descriptive CSV outputs were refreshed under `data/analytics/descriptive/`.

---

## 2. Executive Summary

The refreshed descriptive analytics pillar gives a much broader view of the project catalog than the earlier 15,000-game sample. The larger extraction makes the project more useful for storytelling because it now includes stronger-rated games, lower-rated reliable games, high-visibility games, low-known-visibility games, and a large residual comparison cohort.

The main findings are:

1. **The current database is structurally healthy.**
   - SQLite integrity passed.
   - No foreign-key failures were found.
   - Required analytical fields are complete for the selected games.

2. **The sample is broad but still curated.**
   - The extraction targeted 50,000 games but selected 47,835.
   - 2014-2024 reached the configured yearly target.
   - 2010-2013 fell below target because the eligible candidate pool was smaller.

3. **The catalog is heavily PC and indie oriented.**
   - PC appears on 33,101 games, or 69.20% of the catalog.
   - Indie appears on 23,050 games, or 48.19%.
   - Adventure appears on 17,401 games, or 36.38%.

4. **Core profile readiness is strong.**
   - Summary coverage is 96.39%.
   - Cover coverage is 95.65%.
   - Website coverage is 97.05%.
   - Screenshot coverage is 89.82%.

5. **Ratings are available for a minority of the broader catalog.**
   - Total rating coverage is 29.29%.
   - User rating coverage is 26.77%.
   - Critic rating coverage is 13.34%.
   - Reliable rating coverage using `total_rating_count >= 25` is 5.52%.

6. **Long-form narrative and playtime data are sparse.**
   - Storyline coverage is 15.75%.
   - Time-to-beat record coverage is 6.98%.
   - These fields are useful when available but should not be required for core app functionality.

---

## 3. Sample Design and Extraction Caveat

The current dataset should not be interpreted as the full IGDB catalog or as a market-representative sample. It is a curated analytical sample designed for descriptive, diagnostic, recommendation, and RAG work.

The extraction selected games from five mutually exclusive cohorts:

| Cohort | Games | Share | Purpose |
|---|---:|---:|---|
| Quality | 1,425 | 2.98% | Reliable stronger-rated games using the quality rule |
| Lower-rated | 147 | 0.31% | Reliable lower-rated games using the lower-reception rule |
| Popularity | 9,000 | 18.81% | High-known-visibility games using IGDB interest or visits |
| Low visibility | 5,329 | 11.14% | Low-known-visibility games among games with known visibility |
| Comparison | 31,934 | 66.76% | Remaining eligible games used as a residual comparison group |
| **Total** | **47,835** | **100.00%** | **Current analytical sample** |

Important interpretation rules:

- `quality` means stronger reliable reception under the project rule, not objective game quality.
- `lower_rated` means lower reliable reception, not an objective label that a game is bad.
- `popularity` and `low_visibility` are visibility cohorts based on known IGDB PopScore signals.
- Missing PopScore means unknown visibility, not low visibility.
- The comparison cohort is residual, meaning it is built after the other cohort selections are removed.

---

## 4. Release-Year Coverage

The extraction covers all years from 2010 through 2024.

| Release year | Games | Share |
|---:|---:|---:|
| 2010 | 2,744 | 5.74% |
| 2011 | 2,646 | 5.53% |
| 2012 | 2,772 | 5.79% |
| 2013 | 3,009 | 6.29% |
| 2014 | 3,334 | 6.97% |
| 2015 | 3,333 | 6.97% |
| 2016 | 3,333 | 6.97% |
| 2017 | 3,333 | 6.97% |
| 2018 | 3,333 | 6.97% |
| 2019 | 3,333 | 6.97% |
| 2020 | 3,333 | 6.97% |
| 2021 | 3,333 | 6.97% |
| 2022 | 3,333 | 6.97% |
| 2023 | 3,333 | 6.97% |
| 2024 | 3,333 | 6.97% |

This is a useful improvement over the previous raw-pull concern because the sample now provides broad year coverage while still retaining enough contrast across reception and visibility outcomes.

---

## 5. Genre, Theme, and Platform Profile

### Top genres

| Genre | Games | Share |
|---|---:|---:|
| Indie | 23,050 | 48.19% |
| Adventure | 17,401 | 36.38% |
| Simulator | 8,965 | 18.74% |
| Strategy | 8,060 | 16.85% |
| Role-playing (RPG) | 7,622 | 15.93% |
| Puzzle | 7,441 | 15.56% |
| Arcade | 5,088 | 10.64% |
| Platform | 4,250 | 8.88% |
| Shooter | 3,977 | 8.31% |
| Visual Novel | 3,131 | 6.55% |

The sample remains strongly indie/adventure weighted. That is not necessarily a problem for the project because the app is a game discovery system, but the report and UI should avoid implying that these shares represent the full market.

### Top themes

| Theme | Games | Share |
|---|---:|---:|
| Action | 18,422 | 38.51% |
| Fantasy | 5,538 | 11.58% |
| Science fiction | 3,893 | 8.14% |
| Horror | 3,326 | 6.95% |
| Comedy | 2,835 | 5.93% |
| Mystery | 1,762 | 3.68% |
| Erotic | 1,676 | 3.50% |
| Romance | 1,588 | 3.32% |
| Kids | 1,464 | 3.06% |
| Survival | 1,459 | 3.05% |

Action remains the dominant theme. Fantasy, science fiction, and horror give the catalog good coverage for recommendation questions based on mood, setting, and genre preference.

### Top platforms

| Platform | Games | Share |
|---|---:|---:|
| PC (Microsoft Windows) | 33,101 | 69.20% |
| Mac | 8,249 | 17.24% |
| iOS | 7,977 | 16.68% |
| Android | 6,998 | 14.63% |
| Nintendo Switch | 5,460 | 11.41% |
| Linux | 5,346 | 11.18% |
| PlayStation 4 | 4,721 | 9.87% |
| Xbox One | 3,895 | 8.14% |
| Web browser | 3,398 | 7.10% |
| PlayStation 5 | 2,230 | 4.66% |

PC is the clear anchor platform. Mobile and modern console coverage are also meaningful, which supports future filters for platform availability.

---

## 6. Field Completeness

| Field or relationship | Coverage |
|---|---:|
| Name | 100.00% |
| Release year | 100.00% |
| Game type | 100.00% |
| Genre relationship | 100.00% |
| Platform relationship | 100.00% |
| Release-date relationship | 100.00% |
| Website relationship | 97.05% |
| Summary | 96.39% |
| Cover ID | 95.65% |
| Screenshot | 89.82% |
| Theme relationship | 67.40% |
| Company relationship | 66.54% |
| Keyword relationship | 53.35% |
| Storyline | 15.75% |
| Time-to-beat record | 6.98% |

The catalog is strong enough for browsing, filtering, dashboards, and RAG grounding because most games have basic profile text, media, release metadata, platforms, and genres. The weaker fields should be treated as optional enhancements.

---

## 7. Rating Coverage

| Rating measure | Games | Share |
|---|---:|---:|
| Total rating | 14,009 | 29.29% |
| Total rating count | 14,009 | 29.29% |
| User rating | 12,807 | 26.77% |
| Critic rating | 6,383 | 13.34% |
| Reliable rating, `total_rating_count >= 25` | 2,639 | 5.52% |
| High-rated reliable, `total_rating >= 80` and count >= 25 | 775 | 1.62% |

The important conclusion is that ratings are analytically useful but not universally available. Rating-based charts and diagnostic claims should always disclose their denominator. The larger extraction reduced rating coverage compared with the earlier 15,000-game sample because the new dataset intentionally includes more comparison and low-visibility games.

---

## 8. Media and UI Readiness

| Media metric | Games | Share |
|---|---:|---:|
| Games with cover | 45,752 | 95.65% |
| Games with screenshot | 42,964 | 89.82% |
| Games with cover and screenshot | 41,748 | 87.28% |
| Games with no cover or screenshot | 867 | 1.81% |

This is strong enough for the Streamlit MVP and future website. The UI should still handle missing media gracefully, but the majority of records are presentation-ready.

---

## 9. Descriptive Interpretation

The descriptive pillar is complete enough to support the next project phase. The refreshed sample gives the project a stronger foundation because it now contains:

- broad release-year coverage;
- a large comparison cohort;
- explicit lower-rated and low-visibility cohorts;
- strong metadata coverage for browsing and RAG;
- enough reliable-rated games for diagnostic analysis;
- enough PopScore-covered games for visibility analysis.

The main caveat is that the sample is curated. Full-sample percentages describe this project database, not the complete video-game market.

---

## 10. Recommended Report Wording

Use this wording when presenting the descriptive pillar:

> The project uses a refreshed curated IGDB analytical sample of 47,835 released main games from 2010 through 2024. The extraction targeted 50,000 games, but selected 47,835 because the earliest years had fewer eligible records than the configured target. The sample intentionally combines quality, lower-rated, popularity, low-visibility, and comparison cohorts, so descriptive percentages summarize the project catalog rather than the full IGDB catalog or the full game market.
