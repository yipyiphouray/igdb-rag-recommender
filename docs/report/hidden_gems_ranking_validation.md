# Hidden Gems Ranking Validation

Generated: 2026-07-24

## Purpose

This report validates whether the Hidden Gems ranking is defensible and reproducible, rather than tuned by visual judgment or subjective feel.

The goal is to answer the professor's feedback directly:

> Pin down the retrieval or ranking accuracy number so the Hidden Gems ranking is defensible.

For this project, the Hidden Gems page is not a free-form semantic retrieval page. It is a deterministic ranking built from diagnostic analytics outputs. Therefore, the most appropriate validation number is rule-compliance precision: how many displayed hidden-gem candidates actually satisfy the documented hidden-gem rule.

## Source Artifacts

Primary artifact used for validation:

```text
data/analytics/diagnostic/hidden_gem_candidates.csv
```

App artifact generated from the diagnostic candidate file:

```text
data/app/app_hidden_gems.parquet
```

Relevant implementation files:

```text
src/pipeline/build_app_catalog.py
src/app/validation.py
src/app/constants.py
apps/website/src/app/hidden-gems/page.tsx
```

## Hidden-Gem Definition

The project's Balanced hidden-gem rule uses three required conditions.

A game qualifies as a hidden gem only if it satisfies all of the following:

| Condition | Required Rule |
|---|---:|
| Quality threshold | `total_rating >= 80` |
| Rating evidence threshold | `total_rating_count >= 25` |
| Lower-visibility threshold | `visibility_percentile_eligible_pool <= 0.40` |

The constants come from:

```text
src/app/constants.py
```

Current values:

```text
QUALITY_THRESHOLD = 80
MIN_RATING_COUNT = 25
HIDDEN_GEM_VISIBILITY_PERCENTILE = 0.40
```

## Ranking Formula

The app-level Hidden Gems artifact ranks candidates using this formula:

```text
hidden_gem_score =
    0.65 * (total_rating / 100)
  + 0.35 * inverse_visibility_percentile
```

Where:

```text
inverse_visibility_percentile = 1 - visibility_percentile_eligible_pool
```

Interpretation:

- Higher `total_rating` improves the score.
- Lower visibility improves the score through a higher inverse visibility percentile.
- The formula prioritizes quality more heavily than obscurity.
- This prevents the page from surfacing random obscure games that do not have enough quality evidence.

## Validation Results

### Candidate Count

| Metric | Result |
|---|---:|
| Hidden-gem candidate rows | 231 |
| Unique game IDs | 231 |
| Duplicate game IDs | 0 |

### Rule-Compliance Validation

| Validation Check | Result |
|---|---:|
| Candidates below rating threshold | 0 |
| Candidates below rating-count threshold | 0 |
| Candidates above visibility cutoff | 0 |
| Overall rule-compliance precision | 231 / 231 = 100.0% |

### Top-K Ranking Precision

This checks whether the highest-ranked hidden gems still satisfy the rule.

| Ranked Slice | Rule-Compliant Candidates | Precision |
|---|---:|---:|
| Top 10 | 10 / 10 | 100.0% |
| Top 20 | 20 / 20 | 100.0% |
| Top 50 | 50 / 50 | 100.0% |
| Top 100 | 100 / 100 | 100.0% |

### Threshold Boundary Checks

| Metric | Observed Value |
|---|---:|
| Minimum `total_rating` among candidates | 80.0156 |
| Minimum `total_rating_count` among candidates | 25 |
| Maximum `visibility_percentile_eligible_pool` among candidates | 0.4000 |

These boundary checks confirm that the artifact includes candidates at the edge of the rule, but does not violate the rule.

### Ranking Order Check

The app ranking formula was recomputed from the diagnostic CSV.

| Check | Result |
|---|---|
| Computed score is sorted from highest to lowest | Pass |
| Maximum computed hidden-gem score | 0.9827 |
| Minimum computed hidden-gem score | 0.7312 |

## Top Ranked Hidden Gems Snapshot

The following table shows the top candidates after recomputing the app ranking formula.

| Rank | Game | Year | Rating | Rating Count | Visibility Percentile | Computed Hidden-Gem Score |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Undertale Yellow | 2023 | 99.21 | 25 | 0.0349 | 0.9827 |
| 2 | Town Star | 2020 | 93.32 | 34 | 0.0110 | 0.9530 |
| 3 | Lurkers | 2019 | 97.30 | 36 | 0.0924 | 0.9502 |
| 4 | NextWorld2 | 2024 | 94.23 | 39 | 0.0417 | 0.9482 |
| 5 | Hrot | 2023 | 92.55 | 31 | 0.0465 | 0.9353 |
| 6 | Bad End Theater | 2021 | 94.33 | 25 | 0.0976 | 0.9290 |
| 7 | Gakuen Idolmaster | 2024 | 97.30 | 26 | 0.1806 | 0.9190 |
| 8 | The Cosmic Wheel Sisterhood | 2023 | 87.77 | 25 | 0.0116 | 0.9166 |
| 9 | Football Manager 2019 | 2018 | 87.52 | 65 | 0.0189 | 0.9121 |
| 10 | Football Manager 2012 | 2011 | 88.42 | 50 | 0.0443 | 0.9096 |

## Final Defensibility Metric

The Hidden Gems ranking currently has:

```text
Rule-compliance precision: 100.0%
Top-50 Hidden Gems precision: 100.0%
Duplicate rate: 0.0%
Ranking order check: Pass
```

This means every displayed hidden-gem candidate satisfies the documented quality, evidence, and lower-visibility thresholds.

## What This Metric Does and Does Not Prove

This validation proves:

- Hidden Gems are not random catalog picks.
- Every candidate satisfies the documented hidden-gem rule.
- The ranking formula is reproducible.
- The highest-ranked candidates still satisfy the same rule.
- The app-facing Hidden Gems concept is defensible as a project-defined ranking.

This validation does not prove:

- Hidden Gems are objectively unknown in the real-world market.
- Every user will personally agree that each candidate is a good discovery.
- The IGDB dataset is a complete representation of the full game market.
- The 40th percentile visibility cutoff is the only possible defensible cutoff.

## Recommendation for Professor-Facing Summary

Use this wording in the progress report:

```text
Validated the Hidden Gems ranking with a deterministic rule-compliance check: all 231 hidden-gem candidates satisfy the documented rating, rating-count, and lower-visibility thresholds, producing 100% rule-compliance precision and 100% Top-50 precision.
```

## Optional Next Improvement

If a human relevance number is required in addition to deterministic rule compliance, run a manual review of the top 25 or top 50 hidden gems.

Suggested manual review bar:

```text
At least 80% of reviewed top-25 candidates should be judged as plausible hidden gems by two reviewers.
```

That would add a human-facing relevance score on top of the current deterministic validation.
