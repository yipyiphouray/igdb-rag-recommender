from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


ROOT_DIR = Path(__file__).resolve().parent.parent
TRAIN_CSV = ROOT_DIR / "data" / "analytics" / "modeling_train_features.csv"
TEST_CSV = ROOT_DIR / "data" / "analytics" / "modeling_test_features.csv"
PLOTS_DIR = ROOT_DIR / "data" / "analytics" / "plots"
MODEL_PATH = ROOT_DIR / "models" / "recommender_model.pkl"
TARGET_COL = "total_rating"
RELEASE_YEAR_COL = "release_year"

# Explicitly exclude ID/text columns from modeling.
EXCLUDED_COLUMNS = {
    "game_id",
    "name",
    "slug",
    "first_release_date_iso",
    "category_decoded",
    "status_decoded",
    "rating_confidence",
    "playtime_length",
    "genres",
    "themes",
    "platforms",
    "developers",
    "publishers",
}


def ensure_directories() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = pd.read_csv(TRAIN_CSV)
    test_df = pd.read_csv(TEST_CSV)
    return train_df, test_df


def validate_required_columns(train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    missing = []
    for required_col in [TARGET_COL, RELEASE_YEAR_COL]:
        if required_col not in train_df.columns:
            missing.append(f"train:{required_col}")
        if required_col not in test_df.columns:
            missing.append(f"test:{required_col}")

    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(
            f"Missing required column(s): {missing_str}. "
            "Regenerate modeling CSVs with both release_year and total_rating included."
        )


def impute_target_with_release_year_average(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = train_df.copy()
    test_df = test_df.copy()

    train_df[TARGET_COL] = pd.to_numeric(train_df[TARGET_COL], errors="coerce")
    test_df[TARGET_COL] = pd.to_numeric(test_df[TARGET_COL], errors="coerce")
    train_df[RELEASE_YEAR_COL] = pd.to_numeric(train_df[RELEASE_YEAR_COL], errors="coerce")
    test_df[RELEASE_YEAR_COL] = pd.to_numeric(test_df[RELEASE_YEAR_COL], errors="coerce")

    year_means = train_df.groupby(RELEASE_YEAR_COL)[TARGET_COL].mean()
    global_mean = train_df[TARGET_COL].mean()

    if pd.isna(global_mean):
        global_mean = 0.0

    train_df[TARGET_COL] = (
        train_df[TARGET_COL]
        .fillna(train_df[RELEASE_YEAR_COL].map(year_means))
        .fillna(global_mean)
    )

    test_df[TARGET_COL] = (
        test_df[TARGET_COL]
        .fillna(test_df[RELEASE_YEAR_COL].map(year_means))
        .fillna(global_mean)
    )

    return train_df, test_df


def create_eda_plots(train_df: pd.DataFrame) -> None:
    numeric_df = train_df.select_dtypes(include=["number"]).fillna(0)

    plt.figure(figsize=(14, 10))
    corr = numeric_df.corr()
    sns.heatmap(corr, cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap (Numeric Features)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "correlation_heatmap.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(train_df[TARGET_COL], bins=30, kde=True)
    plt.title("Distribution of total_rating")
    plt.xlabel("total_rating")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "total_rating_distribution.png", dpi=300)
    plt.close()


def identify_numeric_and_binary_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    feature_numeric_cols = [
        col
        for col in numeric_cols
        if col != TARGET_COL and col not in EXCLUDED_COLUMNS
    ]

    binary_cols = [
        col
        for col in feature_numeric_cols
        if set(df[col].dropna().unique()).issubset({0, 1})
    ]
    return feature_numeric_cols, binary_cols


def prepare_xy(df: pd.DataFrame, feature_cols: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    x = df[feature_cols].fillna(0)
    y = df[TARGET_COL]
    return x, y


def train_model(x_train: pd.DataFrame, y_train: pd.Series) -> RandomForestRegressor:
    model = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def evaluate_model(
    model: RandomForestRegressor,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[dict[str, float], pd.Series]:
    preds = pd.Series(model.predict(x_test), index=y_test.index)
    metrics = {
        "mae": mean_absolute_error(y_test, preds),
        "r2": r2_score(y_test, preds),
    }
    return metrics, preds


def save_feature_importance_plot(model: RandomForestRegressor, feature_cols: list[str]) -> None:
    importance_df = pd.DataFrame(
        {
            "feature": feature_cols,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    top_n = min(20, len(importance_df))
    top_importance = importance_df.head(top_n)

    plt.figure(figsize=(10, 7))
    sns.barplot(data=top_importance, x="importance", y="feature")
    plt.title("Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "feature_importance.png", dpi=300)
    plt.close()


def save_predicted_vs_actual_plot(y_test: pd.Series, preds: pd.Series) -> None:
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_test, y=preds, alpha=0.6)

    min_val = min(y_test.min(), preds.min())
    max_val = max(y_test.max(), preds.max())
    plt.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--")

    plt.title("Predicted vs Actual total_rating")
    plt.xlabel("Actual total_rating")
    plt.ylabel("Predicted total_rating")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "predicted_vs_actual.png", dpi=300)
    plt.close()


def save_model(model: RandomForestRegressor, feature_cols: list[str]) -> None:
    artifact = {
        "model": model,
        "feature_columns": feature_cols,
        "target_column": TARGET_COL,
    }
    joblib.dump(artifact, MODEL_PATH)

from scipy.stats import spearmanr

def evaluate_ranking_performance(model, x_test, y_test):
    preds = model.predict(x_test)
    corr, _ = spearmanr(y_test, preds)
    print(f"-> Spearman Rank Correlation: {corr:.4f}")
    return corr

def main() -> None:
    ensure_directories()

    train_df, test_df = load_data()
    validate_required_columns(train_df, test_df)
    train_df, test_df = impute_target_with_release_year_average(train_df, test_df)

    create_eda_plots(train_df)

    feature_cols, binary_cols = identify_numeric_and_binary_columns(train_df)

    x_train, y_train = prepare_xy(train_df, feature_cols)
    x_test, y_test = prepare_xy(test_df, feature_cols)

    model = train_model(x_train, y_train)
    metrics, preds = evaluate_model(model, x_test, y_test)

    rank_corr = evaluate_ranking_performance(model, x_test, y_test)

    save_model(model, feature_cols)
    save_feature_importance_plot(model, feature_cols)
    save_predicted_vs_actual_plot(y_test, preds)

    print("Regression training complete.")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Plots saved to: {PLOTS_DIR}")
    print(f"Numeric feature count: {len(feature_cols)}")
    print(f"Binary feature count: {len(binary_cols)}")
    print("Evaluation on test set:")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  R^2: {metrics['r2']:.4f}")


if __name__ == "__main__":
    main()
