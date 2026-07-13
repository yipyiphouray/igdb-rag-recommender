# Diagnostic Analytics Pillar Findings

## IGDB Game Discovery Project

**Pillar:** Diagnostic Analytics  
**Dataset:** Refreshed curated IGDB analytical sample  
**Current game count:** 47,835 games  
**Release years:** 2010-2024  
**Primary notebook:** [`02_diagnostic_analytics_exploration.ipynb`](../../notebooks/02_diagnostic_analytics_exploration.ipynb)  
**Analysis plan:** [`diagnostic_analytics_pillar_plan.md`](../plan/diagnostic_analytics_pillar_plan.md)  
**Diagnostic outputs:** [`data/analytics/diagnostic/`](../../data/analytics/diagnostic/)

---

## 1. Notebook Review Status

The refreshed diagnostic notebook was updated and rerun after the 47,835-game extraction.

The earlier notebook validation still expected the old 15,000-game / 1,000-games-per-year sample. That check was updated to validate the current extraction design:

- 15 release years are present.
- all selected games have extraction cohort rows;
- SQLite integrity passes;
- foreign-key checks pass;
- diagnostic exports are generated from the refreshed database.

The refreshed diagnostic exports now show:

- `diagnostic_game_base`: 47,835 rows;
- `diagnostic_rating_reliable_base`: 2,639 rows;
- `hidden_gem_candidates`: 231 rows;
- `cohort_adjusted_association_summary`: 684 rows;
- `diagnostic_takeaways`: 5 rows.

---

## 2. Executive Summary

The diagnostic analytics pillar examines why some games appear stronger, more visible, more documented, or more discoverable than others within the curated IGDB sample.

The main findings are:

1. **Rating quality, rating activity, and PopScore visibility are related but distinct.**
   - Total rating versus PopScore visibility has Spearman rho = 0.357.
   - Total rating versus total rating count has Spearman rho = 0.319.
   - These are positive but moderate relationships, so quality, activity, and visibility should remain separate signals.

2. **The project identified 231 low-visibility, high-quality candidates.**
   - These are quality-cohort games with total rating >= 80 and total rating count >= 25.
   - They also have known PopScore visibility and fall at or below the within-year 40th visibility percentile among eligible quality-cohort games.
   - They are auditable discovery candidates, not market-wide hidden-gem estimates.

3. **User and critic ratings generally agree but are not identical.**
   - User-versus-critic Spearman correlation is 0.701.
   - The median user-minus-critic gap is -3.04 points.
   - This suggests critics rate the typical overlapping game slightly higher than users.

4. **Platform reach is associated with visibility.**
   - Platform count versus PopScore percentile has Spearman rho = 0.386.
   - Wider platform availability tends to align with higher known visibility, but the analysis is observational and does not prove causation.

5. **Metadata coverage is more strongly related to visibility than to rating quality.**
   - External-link count has Spearman rho = 0.635 with PopScore percentile.
   - External-link count has only rho = 0.146 with total rating.
   - Metadata volume appears to reflect documentation, discoverability, and commercial footprint more than inherent quality.

6. **Category enrichment patterns are strong but must be interpreted carefully.**
   - 334 category enrichment tests are significant after Benjamini-Hochberg correction.
   - These tests compare the quality cohort against the residual comparison cohort while controlling for release year.
   - They show extraction-cohort enrichment, not causal effects.

---

## 3. Sample and Cohort Interpretation Rules

The diagnostic dataset is curated and cohort-based. It should not be interpreted as a random sample of the full IGDB catalog.

| Cohort | Games | Share | Diagnostic meaning |
|---|---:|---:|---|
| Quality | 1,425 | 2.98% | Stronger reliable reception |
| Lower-rated | 147 | 0.31% | Lower reliable reception |
| Popularity | 9,000 | 18.81% | High known visibility |
| Low visibility | 5,329 | 11.14% | Low known visibility |
| Comparison | 31,934 | 66.76% | Residual comparison group |
| **Total** | **47,835** | **100.00%** | **Current diagnostic base** |

Interpretation rules:

- `total_rating` is the project’s main reception-quality proxy.
- `total_rating_count` is rating evidence and audience-rating activity.
- PopScore is the project’s visibility proxy.
- Reliable rating means `total_rating_count >= 25`.
- Missing PopScore means unknown visibility, not low visibility.
- The comparison cohort is residual because quality, lower-rated, popularity, and low-visibility selections are removed before comparison sampling.
- Associations are not causal explanations.

---

## 4. Diagnostic Dataset Health

| Metric | Value | Status |
|---|---:|---|
| SQLite integrity | ok | Pass |
| Foreign-key failures | 0 | Pass |
| Total games | 47,835 | Informational |
| Games with total rating | 14,009 | Informational |
| Games with total rating count | 14,009 | Informational |
| Reliable-rated games | 2,639 | Informational |
| High-rated reliable games | 775 | Informational |
| Release years | 15 | Pass |
| Years with selected games | 15 | Pass |
| Games missing extraction cohort | 0 | Pass |
| PopScore-covered games | 10,056 | Informational |

The diagnostic base is usable. The key limitation is not data integrity; it is analytical coverage. Ratings and PopScore are not available for every selected game, so each diagnostic question uses the subset of games that has the required fields.

---

## 5. Quality, Visibility, and Rating Activity

### Quality versus visibility

| Scope | Method | N | Correlation |
|---|---|---:|---:|
| Overall | Spearman | 2,504 | 0.357 |
| Overall | Pearson | 2,504 | 0.298 |
| Quality cohort | Spearman | 1,370 | 0.302 |
| Popularity cohort | Spearman | 1,009 | 0.175 |
| Lower-rated cohort | Spearman | 125 | 0.018 |

The overall positive relationship means stronger-rated games tend to have somewhat higher visibility. However, the relationship is not strong enough to treat visibility as a substitute for quality.

### Quality versus rating activity

| Scope | Method | N | Correlation |
|---|---|---:|---:|
| Overall | Spearman | 2,639 | 0.319 |
| Overall | Pearson | 2,639 | 0.299 |
| Quality cohort | Spearman | 1,425 | 0.257 |
| Popularity cohort | Spearman | 1,046 | 0.167 |
| Lower-rated cohort | Spearman | 147 | 0.097 |

Rating count provides evidence and confidence, but it is not the same as quality. High rating activity can reflect awareness, platform reach, fandom, controversy, or age.

---

## 6. Hidden-Gem Candidate Findings

The refreshed diagnostic notebook identified 231 hidden-gem candidates under the balanced project definition.

Definition used:

- game is in the quality cohort;
- game is a main-game record;
- `total_rating >= 80`;
- `total_rating_count >= 25`;
- PopScore visibility is known;
- within-year visibility percentile among eligible quality games is <= 40%.

The hidden-gem count by year is:

| Release year | Eligible quality games | Hidden-gem candidates |
|---:|---:|---:|
| 2010 | 75 | 13 |
| 2011 | 79 | 12 |
| 2012 | 88 | 11 |
| 2013 | 90 | 11 |
| 2014 | 81 | 11 |
| 2015 | 97 | 14 |
| 2016 | 113 | 17 |
| 2017 | 105 | 16 |
| 2018 | 106 | 18 |
| 2019 | 119 | 22 |
| 2020 | 91 | 19 |
| 2021 | 82 | 18 |
| 2022 | 86 | 17 |
| 2023 | 86 | 17 |
| 2024 | 72 | 15 |

Example candidates from the exported list include:

- `Town Star`;
- `Undertale Yellow`;
- `Lurkers`;
- `Bad End Theater`;
- `Gakuen Idolmaster`;
- `Faith`;
- `Animal Company`;
- `Cataclysm: Dark Days Ahead`;
- `Football Manager 2013`;
- `Transport Fever`.

These candidates are useful for the app and report because they can support a clear story: some games have strong reliable reception but relatively low known IGDB visibility for their year.

---

## 7. User and Critic Rating Agreement

| Metric | N | Value |
|---|---:|---:|
| User/critic Pearson correlation | 1,329 | 0.703 |
| User/critic Spearman correlation | 1,329 | 0.701 |
| Median user-minus-critic gap | 1,329 | -3.04 |
| User/critic gap IQR | 1,329 | 7.79 |

The user and critic ratings are strongly related, but not interchangeable. The median gap is negative, meaning the typical overlapping game has a slightly lower user rating than critic rating. The app and future website should preserve user, critic, and combined ratings as separate fields when possible.

---

## 8. Platform Reach and Visibility

The platform-reach analysis supports the idea that wider availability is associated with visibility.

The key diagnostic takeaway is:

- platform count versus PopScore percentile Spearman rho = 0.386.

Median PopScore percentile rises across platform reach bands, especially inside the popularity and quality cohorts. However, platform reach should not be treated as a direct cause of popularity. It may also reflect marketing investment, franchise strength, publisher resources, or post-launch porting strategy.

---

## 9. Metadata Volume and Visibility

Metadata relationships are stronger for visibility than for rating quality.

Top metadata-to-visibility relationships:

| Metadata component | Scope | Spearman with PopScore percentile |
|---|---|---:|
| External-link count | All games | 0.635 |
| External-link count | Quality cohort | 0.584 |
| External-link count | Popularity cohort | 0.534 |
| External-link count | Lower-rated cohort | 0.470 |
| Classification count | All games | 0.419 |
| Distribution count | All games | 0.418 |
| Company coverage count | All games | 0.376 |
| Text completeness score | Quality cohort | 0.398 |
| Storyline length | Quality cohort | 0.364 |

The strongest relationship is external-link count versus PopScore visibility. This makes sense because games with more store, site, and external catalog links are easier to discover and are often better documented.

The metadata-to-rating relationships are much weaker. This means metadata richness should be interpreted as profile/documentation richness, not objective quality.

---

## 10. Category Enrichment Findings

The cohort-adjusted category models compare quality-cohort membership against residual comparison-cohort membership while controlling for release year.

Top significant enrichment patterns include:

| Category type | Category | Odds ratio | Interpretation |
|---|---|---:|---|
| Genre-theme | Adventure + Fantasy | 9.32 | Strongly enriched in the quality cohort |
| Theme | Open world | 17.03 | Strongly enriched in the quality cohort |
| Genre-theme | Adventure + Science fiction | 11.26 | Strongly enriched in the quality cohort |
| Genre-theme | Adventure + Open world | 24.81 | Strongly enriched in the quality cohort |
| Theme | Fantasy | 5.67 | Enriched in the quality cohort |
| Genre-theme | Adventure + Action | 5.34 | Enriched in the quality cohort |
| Theme | Science fiction | 5.77 | Enriched in the quality cohort |
| Genre-theme | RPG + Fantasy | 6.79 | Enriched in the quality cohort |
| Genre-theme | RPG + Action | 5.12 | Enriched in the quality cohort |
| Genre | Adventure | 3.48 | Enriched in the quality cohort |
| Publisher | Nintendo | 34.19 | Strongly enriched in the quality cohort |
| Theme | Action | 3.41 | Enriched in the quality cohort |
| Theme | Stealth | 15.20 | Strongly enriched in the quality cohort |
| Theme | Sandbox | 9.58 | Enriched in the quality cohort |

These patterns are useful diagnostically, but they are not causal. They show which categories are overrepresented in the quality cohort under this extraction design.

---

## 11. Diagnostic Interpretation

The diagnostic pillar is complete enough to move forward, with one important caveat: findings must be framed as associations within the curated project sample.

The refreshed diagnostic analysis is stronger than the previous version because:

- it uses a much larger analytical base;
- it includes lower-rated and low-visibility contrast cohorts;
- it validates that all games have cohort assignments;
- it keeps quality, rating activity, and visibility separate;
- it produces an auditable hidden-gem candidate list;
- it produces category-enrichment outputs that can support storytelling in the app and final website.

The main limitations are:

- rating coverage remains limited;
- reliable rating coverage is only 5.52% of the full sample;
- PopScore coverage is 21.02%;
- low-visibility means low known visibility, not missing visibility;
- comparison-cohort findings are shaped by the extraction design.

---

## 12. Recommended Report Wording

Use this wording when presenting the diagnostic pillar:

> The diagnostic pillar uses a refreshed curated sample of 47,835 released main games from 2010 through 2024. The analysis separates game reception, rating activity, and visibility rather than treating them as one score. The strongest diagnostic findings are that quality and visibility are moderately related, platform reach is associated with visibility, metadata richness is more strongly tied to visibility than to rating quality, and 231 games qualify as low-visibility, high-quality discovery candidates under the project definition. All results are associations within the curated IGDB sample, not causal claims or full-market estimates.
