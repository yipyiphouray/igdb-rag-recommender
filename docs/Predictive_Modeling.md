# Predictive Modeling Methodology

## 1. Overview

The predictive modeling component serves as the "Intelligence Layer" of our recommendation engine. By transitioning from heuristic-based ranking to a machine-learning-driven regression approach, the system is now capable of estimating the relative quality of games based on their intrinsic features rather than simple string matching.

## 2. Regression-Based Quality Estimation

We replaced the previous binary classification approach (`is_high_rated`) with a **RandomForestRegressor**.

* **Target Variable**: The model now predicts the `total_rating` (a continuous value from 0–100).
* **Rationale**: This allows for granular ranking of candidates. Rather than binning games into "good" or "bad," the model assigns a precise quality score, enabling the RAG engine to sort any search result by predicted critical consensus.

## 3. Data Imputation & Temporal Fairness

To address the significant volume of games with missing rating data, we implemented a year-based imputation strategy:

* **Methodology**: Missing `total_rating` values are imputed using the arithmetic mean of ratings within their respective `release_year`.
* **Impact**: This preserves the temporal context of gaming eras, ensuring that games from different decades are evaluated against the relevant quality baselines of their time, preventing unfair penalties for games with sparse data.

## 4. Model Performance & Ranking Efficacy

Our evaluation metrics focus on the model’s ability to rank items accurately:

* **Spearman Rank Correlation (0.6563)**: This is our primary performance indicator. It demonstrates that while the model may not predict an exact score, it effectively preserves the relative quality order (rank) of games, which is the functional requirement for a recommendation list.
* **Mean Absolute Error (MAE): 3.7592**: This indicates that the model's predictions are, on average, within ~3.7 points of the actual rating on a 100-point scale.
* **$R^2$ (0.3137)**: Reflects that ~31% of the rating variance is explained by our feature set. This confirms that game quality is driven by a mix of our tracked structural features (genres, platforms, summary length) and external factors (marketing, community sentiment).

## 5. Integration into the RAG Engine

The model is integrated into the recommendation pipeline as follows:

1. **Semantic Retrieval**: The vector database filters the 15,000-game dataset to provide a subset of contextually relevant titles.
2. **Predictive Scoring**: Each candidate is passed through the `recommender_model.pkl` to generate a predicted quality score.
3. **Curated Ranking**: Final search results are returned in descending order of the predicted score, ensuring the most likely high-quality, relevant titles are presented to the user first.
