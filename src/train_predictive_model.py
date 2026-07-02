import json
import sqlite3
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


ROOT_DIR = Path(__file__).resolve().parent.parent
TRAIN_CSV = ROOT_DIR / "data" / "analytics" / "modeling_train_features.csv"
TEST_CSV = ROOT_DIR / "data" / "analytics" / "modeling_test_features.csv"
GAME_TIME_TO_BEATS_JSON = ROOT_DIR / "data" / "raw" / "game_time_to_beats.json"
DB_PATH = ROOT_DIR / "data" / "database" / "igdb_games.db"
PLOTS_DIR = ROOT_DIR / "data" / "analytics" / "plots"
MODEL_PATH = ROOT_DIR / "models" / "recommender_model.pkl"

TARGET_COL = "rpi"
RELEASE_YEAR_COL = "release_year"
GAME_ID_COL = "game_id"
USER_ID_COL = "user_id"
TIME_PLAYED_COL = "time_played"
PLAYTIME_NORMALLY_COL = "playtime_normally"
USER_PACE_SIGNATURE_COL = "user_pace_signature"
USER_PACE_PROFILE_COL = "user_pace_profile"

# Explicitly exclude ID/text columns from modeling.
EXCLUDED_COLUMNS = {
    GAME_ID_COL,
    USER_ID_COL,
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
    # Global quality is ranked separately at inference time.
    "total_rating",
    "is_high_rated",
    TIME_PLAYED_COL,
    USER_PACE_PROFILE_COL,
}


def get_alpha(games_played):
    if games_played < 3:
        return 0.1
    elif games_played <= 10:
        return 0.4
    else:
        return 0.75


def ensure_directories() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


def classify_user_pace_signature(signature_value: float) -> str:
    if signature_value > 1.2:
        return "Deep/Extended"
    if signature_value < 0.8:
        return "Snackable/Fast"
    return "Balanced"


def load_game_feature_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = pd.read_csv(TRAIN_CSV)
    test_df = pd.read_csv(TEST_CSV)
    for frame_name, frame in [("train", train_df), ("test", test_df)]:
        if GAME_ID_COL not in frame.columns:
            raise ValueError(f"Missing `{GAME_ID_COL}` in {frame_name} feature CSV.")
    return train_df, test_df


def load_game_time_to_beat_map() -> pd.DataFrame:
    records = json.loads(GAME_TIME_TO_BEATS_JSON.read_text())
    if not isinstance(records, list):
        raise ValueError("Expected game_time_to_beats.json to contain a list of records.")

    rows = []
    for record in records:
        game_id = record.get("game_id")
        normally = record.get("normally")
        if game_id is None or normally is None:
            continue
        rows.append(
            {
                GAME_ID_COL: str(game_id),
                PLAYTIME_NORMALLY_COL: pd.to_numeric(normally, errors="coerce"),
            }
        )

    ttb_df = pd.DataFrame(rows)
    if ttb_df.empty:
        raise ValueError("No valid game_time_to_beats mappings found.")

    ttb_df = (
        ttb_df.dropna(subset=[PLAYTIME_NORMALLY_COL])
        .groupby(GAME_ID_COL, as_index=False)[PLAYTIME_NORMALLY_COL]
        .median()
    )
    return ttb_df


def attach_playtime_normally(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    ttb_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = train_df.copy()
    test_df = test_df.copy()

    train_df[GAME_ID_COL] = train_df[GAME_ID_COL].astype(str)
    test_df[GAME_ID_COL] = test_df[GAME_ID_COL].astype(str)
    ttb_df[GAME_ID_COL] = ttb_df[GAME_ID_COL].astype(str)

    train_df = train_df.merge(ttb_df, on=GAME_ID_COL, how="left")
    test_df = test_df.merge(ttb_df, on=GAME_ID_COL, how="left")

    train_missing = train_df[PLAYTIME_NORMALLY_COL].isna().sum()
    test_missing = test_df[PLAYTIME_NORMALLY_COL].isna().sum()
    train_df["playtime_normally_missing"] = train_df[PLAYTIME_NORMALLY_COL].isna().astype(int)
    test_df["playtime_normally_missing"] = test_df[PLAYTIME_NORMALLY_COL].isna().astype(int)
    combined = pd.concat([train_df[[PLAYTIME_NORMALLY_COL]], test_df[[PLAYTIME_NORMALLY_COL]]], ignore_index=True)
    global_playtime_median = pd.to_numeric(combined[PLAYTIME_NORMALLY_COL], errors="coerce").median()
    if pd.isna(global_playtime_median) or global_playtime_median <= 0:
        global_playtime_median = 36000.0  # 10 hours in seconds fallback

    train_df[PLAYTIME_NORMALLY_COL] = pd.to_numeric(train_df[PLAYTIME_NORMALLY_COL], errors="coerce").fillna(global_playtime_median)
    test_df[PLAYTIME_NORMALLY_COL] = pd.to_numeric(test_df[PLAYTIME_NORMALLY_COL], errors="coerce").fillna(global_playtime_median)

    print(
        "[PaceTrain] Attached playtime_normally from JSON | "
        f"train_missing_before_fill={train_missing} | test_missing_before_fill={test_missing} | "
        f"fill_median_seconds={global_playtime_median:.2f}"
    )
    return train_df, test_df


def load_user_interactions() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_interactions'")
        if cursor.fetchone() is None:
            raise ValueError(
                "Missing required table `user_interactions`. "
                "Create and populate user history before training the pace-compatibility model."
            )

        columns = pd.read_sql_query("PRAGMA table_info(user_interactions)", conn)["name"].astype(str).tolist()
        required = {USER_ID_COL, GAME_ID_COL, TIME_PLAYED_COL}
        missing = sorted(required.difference(set(columns)))
        if missing:
            raise ValueError(
                f"user_interactions is missing required column(s): {missing}. "
                "Expected columns: user_id, game_id, time_played."
            )

        interactions = pd.read_sql_query(
            f"""
            SELECT
                CAST({USER_ID_COL} AS TEXT) AS {USER_ID_COL},
                CAST({GAME_ID_COL} AS TEXT) AS {GAME_ID_COL},
                SUM(COALESCE({TIME_PLAYED_COL}, 0.0)) AS {TIME_PLAYED_COL}
            FROM user_interactions
            WHERE {USER_ID_COL} IS NOT NULL AND {GAME_ID_COL} IS NOT NULL
            GROUP BY {USER_ID_COL}, {GAME_ID_COL}
            """,
            conn,
        )
    finally:
        conn.close()

    interactions[TIME_PLAYED_COL] = pd.to_numeric(interactions[TIME_PLAYED_COL], errors="coerce")
    interactions = interactions.dropna(subset=[TIME_PLAYED_COL])
    interactions = interactions[interactions[TIME_PLAYED_COL] > 0]
    if interactions.empty:
        raise ValueError("No usable rows found in user_interactions after filtering positive time_played.")
    return interactions


def build_interaction_training_frames(
    train_games_df: pd.DataFrame,
    test_games_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_join = interactions_df.merge(train_games_df, on=GAME_ID_COL, how="inner")
    test_join = interactions_df.merge(test_games_df, on=GAME_ID_COL, how="inner")

    if train_join.empty:
        raise ValueError("No user interactions matched the training game feature set.")

    # Fallback in case no interactions hit test games: use a random sample from train for evaluation.
    if test_join.empty:
        sample_n = max(1, int(len(train_join) * 0.2))
        test_join = train_join.sample(n=sample_n, random_state=42)

    for df in [train_join, test_join]:
        df[PLAYTIME_NORMALLY_COL] = pd.to_numeric(df[PLAYTIME_NORMALLY_COL], errors="coerce")
        df[TIME_PLAYED_COL] = pd.to_numeric(df[TIME_PLAYED_COL], errors="coerce")
        df[TARGET_COL] = df[TIME_PLAYED_COL] / df[PLAYTIME_NORMALLY_COL]
        df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="coerce")
        df.dropna(subset=[TARGET_COL], inplace=True)
        df = df[df[TARGET_COL] > 0]

    train_join = train_join[(train_join[PLAYTIME_NORMALLY_COL] > 0) & (train_join[TIME_PLAYED_COL] > 0)]
    test_join = test_join[(test_join[PLAYTIME_NORMALLY_COL] > 0) & (test_join[TIME_PLAYED_COL] > 0)]
    train_join = train_join.dropna(subset=[TARGET_COL]).copy()
    test_join = test_join.dropna(subset=[TARGET_COL]).copy()

    if train_join.empty or test_join.empty:
        raise ValueError("Interaction-level train/test sets are empty after RPI filtering.")

    user_signatures = (
        train_join.groupby(USER_ID_COL)[TARGET_COL]
        .median()
        .rename(USER_PACE_SIGNATURE_COL)
        .reset_index()
    )
    global_signature = _safe_float(user_signatures[USER_PACE_SIGNATURE_COL].median(), 1.0)
    if global_signature <= 0:
        global_signature = 1.0

    train_join = train_join.merge(user_signatures, on=USER_ID_COL, how="left")
    test_join = test_join.merge(user_signatures, on=USER_ID_COL, how="left")
    train_join[USER_PACE_SIGNATURE_COL] = train_join[USER_PACE_SIGNATURE_COL].fillna(global_signature)
    test_join[USER_PACE_SIGNATURE_COL] = test_join[USER_PACE_SIGNATURE_COL].fillna(global_signature)
    train_join[USER_PACE_PROFILE_COL] = train_join[USER_PACE_SIGNATURE_COL].apply(classify_user_pace_signature)
    test_join[USER_PACE_PROFILE_COL] = test_join[USER_PACE_SIGNATURE_COL].apply(classify_user_pace_signature)

    print(
        "[PaceTrain] Built interaction datasets | "
        f"train_rows={len(train_join)} | test_rows={len(test_join)} | "
        f"unique_users_train={train_join[USER_ID_COL].nunique()} | "
        f"unique_games_train={train_join[GAME_ID_COL].nunique()}"
    )
    print(
        "[PaceTrain] User pace profile distribution (train): "
        f"{train_join[USER_PACE_PROFILE_COL].value_counts(dropna=False).to_dict()}"
    )
    return train_join, test_join


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def create_eda_plots(train_df: pd.DataFrame) -> None:
    numeric_df = train_df.select_dtypes(include=["number"]).fillna(0)

    plt.figure(figsize=(14, 10))
    corr = numeric_df.corr()
    sns.heatmap(corr, cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap (Interaction-Level Numeric Features)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "pace_correlation_heatmap.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(train_df[TARGET_COL], bins=40, kde=True)
    plt.title("Distribution of RPI (Relative Preference Intensity)")
    plt.xlabel("RPI")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "rpi_distribution.png", dpi=300)
    plt.close()


def identify_feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
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
    y = pd.to_numeric(df[TARGET_COL], errors="coerce").fillna(0.0)
    return x, y


def train_model(x_train: pd.DataFrame, y_train: pd.Series) -> RandomForestRegressor:
    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
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


def evaluate_ranking_performance(
    model: RandomForestRegressor,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> float:
    preds = model.predict(x_test)
    corr, _ = spearmanr(y_test, preds)
    print(f"-> Spearman Rank Correlation: {corr:.4f}")
    return corr


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
    plt.title("Feature Importance (Pace Compatibility Model)")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "pace_feature_importance.png", dpi=300)
    plt.close()


def save_predicted_vs_actual_plot(y_test: pd.Series, preds: pd.Series) -> None:
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_test, y=preds, alpha=0.6)

    min_val = min(y_test.min(), preds.min())
    max_val = max(y_test.max(), preds.max())
    plt.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--")

    plt.title("Predicted vs Actual RPI")
    plt.xlabel("Actual RPI")
    plt.ylabel("Predicted RPI")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "rpi_predicted_vs_actual.png", dpi=300)
    plt.close()


def save_model(model: RandomForestRegressor, feature_cols: list[str], train_df: pd.DataFrame) -> None:
    default_signature = _safe_float(train_df[USER_PACE_SIGNATURE_COL].median(), 1.0)
    artifact = {
        "model": model,
        "feature_columns": feature_cols,
        "target_column": TARGET_COL,
        "model_kind": "pace_compatibility",
        "default_user_pace_signature": default_signature,
    }
    joblib.dump(artifact, MODEL_PATH)


def main() -> None:
    ensure_directories()

    train_games_df, test_games_df = load_game_feature_data()
    ttb_df = load_game_time_to_beat_map()
    train_games_df, test_games_df = attach_playtime_normally(train_games_df, test_games_df, ttb_df)
    interactions_df = load_user_interactions()
    train_df, test_df = build_interaction_training_frames(train_games_df, test_games_df, interactions_df)

    create_eda_plots(train_df)
    feature_cols, binary_cols = identify_feature_columns(train_df)
    x_train, y_train = prepare_xy(train_df, feature_cols)
    x_test, y_test = prepare_xy(test_df, feature_cols)

    model = train_model(x_train, y_train)
    metrics, preds = evaluate_model(model, x_test, y_test)
    rank_corr = evaluate_ranking_performance(model, x_test, y_test)

    save_model(model, feature_cols, train_df)
    save_feature_importance_plot(model, feature_cols)
    save_predicted_vs_actual_plot(y_test, preds)

    print("Pace compatibility regression training complete.")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Plots saved to: {PLOTS_DIR}")
    print(f"Target: {TARGET_COL}")
    print(f"Numeric feature count: {len(feature_cols)}")
    print(f"Binary feature count: {len(binary_cols)}")
    print("Evaluation on test set:")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  R^2: {metrics['r2']:.4f}")
    print(f"  Spearman: {rank_corr:.4f}")


if __name__ == "__main__":
    main()
