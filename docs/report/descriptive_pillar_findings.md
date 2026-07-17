# Descriptive Analytics Pillar Findings

## IGDB Game Discovery Project

**Pillar:** Descriptive Analytics  
**Dataset:** Curated 15,000-game IGDB sample  
**Release years:** 2010–2024  
**Games per year:** 1,000  
**Primary notebook:** [`01_descriptive_analytics_exploration.ipynb`](../../notebooks/01_descriptive_analytics_exploration.ipynb)  
**Analysis plan:** [`descriptive_analytics_pillar_plan.md`](../descriptive_analytics_pillar_plan.md)  
**Descriptive outputs:** [`data/analytics/descriptive/`](../../data/analytics/descriptive/)

---

## 1. Notebook Review Status

The descriptive notebook completed successfully:

- All 28 code cells executed.
- No runtime errors occurred.
- No warnings were written to standard error.
- The database connection closed normally.
- All 48 descriptive CSV outputs were refreshed.
- The exported CSVs contained no duplicate rows or infinite numeric values.
- All database integrity and data-quality checks passed.

### Required notebook documentation correction

The notebook's opening **Current Sample Caveat** still describes an older
500-game extraction that required a high rating count and a summary. That text
does not describe the database used by the current notebook run.

The correct current sample is:

```text
15,000 released main games
1,000 games from each year from 2010 through 2024
name, release date, genre, and platform required
quality, popularity, and comparison extraction cohorts
```

All findings in this report use the current 15,000-game sample. The stale
notebook caveat should be replaced before the notebook is presented or
submitted.

Two additional terminology points should be corrected in the notebook:

- `total_rating_count` should be described as rating evidence or audience
  rating activity, not as the primary visibility measure. PopScore is the
  project's visibility signal.
- The combined `metadata_richness` field is a relationship-volume summary. It
  should not be described as objective metadata quality.

---

## 2. Executive Summary

The descriptive analytics pillar establishes what the project catalog
contains, how complete its major fields are, and where important coverage gaps
remain.

The main findings are:

1. **The database is structurally healthy.**
   - SQLite integrity passed.
   - No foreign-key violations were found.
   - No duplicate bridge relationships were detected.
   - Required names, rating ranges, rating counts, and release-date components
     passed validation.

2. **The catalog is intentionally balanced by release year.**
   - It contains exactly 1,000 games for every year from 2010 through 2024.
   - Year counts therefore reflect the extraction design, not the natural
     number of games released in each year.

3. **The sample is dominated by PC, indie, adventure, and action-related
   content.**
   - PC appears on 71.6% of games.
   - Indie is assigned to 47.9% of games.
   - Adventure is assigned to 40.2%.
   - Action is the most common theme at 43.8%.

4. **Core identification and release fields are highly complete.**
   - Name, release year, first release date, genre, platform, and release-date
     relationships have 100% coverage.
   - Summaries cover 97.1% of games.
   - Covers cover 96.3%.
   - Websites cover 97.7%.

5. **Ratings have limited coverage.**
   - Only 41.9% of games have a combined total rating.
   - User ratings cover 40.0%.
   - Critic ratings cover 25.6%.
   - Rating charts describe a minority of the catalog and are influenced by
     the quality and popularity extraction cohorts.

6. **Storyline, multiplayer-detail, and playtime fields are sparse.**
   - Storylines cover 20.5% of games.
   - Detailed multiplayer records cover 12.2%.
   - Normal-completion playtime covers 13.1%.

7. **Media coverage is strong.**
   - 96.3% of games have a cover.
   - 91.4% have at least one screenshot.
   - 89.3% have both.

8. **Metadata volume is highly uneven.**
   - The median game has 21 normalized relationship records.
   - 86.0% of games fall below 50 relationships.
   - A small number of games have exceptionally dense metadata profiles.

9. **Keyword data is useful but requires cleanup.**
   - The sample contains 3,972 represented keywords.
   - 751 keywords occur only once.
   - 2,441 occur fewer than 10 times.
   - Store/platform terms, event-year tags, very short terms, and compound
     award labels should be reviewed before use in search or recommendation.

---

## 3. Sample Definition and Interpretation

### 3.1 Curated extraction

The current database contains exactly 15,000 main games:

| Release period | Years | Games |
|---|---:|---:|
| 2010s | 2010–2019 | 10,000 |
| 2020s | 2020–2024 | 5,000 |
| **Total** | **2010–2024** | **15,000** |

The sample contains three mutually exclusive extraction cohorts:

| Cohort | Games | Purpose |
|---|---:|---|
| Quality | 1,418 | Stronger-rated games selected using a reliable yearly quality rule |
| Popularity | 3,000 | PopScore-visible games selected after quality games |
| Comparison | 10,582 | Reproducible sample from remaining eligible games |

This is not a random sample of the complete IGDB catalog. It deliberately
oversamples games with stronger reception or visibility.

### 3.2 Consequences for descriptive interpretation

The following rules apply:

- Counts describe the project sample, not the complete video game market.
- Category percentages may be influenced by the extraction cohorts.
- Rating distributions should not be interpreted as the prevalence of good
  or bad games in the market.
- Release-year counts cannot be used to infer industry growth because every
  year was fixed at 1,000 games.
- Genre, theme, platform, mode, perspective, and company categories overlap.
  Their counts cannot be added together to obtain unique-game totals.

---

## 4. Database Scale and Data Quality

### 4.1 Core database scale

The normalized relational database contains:

| Entity or relationship | Rows |
|---|---:|
| Games | 15,000 |
| Companies | 8,176 |
| Platforms | 99 |
| Genres | 23 |
| Themes | 22 |
| Keywords | 3,972 |
| Game-genre relationships | 34,521 |
| Game-theme relationships | 19,246 |
| Game-keyword relationships | 83,124 |
| Game-platform relationships | 35,407 |
| Involved-company relationships | 18,359 |
| Release-date records | 43,447 |
| Website records | 69,490 |
| External-game records | 58,102 |
| Screenshots | 83,764 |
| Popularity primitives | 60,447 |
| Multiplayer-mode records | 2,474 |
| Time-to-beat records | 2,316 |

The scale of the bridge tables confirms that most classifications and
availability fields are many-to-many.

### 4.2 Data-quality checks

All 12 implemented quality checks passed:

| Check | Result |
|---|---|
| SQLite integrity | Pass |
| Foreign-key failures | 0 |
| Empty core tables | 0 |
| Missing required names | 0 |
| Invalid rating ranges | 0 |
| Negative rating counts | 0 |
| Invalid release months | 0 |
| Invalid release days | 0 |
| Duplicate game-genre relationships | 0 |
| Duplicate game-theme relationships | 0 |
| Duplicate game-keyword relationships | 0 |
| Duplicate game-platform relationships | 0 |

The database is suitable for the project's analytical work. Remaining issues
are primarily coverage and vocabulary concerns rather than relational
integrity failures.

---

## 5. Catalog Composition

### 5.1 Game type

All 15,000 games are classified as **Main Game**.

This is intentional and prevents expansions, bundles, editions, ports, and
other version records from dominating catalog counts.

### 5.2 Game status

| Game status | Games | Share |
|---|---:|---:|
| No explicit status | 13,600 | 90.7% |
| Early Access | 670 | 4.5% |
| Delisted | 458 | 3.1% |
| Offline | 166 | 1.1% |
| Beta | 57 | 0.4% |
| Alpha | 48 | 0.3% |
| Released | 1 | Less than 0.1% |

An absent game-status value does not mean the game is unreleased. IGDB status
values are primarily used for exceptional lifecycle states. Release timing is
represented separately through first release dates and release-date records.

### 5.3 Genre composition

Every game has at least one genre because genre presence was required during
extraction.

| Genre | Games | Share of sample |
|---|---:|---:|
| Indie | 7,186 | 47.9% |
| Adventure | 6,027 | 40.2% |
| Simulator | 2,849 | 19.0% |
| Role-playing | 2,762 | 18.4% |
| Strategy | 2,699 | 18.0% |
| Puzzle | 2,458 | 16.4% |
| Arcade | 1,540 | 10.3% |
| Shooter | 1,530 | 10.2% |
| Platform | 1,482 | 9.9% |
| Sport | 900 | 6.0% |
| Visual Novel | 892 | 5.9% |

The catalog has a strong indie and adventure orientation. Because games can
have multiple genres, 47.9% Indie and 40.2% Adventure do not describe
mutually exclusive segments.

The median game has two genres:

- Mean genres per game: 2.30.
- Median: 2.
- 75th percentile: 3.
- Maximum: 10.

### 5.4 Theme composition

Themes cover 10,817 games, or 72.1% of the sample.

| Theme | Games | Share of sample |
|---|---:|---:|
| Action | 6,573 | 43.8% |
| Fantasy | 2,265 | 15.1% |
| Science fiction | 1,565 | 10.4% |
| Horror | 1,163 | 7.8% |
| Comedy | 1,056 | 7.0% |
| Mystery | 662 | 4.4% |
| Survival | 609 | 4.1% |
| Open world | 589 | 3.9% |
| Historical | 552 | 3.7% |
| Kids | 510 | 3.4% |

Action is much more common than any other theme. Theme coverage remains
incomplete: 4,183 games have no theme relationship.

The median game has one theme, while the maximum is eight.

---

## 6. Platform Coverage

### 6.1 Overall platform availability

All games have at least one platform because platform presence was required
during extraction.

The sample contains 99 represented platforms and 35,407 game-platform
relationships.

| Platform | Games | Share of sample |
|---|---:|---:|
| PC (Microsoft Windows) | 10,735 | 71.6% |
| Mac | 3,027 | 20.2% |
| iOS | 2,608 | 17.4% |
| PlayStation 4 | 2,502 | 16.7% |
| Nintendo Switch | 2,342 | 15.6% |
| Android | 2,204 | 14.7% |
| Xbox One | 2,161 | 14.4% |
| Linux | 2,018 | 13.5% |
| PlayStation 5 | 1,159 | 7.7% |
| Xbox Series X\|S | 1,041 | 6.9% |
| Web browser | 917 | 6.1% |

PC is the dominant platform by a wide margin. Mobile operating systems,
eighth-generation consoles, Linux, and Mac also have substantial coverage.

### 6.2 Number of platforms per game

| Statistic | Platforms per game |
|---|---:|
| Mean | 2.36 |
| Median | 1 |
| 75th percentile | 3 |
| 90th percentile | 5 |
| 95th percentile | 6 |
| Maximum | 16 |

The median of one platform shows that single-platform availability is common,
while a smaller group of games has broad multi-platform distribution.

### 6.3 Platform families

| Platform family | Games |
|---|---:|
| Unknown or no family | 13,162 |
| Linux | 3,969 |
| PlayStation | 3,682 |
| Nintendo | 3,248 |
| Xbox | 2,955 |
| Sega | 23 |

The large Unknown/No Family category does not mean platform data is absent.
Many platforms, including PC and mobile operating systems, are not assigned to
a console-style family.

### 6.4 Platform types

| Platform type | Games |
|---|---:|
| Operating system | 12,441 |
| Console | 4,778 |
| Portable console | 1,212 |
| Platform | 1,129 |
| Unknown or no type | 200 |
| Arcade | 85 |
| Computer | 34 |

Platform-type counts overlap because games can be available on several types.

---

## 7. Release-Year and Release-Metadata Findings

### 7.1 Release-year distribution

Every release year from 2010 through 2024 contains exactly 1,000 games.

This is a validation of the extraction quota. It is not evidence that release
volume remained constant over time.

### 7.2 Release-date relationship density

The database contains 43,447 release-date records:

- Average: 2.90 release-date records per game.
- Every game has at least one release-date relationship.
- Multiple records commonly reflect different platforms, regions, formats, or
  statuses.

### 7.3 Date precision

| Date format | Games with at least one record | Share |
|---|---:|---:|
| Full date (`YYYYMMDD`) | 14,615 | 97.4% |
| Year only | 444 | 3.0% |
| To be determined | 341 | 2.3% |
| Year and month | 117 | 0.8% |

These percentages overlap because one game can have multiple release-date
records with different levels of precision.

### 7.4 Release regions

| Region | Games | Share |
|---|---:|---:|
| Worldwide | 13,110 | 87.4% |
| North America | 3,355 | 22.4% |
| Europe | 2,228 | 14.9% |
| Japan | 1,597 | 10.7% |
| Australia | 464 | 3.1% |

Regional counts overlap. Worldwide release records dominate the sample.

### 7.5 Release-date statuses

| Release-date status | Games | Share |
|---|---:|---:|
| Unknown release status | 10,751 | 71.7% |
| Full Release | 4,594 | 30.6% |
| Early Access | 597 | 4.0% |
| Offline | 90 | 0.6% |
| Beta | 82 | 0.6% |
| Cancelled release record | 52 | 0.4% |

A cancelled release-date record does not necessarily mean the entire game was
cancelled. It may describe one platform or regional release while another
release record remains valid.

---

## 8. Rating Coverage and Distribution

### 8.1 Rating-field coverage

| Rating field | Games | Coverage |
|---|---:|---:|
| Combined total rating | 6,278 | 41.9% |
| Combined total rating count | 6,278 | 41.9% |
| User rating | 5,993 | 40.0% |
| User rating count | 5,993 | 40.0% |
| Aggregated critic rating | 3,839 | 25.6% |
| Aggregated critic rating count | 3,839 | 25.6% |

Most games do not have a combined rating. Critic coverage is especially
limited.

### 8.2 Rating bands

| Rating band | Games | Share of all games | Share of rated games |
|---|---:|---:|---:|
| Excellent: 90+ | 178 | 1.2% | 2.8% |
| Highly rated: 80–89.99 | 1,241 | 8.3% | 19.8% |
| Good: 70–79.99 | 2,522 | 16.8% | 40.2% |
| Mixed/average: 60–69.99 | 1,295 | 8.6% | 20.6% |
| Lower rated: below 60 | 1,042 | 6.9% | 16.6% |
| No combined rating | 8,722 | 58.1% | Not applicable |

Among rated games, the largest group falls between 70 and 80.

### 8.3 Reliability caveat

The descriptive rating bands include every non-null `total_rating`, regardless
of rating count. They should not be interpreted as reliable quality classes.

For example:

- The descriptive tables contain 1,419 games rated at least 80.
- The diagnostic reliability rule retains only 775 games rated at least 80
  with at least 25 ratings.

The diagnostic figure is the appropriate count when reliable high-rating
evidence is required.

### 8.4 Sampling caveat

The extraction includes an explicit quality cohort, so the rating distribution
is deliberately more favorable than a random market sample would be. The
rating-band percentages are catalog descriptions only.

---

## 9. Company Representation

### 9.1 Company coverage

The database contains 8,176 represented companies.

Company relationships cover 10,608 games, or 70.7% of the sample.

| Role | Games | Share of sample | Relationship records |
|---|---:|---:|---:|
| Developer | 10,011 | 66.7% | 10,919 |
| Publisher | 9,745 | 65.0% | 11,764 |
| Porting | 450 | 3.0% | 514 |
| Supporting | 451 | 3.0% | 743 |

A company can hold multiple roles for the same game.

### 9.2 Most represented developers

| Developer | Games |
|---|---:|
| Capcom | 36 |
| Gameloft | 35 |
| Otomate | 29 |
| Konami | 27 |
| Nintendo | 25 |
| Omega Force | 24 |
| Ubisoft Montreal | 24 |
| EA Canada | 22 |
| Spike Chunsoft | 21 |
| Visual Concepts | 21 |

Developer counts are relatively dispersed. Even the most represented
developer appears on only 36 of 15,000 games.

### 9.3 Most represented publishers

| Publisher | Games |
|---|---:|
| Nintendo | 212 |
| Square Enix | 132 |
| Ubisoft Entertainment | 128 |
| Sega | 114 |
| Bandai Namco Entertainment | 112 |
| Electronic Arts | 101 |
| Sony Computer Entertainment | 86 |
| Activision | 75 |
| Devolver Digital | 75 |
| Focus Entertainment | 69 |

Publisher representation is more concentrated than developer representation,
but the long tail remains substantial.

---

## 10. Text Coverage

### 10.1 Summary coverage

Summaries are available for 14,564 games, or 97.1%.

| Summary band | Games | Typical length |
|---|---:|---:|
| Missing | 436 | 0 |
| Short: under 250 characters | 7,021 | Median 154 |
| Medium: 250–749 characters | 6,610 | Median 355 |
| Long: 750+ characters | 933 | Median 960 |

Summary-length statistics:

- Overall median: 251 characters.
- 90th percentile: 625.
- 95th percentile: 811.
- Maximum: 4,718.

Most games have enough summary text for a basic profile, although almost half
of the summaries are short.

### 10.2 Storyline coverage

Storylines are available for 3,072 games, or 20.5%.

| Storyline band | Games | Typical length |
|---|---:|---:|
| Missing | 11,928 | 0 |
| Short: under 250 characters | 529 | Median 181 |
| Medium: 250–749 characters | 1,804 | Median 442 |
| Long: 750+ characters | 739 | Median 1,029 |

Storyline coverage is too sparse to be a universal catalog field. It is useful
when available but should not be required for every downstream game profile.

---

## 11. Relationship Coverage and Metadata Volume

### 11.1 Relationship coverage

| Relationship | Games covered | Coverage |
|---|---:|---:|
| Genre | 15,000 | 100.0% |
| Platform | 15,000 | 100.0% |
| Release date | 15,000 | 100.0% |
| Website | 14,650 | 97.7% |
| External source | 14,913 | 99.4% |
| Cover | 14,446 | 96.3% |
| Screenshot | 13,714 | 91.4% |
| Game mode | 13,328 | 88.9% |
| Theme | 10,817 | 72.1% |
| Company | 10,608 | 70.7% |
| Keyword | 8,903 | 59.4% |
| Player perspective | 8,903 | 59.4% |

The extraction guarantees genre, platform, and release-date coverage. Theme,
company, keyword, and player-perspective coverage remain incomplete.

### 11.2 Typical relationship counts

| Relationship | Mean per game | Median | 95th percentile | Maximum |
|---|---:|---:|---:|---:|
| Genres | 2.30 | 2 | 5 | 10 |
| Themes | 1.28 | 1 | 4 | 8 |
| Keywords | 5.54 | 1 | 26 | 213 |
| Platforms | 2.36 | 1 | 6 | 16 |
| Companies | 1.22 | 1 | 3 | 18 |
| Game modes | 1.27 | 1 | 3 | 6 |
| Player perspectives | 0.69 | 1 | 2 | 5 |
| Websites | 4.63 | 3 | 13 | 20 |
| External sources | 3.87 | 2 | 12 | 93 |
| Screenshots | 5.58 | 5 | 12 | 55 |

Keyword and external-source counts are strongly right-skewed. A small number
of games have exceptionally dense relationship profiles.

### 11.3 Aggregate relationship-volume bands

The notebook sums several heterogeneous relationship counts into a
`metadata_relationship_count`. This describes volume, not objective metadata
quality.

| Relationship-volume band | Games | Share |
|---|---:|---:|
| Lean: fewer than 50 links | 12,895 | 86.0% |
| Moderate: 50–99 | 1,861 | 12.4% |
| Rich: 100–149 | 196 | 1.3% |
| Very rich: 150+ | 48 | 0.3% |

Across all games:

- Mean relationship count: 28.76.
- Median: 21.
- 90th percentile: 56.
- 95th percentile: 70.
- Maximum: 321.

The combined total should not be interpreted as a game-quality score because
one additional keyword, screenshot, platform, company, or website does not
have the same meaning.

---

## 12. Media Coverage

### 12.1 Cover and screenshot availability

| Media measure | Games | Coverage |
|---|---:|---:|
| Has cover | 14,446 | 96.3% |
| Has screenshot | 13,714 | 91.4% |
| Has both cover and screenshot | 13,395 | 89.3% |
| Has neither | 235 | 1.6% |

The sample is well prepared for visual dashboards and game-detail pages.

### 12.2 Screenshot counts

| Screenshot count | Games | Share |
|---|---:|---:|
| 0 | 1,286 | 8.6% |
| 1 | 665 | 4.4% |
| 2–3 | 1,568 | 10.5% |
| 4–6 | 7,443 | 49.6% |
| 7+ | 4,038 | 26.9% |

More than three-quarters of the catalog has at least four screenshots.

### 12.3 Image technical completeness

| Image type | Records | With dimensions | With URL |
|---|---:|---:|---:|
| Covers | 14,446 | 99.97% | 100.0% |
| Screenshots | 83,764 | 99.95% | 100.0% |

Image records are technically complete, with almost universal URLs and
dimensions.

---

## 13. Websites and External Sources

### 13.1 Website coverage

Websites cover 14,650 games, or 97.7%. The database contains 69,490 website
records, averaging 4.63 per game.

| Website type | Games | Coverage |
|---|---:|---:|
| Twitch | 11,921 | 79.5% |
| Official website | 8,822 | 58.8% |
| Steam | 8,808 | 58.7% |
| Twitter | 4,682 | 31.2% |
| YouTube | 3,875 | 25.8% |
| Wikipedia | 3,360 | 22.4% |
| Facebook | 3,229 | 21.5% |
| Discord | 2,696 | 18.0% |
| Community Wiki | 2,613 | 17.4% |

The catalog is strongly connected to streaming, storefront, official, and
social-media sources.

### 13.2 External-game source coverage

External source relationships cover 14,913 games, or 99.4%. The database
contains 58,102 external-game records.

| External source | Games | Coverage |
|---|---:|---:|
| Twitch | 14,432 | 96.2% |
| Steam | 8,848 | 59.0% |
| GiantBomb | 6,061 | 40.4% |
| PlayStation Store US | 2,542 | 17.0% |
| Microsoft | 2,513 | 16.8% |
| Amazon | 1,631 | 10.9% |
| GOG | 1,469 | 9.8% |
| Itch.io | 1,340 | 8.9% |
| Epic Games Store | 1,227 | 8.2% |

Amazon has 13,544 records but covers only 1,631 games, indicating that some
games have many Amazon-linked records.

---

## 14. Keyword Findings and Cleanup

### 14.1 Keyword coverage

Keywords cover 8,903 games, or 59.4%. The sample contains:

- 3,972 represented keywords.
- 83,124 game-keyword relationships.
- Mean of 5.54 keywords per game.
- Median of one keyword per game.
- Maximum of 213 keywords for one game.

### 14.2 Most common keywords

| Keyword | Games |
|---|---:|
| Digital distribution | 1,848 |
| Steam | 1,115 |
| Steam achievements | 862 |
| Achievements | 720 |
| Female protagonist | 630 |
| Steam trading cards | 575 |
| Anime | 548 |
| Steam cloud | 511 |
| PlayStation trophies | 476 |
| Action-adventure | 466 |
| Polygonal 3D | 433 |
| Voice acting | 429 |
| Male protagonist | 420 |
| Casual | 412 |
| Exploration | 403 |

The frequent presence of distribution and storefront features shows that
keywords mix semantic game concepts with platform and product metadata.

### 14.3 Long-tail sparsity

| Frequency threshold | Keyword count |
|---|---:|
| Appears once | 751 |
| Appears fewer than 5 times | 1,759 |
| Appears fewer than 10 times | 2,441 |

The vocabulary has a substantial long tail. Rare terms can improve specificity
but may also add noise.

### 14.4 Cleanup categories

| Review category | Keywords | Total game mentions |
|---|---:|---:|
| Likely semantic terms | 3,757 | 77,159 |
| Contains a number | 199 | 4,128 |
| Punctuation or compound review | 9 | 127 |
| Very short term | 6 | 595 |
| Platform/store term | 1 | 1,115 |

Examples requiring review include:

- `steam`, which is a storefront/platform term rather than game content.
- Event-year terms such as `pax west 2016`.
- Display terms such as `2d`, `3d`, and `4k`, which are valid but ambiguous
  without context.
- Long award labels such as Game Awards nominee/winner phrases.
- Slash-based compounds such as `day/night cycle`.

Keyword cleanup should preserve useful semantic terms while separating:

- Content and theme descriptors.
- Technical features.
- Storefront/platform metadata.
- Event and award labels.

---

## 15. Game Modes and Player Perspectives

### 15.1 Game-mode coverage

Game-mode labels cover 13,328 games, or 88.9%.

| Game mode | Games | Share of sample |
|---|---:|---:|
| Single player | 12,702 | 84.7% |
| Multiplayer | 3,492 | 23.3% |
| Co-operative | 1,983 | 13.2% |
| MMO | 410 | 2.7% |
| Split screen | 377 | 2.5% |
| Battle Royale | 71 | 0.5% |

Modes overlap. For example, one game can support single-player,
multiplayer, and co-operative play.

### 15.2 Player-perspective coverage

Player perspectives cover 8,903 games, or 59.4%.

| Perspective | Games | Share |
|---|---:|---:|
| Bird view / Isometric | 2,393 | 16.0% |
| Third person | 2,351 | 15.7% |
| Side view | 2,334 | 15.6% |
| First person | 1,992 | 13.3% |
| Text | 851 | 5.7% |
| Virtual Reality | 301 | 2.0% |
| Auditory | 74 | 0.5% |

No single perspective dominates. Bird view, third person, side view, and first
person have broadly similar representation.

---

## 16. Detailed Multiplayer Coverage

Detailed multiplayer records cover only 1,836 games, or 12.2%.

| Multiplayer feature | Games | Share of sample |
|---|---:|---:|
| Online co-op | 860 | 5.7% |
| Offline/local co-op | 585 | 3.9% |
| Campaign co-op | 537 | 3.6% |
| Drop-in multiplayer | 397 | 2.7% |
| Split screen | 235 | 1.6% |
| LAN co-op | 165 | 1.1% |
| Offline player maximum above zero | 802 | 5.4% |
| Online player maximum above zero | 1,007 | 6.7% |

Missing multiplayer-detail records mean unknown, not confirmed absence.

### 16.1 Recorded player capacities

Among records with a positive maximum:

- Offline/local support is most commonly two players.
- Online support is most commonly three to four players.
- 133 games have recorded online maxima of 17 or more players.

These figures only describe games with detailed multiplayer records.

---

## 17. Playtime Coverage and Distribution

### 17.1 Coverage

| Playtime field | Games | Coverage |
|---|---:|---:|
| Any time-to-beat record | 2,316 | 15.4% |
| Normal completion estimate | 1,961 | 13.1% |
| Quick completion estimate | 1,317 | 8.8% |
| Completionist estimate | 1,438 | 9.6% |

Playtime is one of the sparsest analytical areas in the catalog.

### 17.2 Normal-completion bands

The 1,961 games with normal-completion estimates are distributed as follows:

| Normal playtime | Games | Median hours |
|---|---:|---:|
| Under 5 hours | 410 | 3.0 |
| 5–9 hours | 471 | 7.0 |
| 10–19 hours | 417 | 13.5 |
| 20–39 hours | 315 | 25.9 |
| 40–79 hours | 206 | 50.0 |
| 80+ hours | 142 | 150.0 |

The three shortest bands account for 1,298 games, or 66.2% of games with a
normal estimate.

### 17.3 Extreme outliers

The 80+ hour band is extremely skewed:

- 95th percentile: 3,237.5 hours.
- Maximum: 277,430.5 hours.

The outlier list includes open-ended, multiplayer, idle, and live-service
games such as Gorilla Tag, Rocket League Sideswipe, VRChat, Albion Online,
Cookie Clicker, Dota 2, and Fortnite.

Some extreme values are not meaningful estimates of a finite campaign.
Playtime should therefore be:

- Treated as missing for games without estimates.
- Log-transformed or winsorized for statistical summaries.
- Interpreted cautiously for live-service and open-ended games.
- Supported by observation counts where possible.

---

## 18. Popularity-Signal Availability

The database contains 60,447 popularity primitive records across 11
source/type combinations.

| Source and signal | Games | Coverage |
|---|---:|---:|
| IGDB Played | 7,949 | 53.0% |
| Steam Negative Reviews | 7,473 | 49.8% |
| Steam Total Reviews | 7,462 | 49.7% |
| Steam Positive Reviews | 7,462 | 49.7% |
| Steam 24-hour Peak Players | 7,462 | 49.7% |
| IGDB Want to Play | 7,267 | 48.4% |
| IGDB Playing | 5,102 | 34.0% |
| IGDB Visits | 5,027 | 33.5% |
| Twitch 24-hour Hours Watched | 3,415 | 22.8% |
| Steam Global Top Sellers | 1,821 | 12.1% |
| Steam Most Wishlisted Upcoming | 7 | Less than 0.1% |

These signals have different units and meanings. They must not be averaged
directly into a single raw popularity score.

### Vocabulary cleanup note

The source lookup currently displays `Postitive Reviews`. This should be
corrected to `Positive Reviews` in the lookup data or display layer.

---

## 19. Catalog Strengths

The catalog is particularly strong in the following areas:

1. **Release-year balance**
   - Exactly 1,000 games per year supports consistent year-based comparisons.

2. **Core classification**
   - Genre, platform, and release-date coverage are complete.

3. **Summary text**
   - 97.1% of games have summaries.

4. **Media**
   - Covers and screenshots are broadly available and technically complete.

5. **External identity**
   - 99.4% of games have an external-source relationship.
   - 97.7% have website records.

6. **Relational integrity**
   - All implemented integrity, range, and duplicate checks passed.

7. **Diverse normalized metadata**
   - The database supports genres, themes, keywords, platforms, companies,
     release dates, modes, perspectives, websites, external sources, media,
     multiplayer details, playtime, ratings, and popularity primitives.

---

## 20. Catalog Gaps and Risks

### 20.1 Sparse ratings

Most games have no combined rating, and only 16.7% satisfy the diagnostic
reliability threshold of 25 ratings.

### 20.2 Sparse storylines

Nearly four out of five games have no storyline.

### 20.3 Incomplete semantic relationships

Theme, keyword, company, and player-perspective coverage are incomplete.

### 20.4 Sparse multiplayer and playtime data

Detailed multiplayer and normal playtime cover only about one in eight games.

### 20.5 Keyword noise and long-tail sparsity

Storefront terms, event-year labels, compound awards, and very rare terms may
reduce search quality unless reviewed.

### 20.6 Uneven metadata volume

A small group of highly documented games has far more websites, external
sources, keywords, screenshots, and relationships than the typical game.

### 20.7 Curated-sample bias

The extraction deliberately oversamples quality and visibility cohorts.
Descriptive percentages should not be generalized to the full IGDB catalog.

---

## 21. Final Descriptive Answer

The descriptive pillar answers the question **“What does the current game
catalog look like?”** as follows:

> The project catalog is a balanced, curated collection of 15,000 main games
> released from 2010 through 2024. It is strongly represented by PC, indie,
> adventure, action, simulation, role-playing, strategy, and puzzle games.
> Core identity, release, genre, platform, summary, media, website, and
> external-source fields are highly complete. Rating, storyline, keyword,
> company, perspective, multiplayer-detail, and playtime coverage are more
> limited. Metadata depth varies substantially between games, with a small
> number of highly documented titles and a large long tail of leaner profiles.
> The database is relationally healthy and suitable for downstream analytics,
> but its curated extraction and uneven field coverage must remain explicit in
> all interpretations.

The central descriptive narrative is:

```text
The catalog is structurally reliable and rich in core discovery metadata.
It is strongest for identity, release, platform, genre, summary, media, and links.
It is weaker for reliable ratings, storylines, multiplayer detail, and playtime.
Its composition describes a curated project sample, not the full game market.
```
