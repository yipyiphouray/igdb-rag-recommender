# Diagnostic Analytics Pillar Findings

## IGDB Game Discovery Project

**Pillar:** Diagnostic Analytics  
**Dataset:** Curated 15,000-game IGDB sample  
**Release years:** 2010–2024  
**Games per year:** 1,000  
**Primary notebook:** [`02_diagnostic_analytics_exploration.ipynb`](../../notebooks/02_diagnostic_analytics_exploration.ipynb)  
**Analysis plan:** [`diagnostic_analytics_pillar_plan.md`](../diagnostic_analytics_pillar_plan.md)  
**Diagnostic outputs:** [`data/analytics/diagnostic/`](../../data/analytics/diagnostic/)

---

## 1. Executive Summary

The diagnostic analysis examined how game reception, rating activity, IGDB
PopScore visibility, genre and theme membership, platform reach, company
involvement, metadata coverage, gameplay format, multiplayer support, and
playtime relate to one another in the curated IGDB sample.

The most important findings are:

1. **Rating quality, rating activity, and PopScore visibility are related but
   distinct signals.**
   - Total rating and PopScore had a Spearman correlation of **0.331**.
   - Total rating and rating count had a Spearman correlation of **0.294**.
   - Neither relationship is strong enough to justify treating visibility,
     audience activity, and quality as interchangeable.

2. **The project identified 229 low-visibility, high-quality candidates.**
   - Each candidate belongs to the quality cohort.
   - Each has a total rating of at least 80 and at least 25 ratings.
   - Each falls at or below the within-year 40th visibility percentile among
     PopScore-covered quality-cohort games.
   - These are within-sample discovery candidates, not market-wide hidden-gem
     estimates.

3. **User and critic ratings generally agree, but meaningful disagreement
   remains.**
   - Spearman correlation: **0.696**.
   - The median user-minus-critic gap was **-3.04 points**, indicating that
     critics rated the typical game in this analysis slightly higher than
     users.

4. **Platform reach had a positive but moderate relationship with PopScore
   visibility.**
   - Number of platforms versus PopScore percentile had a Spearman correlation
     of approximately **0.297**.
   - Wider availability is associated with more visibility, but the analysis
     does not establish that platform expansion causes visibility.

5. **Metadata coverage was much more strongly related to visibility than to
   rating quality.**
   - External-link count had the strongest metadata relationship with
     PopScore: **rho = 0.627**.
   - Most metadata-to-rating relationships were weak.
   - Metadata richness appears to reflect documentation and commercial
     visibility more than inherent game quality.

6. **Genres, themes, companies, and genre-theme combinations showed strong
   extraction-cohort enrichment patterns.**
   - These results describe which categories are overrepresented in the
     quality cohort relative to the residual comparison cohort.
   - They must not be interpreted as proof that those categories cause better
     ratings.

---

## 2. Interpretation Rules

### 2.1 The sample is curated rather than market-representative

The extraction contains three mutually exclusive cohorts:

| Cohort | Games | Purpose |
|---|---:|---|
| Quality | 1,418 | Reliable, stronger-rated games selected using the yearly quality rule |
| Popularity | 3,000 | Up to 200 highly visible games per year after removing quality selections |
| Comparison | 10,582 | Reproducible sample from the remaining eligible games |
| **Total** | **15,000** | **1,000 games for each year from 2010 through 2024** |

The quality and popularity cohorts were intentionally oversampled. Therefore:

- Full-sample high-rating shares are not market prevalence estimates.
- The comparison cohort is residual: quality-selected and popularity-selected
  games were removed before comparison games were selected.
- Quality-versus-comparison odds ratios measure **quality-cohort enrichment
  under the extraction design**, not a direct effect on game quality.
- Results show associations, not causation.

### 2.2 Core analytical terms

| Term | Meaning in this project |
|---|---|
| `total_rating` | Combined game reception or rating quality |
| `total_rating_count` | Rating evidence and audience-rating activity |
| IGDB interest score | `0.60 × Want to Play + 0.40 × Playing` |
| PopScore visibility | Current interest/visibility signal derived from IGDB popularity primitives |
| Reliable rating | `total_rating_count >= 25` |
| High-rated game | Reliable game with `total_rating >= 80` |
| Low-visibility, high-quality candidate | Quality-cohort game meeting the balanced candidate rule |

Missing PopScore is treated as **visibility unknown**, not as zero visibility.

---

## 3. Dataset Validation and Analytical Coverage

All core validation checks passed:

| Validation item | Result |
|---|---:|
| SQLite integrity check | Passed (`ok`) |
| Foreign-key violations | 0 |
| Total games | 15,000 |
| Release years | 15 |
| Years containing exactly 1,000 games | 15 |
| Games missing an extraction cohort | 0 |

### 3.1 Rating and PopScore coverage

| Coverage measure | Games | Share of 15,000 |
|---|---:|---:|
| Games with `total_rating` | 6,278 | 41.9% |
| Games with a reliable rating | 2,498 | 16.7% |
| Reliable games rated at least 80 | 775 | 5.2% |
| Games with project IGDB PopScore | 4,821 | 32.1% |

The 775 high-rated reliable games represent 31.0% of the reliable-rating
subset, but this is not a market prevalence statistic because the extraction
deliberately contains a quality cohort.

### 3.2 Coverage differs sharply by extraction cohort

| Cohort | Games | Reliable ratings | Reliable-rating coverage | PopScore games | PopScore coverage |
|---|---:|---:|---:|---:|---:|
| Comparison | 10,582 | 29 | 0.3% | 457 | 4.3% |
| Popularity | 3,000 | 1,051 | 35.0% | 3,000 | 100.0% |
| Quality | 1,418 | 1,418 | 100.0% | 1,364 | 96.2% |

This coverage imbalance is one of the most important limitations of the
project sample. Rating-based comparisons are dominated by quality and
popularity games, while PopScore analyses have very little comparison-cohort
coverage.

### 3.3 PopScore coverage by year

Annual PopScore coverage was relatively stable, ranging from:

- **28.3% in 2010**, the lowest year.
- **35.6% in 2016**, the highest year.

The yearly range is narrow enough for within-year visibility comparisons, but
the cohort imbalance remains substantial in every year.

---

## 4. Rating Quality, Rating Activity, and Visibility

### 4.1 Quality versus PopScore visibility

Among 2,425 reliable games with PopScore:

| Scope | Games | Spearman correlation | Interpretation |
|---|---:|---:|---|
| Overall | 2,425 | 0.331 | Moderate positive association |
| Quality cohort | 1,364 | 0.309 | Moderate positive association |
| Popularity cohort | 1,051 | 0.181 | Weak positive association |
| Comparison cohort | 10 | Not reported | Insufficient sample |

Higher-rated games tended to have more IGDB interest, but the relationship was
far from deterministic. The scatter plot contains:

- Highly rated games at both low and high visibility levels.
- Popular games with only moderate or low ratings.
- A clear extraction-cohort boundary because cohort membership depends partly
  on rating and visibility.

The correlation weakened in more recent release-year bands:

| Release-year band | Games | Spearman correlation |
|---|---:|---:|
| 2010–2014 | 774 | 0.345 |
| 2015–2019 | 1,000 | 0.315 |
| 2020–2024 | 651 | 0.232 |

This decline may reflect changing audience behavior, different observation
windows for newer releases, or sample composition. The current analysis does
not identify which explanation is responsible.

### 4.2 Quality versus rating activity

Across the 2,498 reliable games:

| Scope | Games | Spearman correlation |
|---|---:|---:|
| Overall | 2,498 | 0.294 |
| Quality cohort | 1,418 | 0.256 |
| Popularity cohort | 1,051 | 0.196 |
| Comparison cohort | 29 | 0.196, not statistically significant |

The result indicates that better-rated games tend to attract more rating
activity, but rating count is not a quality measure by itself.

The relationship was strongest for older games:

| Release-year band | Spearman correlation |
|---|---:|
| 2010–2014 | 0.404 |
| 2015–2019 | 0.306 |
| 2020–2024 | 0.229 |

Older releases have had more time to accumulate ratings, which likely
contributes to this pattern.

### 4.3 Rating bands and visibility

Within the quality cohort:

| Rating band | Games | Median rating | Median rating count | Median PopScore percentile |
|---|---:|---:|---:|---:|
| Excellent | 52 | 92.38 | 372 | 0.967 |
| Highly rated | 723 | 83.42 | 113 | 0.836 |
| Good | 643 | 77.38 | 62 | 0.689 |

Excellent quality-cohort games were generally more visible and had much
stronger rating evidence than merely good games. This is consistent with the
positive correlations, but it remains influenced by the quality-cohort
selection process.

---

## 5. Low-Visibility, High-Quality Candidates

### 5.1 Balanced candidate definition

The main candidate rule was:

```text
extraction cohort = quality
total_rating >= 80
total_rating_count >= 25
main game = yes
PopScore available
within-year visibility percentile among eligible quality games <= 40%
```

This produced **229 candidates**, equal to **16.8%** of the 1,364 eligible
quality-cohort games with PopScore.

The label means:

> The game has reliable, strong reception but relatively low IGDB interest
> compared with other quality-cohort games released in the same year.

It does not mean:

> The game is objectively unknown or overlooked across the entire video game
> market.

### 5.2 Sensitivity analysis

| Version | Rating threshold | Visibility threshold | Candidates | Share of eligible games | Median rating |
|---|---:|---:|---:|---:|---:|
| Conservative | 85 | Bottom 25% | 47 | 3.4% | 87.77 |
| Balanced | 80 | Bottom 40% | 229 | 16.8% | 83.45 |
| Broad | 75 | Bottom 50% | 678 | 49.7% | 79.47 |

The conservative version provides a smaller list with stronger ratings. The
broad version includes almost half of the eligible pool and is therefore less
selective.

### 5.3 Candidate distribution by year

Every release year contributed candidates:

| Year | Candidates | Year | Candidates | Year | Candidates |
|---:|---:|---:|---:|---:|---:|
| 2010 | 12 | 2015 | 14 | 2020 | 19 |
| 2011 | 12 | 2016 | 17 | 2021 | 18 |
| 2012 | 11 | 2017 | 15 | 2022 | 17 |
| 2013 | 11 | 2018 | 17 | 2023 | 18 |
| 2014 | 12 | 2019 | 21 | 2024 | 15 |

Using within-year percentiles prevents older or newer games from being judged
against a single global visibility cutoff.

### 5.4 Illustrative candidates

The candidate file is ordered using quality percentile, inverse visibility,
and rating evidence. Examples near the top include:

| Game | Year | Total rating | Rating count | Within-year visibility percentile |
|---|---:|---:|---:|---:|
| Town Star | 2020 | 93.32 | 34 | 0.022 |
| Undertale Yellow | 2023 | 99.21 | 25 | 0.036 |
| Lurkers | 2019 | 97.30 | 36 | 0.101 |
| Gakuen Idolmaster | 2024 | 97.30 | 26 | 0.181 |
| Escape Simulator | 2021 | 93.33 | 45 | 0.338 |
| Faith | 2017 | 93.68 | 26 | 0.192 |
| Animal Company | 2024 | 96.63 | 74 | 0.306 |
| Cataclysm: Dark Days Ahead | 2013 | 89.97 | 25 | 0.233 |
| Football Manager 2013 | 2012 | 89.31 | 46 | 0.107 |
| Transport Fever | 2016 | 88.47 | 26 | 0.053 |

Some candidates have only the minimum required rating evidence. Their scores
should therefore be interpreted less confidently than candidates with much
larger rating counts.

### 5.5 Candidate patterns by genre

The largest candidate counts occurred in broad, frequently assigned genres:

| Genre | Candidate count | Eligible quality games | Candidate share |
|---|---:|---:|---:|
| Indie | 124 | 596 | 20.8% |
| Adventure | 119 | 859 | 13.9% |
| Role-playing (RPG) | 66 | 421 | 15.7% |
| Puzzle | 60 | 314 | 19.1% |
| Simulator | 51 | 279 | 18.3% |
| Platform | 49 | 233 | 21.0% |
| Strategy | 48 | 284 | 16.9% |

Among genres with at least 20 eligible quality games, the highest candidate
shares were:

| Genre | Candidate share |
|---|---:|
| Music | 42.9% |
| Sport | 38.8% |
| Arcade | 25.5% |
| Visual Novel | 23.5% |
| Platform | 21.0% |
| Indie | 20.8% |

These shares describe where low-visibility candidates occur inside the
quality cohort. They do not estimate how common hidden gems are across all
games in those genres.

### 5.6 Candidate patterns by theme

The largest counts occurred in:

| Theme | Candidate count | Candidate share among eligible quality games |
|---|---:|---:|
| Action | 119 | 13.4% |
| Fantasy | 61 | 13.0% |
| Science fiction | 48 | 13.6% |
| Horror | 30 | 16.8% |
| Mystery | 22 | 16.3% |
| Comedy | 21 | 13.0% |

Among themes with at least 20 eligible games, Non-fiction and Business each
had a candidate share of approximately 20.7%, while Romance and Party each
had a share of 20.0%.

### 5.7 Candidate patterns by platform family

Platform-family categories overlap because a game can be available in several
families.

| Platform family | Candidate count | Candidate share |
|---|---:|---:|
| Other / Unknown | 185 | 15.7% |
| PlayStation | 129 | 13.8% |
| Nintendo | 128 | 18.7% |
| Xbox | 111 | 13.2% |
| Linux | 71 | 13.1% |

Nintendo had the highest candidate share among the major named platform
families.

---

## 6. User-versus-Critic Reception

### 6.1 Agreement

The main user-versus-critic subset contained 1,300 games with:

- At least 25 user ratings.
- At least 5 critic ratings.
- Both user and aggregated critic scores.

| Measure | Result |
|---|---:|
| Pearson correlation | 0.695 |
| Spearman correlation | 0.696 |
| Median user-minus-critic gap | -3.04 |
| Gap interquartile range | 7.71 |

Users and critics generally agree on the relative ordering of games. However,
the median negative gap indicates that critics scored the typical game about
three points higher.

### 6.2 Cohort differences

| Cohort | Games | Median user-minus-critic gap |
|---|---:|---:|
| Quality | 797 | -3.64 |
| Popularity | 500 | -1.41 |
| Comparison | 3 | Not interpretable because the sample is too small |

The quality cohort showed a larger critic-over-user gap than the popularity
cohort.

### 6.3 Release-year pattern

The median gap was negative in every release year. It became more negative in
the most recent years:

| Year | Median gap |
|---:|---:|
| 2020 | -3.82 |
| 2021 | -4.92 |
| 2022 | -4.50 |
| 2023 | -5.66 |
| 2024 | -5.21 |

This could indicate changing audience expectations or review composition, but
newer years also contain fewer qualifying user-and-critic observations.

### 6.4 Largest disagreements

Examples where users rated the game more highly than critics:

| Game | User rating | Critic rating | Gap |
|---|---:|---:|---:|
| 7 Days to Die | 68.91 | 36.13 | +32.79 |
| Pathologic 2 | 90.04 | 63.20 | +26.84 |
| James Bond 007: Blood Stone | 70.96 | 46.55 | +24.41 |
| Outward | 78.52 | 56.50 | +22.02 |
| Gods Will Be Watching | 85.78 | 64.00 | +21.78 |

Examples where critics rated the game more highly than users:

| Game | User rating | Critic rating | Gap |
|---|---:|---:|---:|
| Metal Gear Survive | 29.93 | 59.79 | -29.86 |
| Brink | 44.34 | 73.38 | -29.03 |
| OlliOlli World | 58.18 | 86.70 | -28.52 |
| NBA 2K19 | 55.72 | 82.11 | -26.39 |
| Yomawari: Night Alone | 54.37 | 80.00 | -25.63 |

These examples show why combined, user-only, and critic-only ratings should
remain separate analytical concepts.

---

## 7. Genre Findings

### 7.1 Descriptive reliable-rating patterns

Genres with the highest median reliable ratings among groups with meaningful
sample sizes included:

| Genre | Reliable games | Median rating | High-rated share |
|---|---:|---:|---:|
| Turn-based strategy | 154 | 79.18 | 44.8% |
| Visual Novel | 79 | 78.66 | 43.0% |
| Music | 61 | 78.17 | 39.3% |
| Platform | 388 | 77.42 | 36.9% |
| Puzzle | 530 | 77.29 | 33.2% |
| Point-and-click | 154 | 77.11 | 31.2% |

These medians are descriptive and combine reliable games from the quality,
popularity, and small comparison subsets.

### 7.2 Quality-cohort enrichment

The enrichment model compared quality-cohort membership against the residual
comparison cohort while controlling for release year.

Of 21 modeled genres:

- 18 remained significant after Benjamini-Hochberg correction.
- Three did not show significant enrichment after correction.

Strong positive enrichment estimates included:

| Genre | Odds ratio | 95% confidence interval |
|---|---:|---:|
| Tactical | 7.37 | 5.45–9.97 |
| Hack and slash / Beat 'em up | 6.91 | 5.40–8.84 |
| Turn-based strategy | 4.65 | 3.63–5.94 |
| Real-time strategy | 4.06 | 2.88–5.72 |
| Adventure | 3.46 | 3.08–3.89 |
| Shooter | 2.91 | 2.49–3.40 |
| Role-playing | 2.86 | 2.52–3.25 |

Categories underrepresented in the quality cohort included:

| Genre | Odds ratio | 95% confidence interval |
|---|---:|---:|
| Visual Novel | 0.55 | 0.41–0.73 |
| Arcade | 0.76 | 0.62–0.92 |
| Indie | 0.78 | 0.68–0.88 |

An apparently high median rating and a low enrichment odds ratio are not
contradictory. The median describes the reliable-rating subset, whereas the
odds ratio describes extraction-cohort membership across the quality and
residual comparison universe.

---

## 8. Theme Findings

### 8.1 Descriptive reliable-rating patterns

The highest median reliable ratings appeared in:

| Theme | Reliable games | Median rating | High-rated share |
|---|---:|---:|---:|
| Drama | 151 | 79.76 | 45.7% |
| Romance | 32 | 78.34 | 34.4% |
| Mystery | 223 | 77.67 | 35.4% |
| Fantasy | 786 | 77.32 | 36.8% |
| Non-fiction | 92 | 77.27 | 26.1% |
| Sandbox | 195 | 76.98 | 34.4% |

### 8.2 Quality-cohort enrichment

All 22 modeled themes were significant after false-discovery-rate correction.
This unusually broad significance should be interpreted in light of the
curated extraction and residual comparison design.

The strongest positive enrichment estimates were:

| Theme | Odds ratio | 95% confidence interval |
|---|---:|---:|
| Open world | 16.21 | 12.69–20.72 |
| Stealth | 11.75 | 8.53–16.17 |
| Thriller | 8.95 | 6.25–12.82 |
| Sandbox | 8.49 | 6.52–11.06 |
| Non-fiction | 7.08 | 4.99–10.04 |
| Survival | 5.78 | 4.59–7.26 |
| Science fiction | 5.47 | 4.73–6.32 |
| Fantasy | 5.01 | 4.40–5.70 |

Themes underrepresented in the quality cohort included:

| Theme | Odds ratio | 95% confidence interval |
|---|---:|---:|
| Erotic | 0.08 | 0.03–0.22 |
| Romance | 0.39 | 0.25–0.61 |
| Educational | 0.52 | 0.30–0.91 |

These findings describe extraction-cohort composition, not inherent quality
advantages or disadvantages.

---

## 9. Genre-Theme Combination Findings

Genre-theme combinations provide a more specific view of game style than
either field alone.

### 9.1 Strong median-rating combinations

Examples with at least 10 reliable games included:

| Combination | Games | Median rating | High-rated share |
|---|---:|---:|---:|
| Hack and slash + Drama | 14 | 84.51 | 78.6% |
| RPG + Drama | 50 | 82.66 | 60.0% |
| Platform + Drama | 10 | 82.44 | 60.0% |
| Hack and slash + Stealth | 11 | 82.23 | 63.6% |
| Visual Novel + Action | 17 | 82.14 | 58.8% |
| Turn-based strategy + Science fiction | 48 | 80.83 | 58.3% |

Small group sizes make several of these estimates unstable. RPG + Drama and
Turn-based strategy + Science fiction have stronger support than combinations
with only 10–14 games.

### 9.2 Candidate-rich combinations

Among combinations with at least 10 eligible quality games:

| Combination | Eligible games | Candidate share |
|---|---:|---:|
| Music + Party | 10 | 50.0% |
| Music + Action | 28 | 39.3% |
| Turn-based strategy + Comedy | 11 | 36.4% |
| Visual Novel + Fantasy | 11 | 36.4% |
| Sport + Action | 34 | 35.3% |
| Tactical + Fantasy | 34 | 29.4% |

### 9.3 Enrichment tests

Of 213 eligible genre-theme tests:

- 212 models were successfully estimated.
- 176 were significant after false-discovery-rate correction.

Some of the largest odds ratios were attached to small groups:

| Combination | Games in model universe | Odds ratio | 95% confidence interval |
|---|---:|---:|---:|
| Hack and slash + Open world | 25 | 56.50 | 16.99–187.90 |
| Shooter + Open world | 66 | 39.24 | 20.27–75.96 |
| Racing + Non-fiction | 27 | 32.73 | 12.21–87.76 |
| RPG + Stealth | 34 | 28.96 | 12.73–65.87 |
| Adventure + Open world | 236 | 21.10 | 15.82–28.13 |
| RPG + Open world | 140 | 20.71 | 14.33–29.94 |

The very wide confidence intervals for smaller combinations indicate high
uncertainty. Adventure + Open world and RPG + Open world provide more stable
evidence because their samples are larger.

---

## 10. Platform Findings

### 10.1 Platform reach and visibility

Number of platforms and PopScore percentile had a Spearman correlation of
approximately **0.297**.

Median PopScore percentile increased with reach in both the popularity and
quality cohorts:

| Reach | Popularity cohort | Quality cohort |
|---|---:|---:|
| 1 platform | 0.343 | 0.686 |
| 2–3 platforms | 0.407 | 0.779 |
| 4–6 platforms | 0.512 | 0.789 |
| 7+ platforms | 0.515 | 0.823 |

The pattern is consistent with wider distribution being associated with
greater visibility. However, well-known games may also be more likely to
receive additional ports, producing reverse direction or shared-cause
explanations.

### 10.2 Platform reach and reliable ratings

Within the quality cohort:

| Reach | Reliable games | Median rating | High-rated share | Candidate share |
|---|---:|---:|---:|---:|
| 1 platform | 198 | 81.61 | 64.6% | 25.9% |
| 2–3 platforms | 381 | 80.47 | 54.9% | 16.7% |
| 4–6 platforms | 552 | 80.07 | 51.1% | 15.7% |
| 7+ platforms | 287 | 80.59 | 54.4% | 12.9% |

Single-platform quality games had the highest median rating and candidate
share, while wider-reach quality games had greater PopScore visibility. This
supports keeping quality and visibility as separate concepts.

### 10.3 Platform-family patterns

Among major families, Nintendo had:

- The highest median reliable rating: **76.83**.
- The highest high-rated share: **33.2%**.
- The highest low-visibility candidate share: **18.7%**.

PlayStation, Xbox, Linux, and Other/Unknown had similar median ratings near
76.0–76.3. Platform families overlap and therefore cannot be summed as unique
games.

### 10.4 Platform-type patterns

Portable-console games had:

- Median rating: **77.33**.
- High-rated share: **37.0%**.
- Candidate share: **18.8%**.

The Arcade and Unknown groups had higher medians but only 12 and 37 reliable
games, respectively, so they should not be treated as stable leaders.

---

## 11. Developer and Publisher Findings

Company results are exploratory because:

- Most companies have very few reliable games.
- Company roles can overlap.
- Many company enrichment models had insufficient cohort variation.
- Several estimated odds ratios had extremely wide confidence intervals.

### 11.1 Developer descriptive patterns

Among developers with at least 10 reliable games:

| Developer | Reliable games | Median rating | High-rated share |
|---|---:|---:|---:|
| Sports Interactive | 14 | 83.76 | 85.7% |
| Ryu Ga Gotoku Studios | 10 | 83.09 | 80.0% |
| Obsidian Entertainment | 10 | 81.84 | 70.0% |
| Spike Chunsoft | 12 | 81.12 | 58.3% |
| Nintendo | 12 | 81.09 | 58.3% |
| The Creative Assembly | 10 | 81.03 | 70.0% |

Sports Interactive also had 10 candidates among 12 eligible quality games.
This primarily reflects highly rated Football Manager titles with relatively
low PopScore compared with other quality games from the same years.

### 11.2 Publisher descriptive patterns

Among publishers with at least 10 reliable games:

| Publisher | Reliable games | Median rating | High-rated share |
|---|---:|---:|---:|
| Take-Two Interactive | 13 | 83.88 | 53.8% |
| Sony Interactive Entertainment | 37 | 83.50 | 64.9% |
| Xbox Game Studios | 18 | 83.27 | 55.6% |
| Sega Games | 17 | 83.15 | 76.5% |
| Spike Chunsoft | 19 | 82.14 | 68.4% |
| NIS America | 15 | 82.14 | 60.0% |

Nintendo had the largest reliable sample among these notable publishers:

- 140 reliable games.
- Median rating of 79.34.
- 46.4% high-rated share.
- 15 low-visibility candidates.

### 11.3 Company enrichment models

| Company type | Tests | Successful models | FDR-significant models |
|---|---:|---:|---:|
| Developer | 33 | 17 | 13 |
| Publisher | 89 | 60 | 44 |

Some company odds ratios were extremely large. For example, Ubisoft Montreal
had an estimated odds ratio above 100, but its confidence interval ranged from
approximately 16 to 896. Such estimates indicate sparse cohort cells and
should not be used as company rankings.

---

## 12. Metadata Findings

### 12.1 Metadata was more strongly associated with visibility than quality

| Metadata component | Spearman with PopScore | Spearman with total rating |
|---|---:|---:|
| External-link count | 0.627 | 0.104 |
| Text completeness | 0.298 | 0.150 |
| Has storyline | 0.295 | 0.150 |
| Distribution count | 0.291 | -0.002 |
| Storyline length | 0.277 | 0.140 |
| Media count | 0.267 | 0.080 |
| Company coverage | 0.235 | 0.029 |
| Classification count | 0.217 | 0.108 |
| Summary length | 0.048 | 0.001 |

The strongest result was the relationship between external links and
visibility. Games connected to more websites and external sources were much
more likely to have high PopScore.

In contrast:

- Distribution count was unrelated to rating quality.
- Company coverage had no meaningful rating relationship.
- Summary length was essentially unrelated to rating.
- Even statistically significant rating relationships were generally weak.

### 12.2 Interpretation

Metadata should be interpreted as a mixture of:

- Documentation effort.
- Commercial reach.
- Community attention.
- Platform availability.
- Age and historical prominence.

It should not be converted into a single game-quality score.

### 12.3 Metadata volume bands

Very-high-volume quality games had:

- Median rating of 80.71.
- Median rating count of 96.5.
- Median PopScore percentile of 0.805.

The visibility difference across metadata bands was much stronger than the
rating difference. The moderate and low bands also contain very few reliable
quality games, making direct band comparisons unstable.

---

## 13. Gameplay Mode and Player Perspective Findings

### 13.1 Game modes

| Game mode | Reliable games | Median rating | High-rated share | Candidate share |
|---|---:|---:|---:|---:|
| Split screen | 186 | 76.60 | 28.0% | 17.1% |
| Single player | 2,376 | 76.42 | 31.5% | 16.6% |
| Multiplayer | 1,195 | 75.39 | 27.4% | 15.3% |
| Co-operative | 817 | 75.09 | 25.8% | 12.9% |
| MMO | 112 | 71.29 | 17.0% | 17.5% |
| Battle Royale | 33 | 70.21 | 21.2% | 18.2% |

Single-player and split-screen games had somewhat higher median ratings than
multiplayer, co-operative, MMO, and Battle Royale games. These categories
overlap, so the table does not represent mutually exclusive game groups.

### 13.2 Player perspectives

| Perspective | Reliable games | Median rating | High-rated share | Candidate share |
|---|---:|---:|---:|---:|
| Text | 100 | 78.40 | 41.0% | 27.0% |
| Side view | 565 | 77.35 | 33.8% | 20.2% |
| Bird view / Isometric | 574 | 76.96 | 35.2% | 20.6% |
| Virtual Reality | 85 | 76.63 | 34.1% | 22.4% |
| First person | 634 | 75.75 | 28.7% | 12.7% |
| Third person | 1,026 | 75.54 | 30.0% | 10.8% |

The Auditory perspective had a median of 78.86 and a 60.0% candidate share,
but it contained only 16 reliable games and is too small for a stable
conclusion.

---

## 14. Multiplayer Support Findings

Detailed multiplayer records existed for only **1,836 games**, or **12.2%** of
the complete sample. The remaining 87.8% are unknown, not confirmed
single-player or non-cooperative games.

Within games that had multiplayer records:

| Feature | Median rating: yes | Median rating: recorded no | Candidate share: yes | Candidate share: recorded no |
|---|---:|---:|---:|---:|
| Campaign co-op | 75.28 | 75.73 | 6.1% | 13.1% |
| Online co-op | 74.95 | 76.63 | 7.6% | 13.8% |
| Offline co-op | 75.90 | 75.28 | 13.5% | 8.9% |
| Split screen | 75.75 | 75.61 | 11.4% | 10.5% |

The differences are small and should remain descriptive. Coverage is too low
to generalize them to the full sample.

---

## 15. Playtime Findings

Normal-completion playtime was available for only **1,961 games**, or **13.1%**
of the sample. Missing playtime is therefore a major limitation.

Within the quality cohort:

| Playtime band | Reliable games | Median rating | High-rated share | Candidate share |
|---|---:|---:|---:|---:|
| Very short: 0–5 hours | 134 | 79.39 | 41.8% | 20.5% |
| Short: 5–15 hours | 318 | 80.58 | 54.7% | 12.8% |
| Medium: 15–30 hours | 185 | 81.74 | 63.2% | 7.7% |
| Long: 30–60 hours | 150 | 81.92 | 68.7% | 6.7% |
| Very long: 60+ hours | 118 | 82.69 | 71.2% | 9.4% |
| Unknown | 513 | 79.55 | 47.0% | 26.9% |

Among games with known playtime, longer quality-cohort games tended to have
higher ratings and greater visibility. However:

- The data are observational.
- Long games may be concentrated in particular genres.
- Open-ended and live-service games can produce extreme values.
- Missing playtime is not random.

No causal conclusion should be drawn from the apparent length gradient.

---

## 16. Popularity Primitive Findings

Popularity primitives were analyzed separately by source and type. Their
values were not averaged across incompatible signals.

### 16.1 Relationship with rating activity

The strongest correlations with total rating count were:

| Popularity primitive | Source | Spearman correlation |
|---|---|---:|
| Played | IGDB | 0.955 |
| Positive Reviews | Steam | 0.823 |
| Total Reviews | Steam | 0.821 |
| Negative Reviews | Steam | 0.757 |
| Want to Play | IGDB | 0.735 |
| 24-hour Peak Players | Steam | 0.692 |
| Playing | IGDB | 0.645 |
| Visits | IGDB | 0.505 |
| 24-hour Hours Watched | Twitch | 0.418 |

These results confirm that rating count behaves as an audience-activity
measure. Review totals, played counts, wish-list interest, player peaks, and
rating activity all tend to grow with audience exposure.

### 16.2 Relationship with rating quality

Relationships with total rating were weaker:

| Popularity primitive | Spearman with total rating |
|---|---:|
| Steam Positive Reviews | 0.460 |
| Steam Total Reviews | 0.428 |
| Steam 24-hour Peak Players | 0.428 |
| IGDB Played | 0.381 |
| IGDB Want to Play | 0.369 |
| IGDB Playing | 0.315 |
| Steam Negative Reviews | 0.255 |
| Twitch Hours Watched | 0.232 |
| IGDB Visits | 0.223 |
| Steam Global Top Sellers | 0.129 |

Popularity and quality overlap, but popularity signals cannot replace ratings.

The Steam Most Wishlisted Upcoming category had only three complete
observations for correlation analysis and was correctly marked as an
insufficient sample.

---

## 17. Statistical Testing Summary

| Category family | Tests attempted | Successful models | Significant after FDR correction |
|---|---:|---:|---:|
| Genres | 21 | 21 | 18 |
| Themes | 22 | 22 | 22 |
| Genre-theme combinations | 213 | 212 | 176 |
| Developers | 33 | 17 | 13 |
| Publishers | 89 | 60 | 44 |
| **Total** | **378** | **332** | **273** |

Benjamini-Hochberg correction was used to reduce false discoveries across each
family of tests.

The large number of significant results is partly a consequence of:

- The deliberate quality-cohort construction.
- The residual nature of the comparison cohort.
- Large sample sizes for broad genres and themes.
- Correlated category memberships.

Statistical significance should therefore be evaluated together with:

- Odds-ratio magnitude.
- Confidence-interval width.
- Category sample size.
- Whether the category has sufficient observations in both cohorts.

---

## 18. Cross-Cutting Conclusions

### 18.1 Quality is not the same as visibility

The central diagnostic conclusion is that highly rated games are somewhat
more visible, but the relationship is only moderate. A useful game-discovery
system must retain separate measures for:

- Rating quality.
- Rating confidence/activity.
- Current visibility.

### 18.2 The best discovery opportunity lies within reliable quality games

The 229 balanced candidates demonstrate that strong reception can coexist with
relatively low current interest. Music, Sport, Arcade, Visual Novel, Platform,
Indie, Puzzle, and Simulator games contained notable candidate shares.

### 18.3 Metadata primarily reflects exposure and documentation

External links, storyline availability, media, and relationship coverage were
much more strongly connected to PopScore visibility than rating quality.
Metadata abundance should not be interpreted as evidence that a game is good.

### 18.4 Audience groups do not evaluate every game identically

User and critic scores were strongly related but had important outliers. The
combined rating is useful for a broad reception summary, but it hides audience
disagreement.

### 18.5 Category enrichment is not category causation

Genre, theme, genre-theme, developer, and publisher enrichment results are
strongly shaped by the curated extraction. They are useful for understanding
the project's sample composition but do not establish that a category or
company produces higher-quality games.

---

## 19. Limitations

1. **Curated sample**
   - The analysis does not represent all IGDB games or the overall game
     market.

2. **Cohort-dependent inclusion**
   - Quality and visibility cases were deliberately oversampled.

3. **Residual comparison cohort**
   - The comparison cohort excludes games already selected into quality and
     popularity cohorts.

4. **Unequal data coverage**
   - Reliable-rating and PopScore coverage differ sharply by cohort.

5. **Missing PopScore**
   - Missing visibility is unknown, not low.

6. **Overlapping categories**
   - Games can have multiple genres, themes, platforms, companies, modes, and
     perspectives.

7. **Sparse company estimates**
   - Many developer and publisher results are based on small samples or
     limited comparison-cohort variation.

8. **Sparse multiplayer and playtime data**
   - Multiplayer details cover 12.2% of games.
   - Normal playtime covers 13.1% of games.

9. **Observational relationships**
   - The analysis identifies associations and cannot determine causality.

10. **Multiple comparisons**
    - False-discovery-rate correction reduces but does not eliminate the risk
      of misleading category findings.

---

## 20. Final Diagnostic Answer

The diagnostic pillar answers the project question as follows:

> Games appear more highly rated, more visible, or more discoverable for
> different reasons. Rating quality is moderately associated with visibility
> and audience activity, but neither signal fully explains the other.
> Platform reach, external links, and metadata coverage are especially
> associated with visibility. Genres, themes, genre-theme combinations, and
> companies show strong cohort-enrichment patterns, although these patterns
> are heavily influenced by the curated extraction. User and critic ratings
> generally agree but retain meaningful disagreement. Most importantly, 229
> reliable quality-cohort games combine strong ratings with relatively low
> within-year IGDB interest, creating an auditable set of discovery
> candidates.

The completed diagnostic outputs support a clear project narrative:

```text
Quality identifies well-received games.
Rating count identifies evidence and audience activity.
PopScore identifies current visibility.
The gap between quality and visibility identifies discovery opportunity.
```
