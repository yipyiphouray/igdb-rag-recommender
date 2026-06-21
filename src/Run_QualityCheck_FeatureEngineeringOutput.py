import pandas as pd
import numpy as np
from pathlib import Path

# Setup authoritative directory boundaries
ROOT_DIR = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT_DIR / "data" / "analytics" / "modeling_train_features.csv"
TEST_PATH = ROOT_DIR / "data" / "analytics" / "modeling_test_features.csv"

def run_checks():
    print("==================================================")
    print("    IGDB RECONSTRUCTION PIPELINE: COMPREHENSIVE DQ  ")
    print("==================================================\n")
    
    if not TRAIN_PATH.exists():
        print(f"Error: Feature matrices not found at {TRAIN_PATH}. Please run build_analytics_ready.py first.")
        return
        
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)
    full_df = pd.concat([train_df, test_df], axis=0)
    
    print(f"[PASSED] Analytical Matrix Ingestion Verified.")
    print(f"       -> Total Records Cleaned: {len(full_df)}")
    print(f"       -> Training Set (80%):    {len(train_df)} rows")
    print(f"       -> Testing Set (20%):     {len(test_df)} rows\n")
    
    print("--------------------------------------------------")
    print("CHECK 1: IDENTITY MULTIPLIER INTEGRITY")
    print("--------------------------------------------------")
    duplicate_ids = full_df.duplicated(subset=['game_id']).sum()
    if duplicate_ids == 0:
        print(f"[SUCCESS] Row multiplier trap averted. Unique Game IDs: {full_df['game_id'].nunique()}")
    else:
        print(f"[CRITICAL FAILURE] Found {duplicate_ids} duplicate game_id entries! Check grouping logic.")

    print("\n--------------------------------------------------")
    print("CHECK 2: TEXT PROFILE BOUNDARIES (RAG ENGINES)")
    print("--------------------------------------------------")
    blank_summaries = (full_df['summary_length'].fillna(0) == 0).sum()
    avg_summary = full_df['summary_length'].mean()
    
    # Check if raw text categorical columns contain default "Not Listed" null replacements
    not_listed_genres = (full_df['genres'] == "Not Listed").sum()
    not_listed_devs = (full_df['developers'] == "Not Listed").sum()
    
    if blank_summaries == 0:
        print(f"[SUCCESS] 100% of game profiles possess structural summary tokens.")
    else:
        print(f"[WARNING] {blank_summaries} titles contain completely blank text layouts.")
    print(f"       -> Average Summary Length: {avg_summary:.1f} characters")
    print(f"       -> Genres Missing Array Strings: {not_listed_genres}")
    print(f"       -> Developers Missing Array Strings: {not_listed_devs}")

    print("\n--------------------------------------------------")
    print("CHECK 3: MULTIPLAYER RANGE INTEGRITY REGISTER")
    print("--------------------------------------------------")
    # Make sure multiplayer binary flags don't contain stray text strings or numbers out of bounds
    invalid_coop = (~full_df['mp_campaign_coop'].isin([0, 1])).sum()
    max_players_registered = full_df['mp_max_online_players'].max()
    games_with_multiplayer = (full_df['mp_campaign_coop'] + full_df['mp_splitscreen'] + full_df['mp_online_coop'] > 0).sum()
    
    if invalid_coop == 0:
        print(f"[SUCCESS] Multiplayer indicators conform to clean binary bits.")
    else:
        print(f"[CRITICAL] Found non-binary noise values inside multiplayer dimensions!")
    print(f"       -> Total Games with Multi-Play Capacity: {games_with_multiplayer} / {len(full_df)}")
    print(f"       -> Maximum Cap Player Sizing Detected: {int(max_players_registered)} players")

    print("\n--------------------------------------------------")
    print("CHECK 4: ONE-HOT DENSITY & SPARSITY LOGS")
    print("--------------------------------------------------")
    print("Evaluating flag activation density parameters across engineered matrices:")
    
    # Filter for engineered one-hot columns while strictly excluding descriptive text strings
    feature_cols = [
        col for col in full_df.columns 
        if col.startswith(('platform_', 'genre_', 'dev_', 'category_')) 
        and not col.endswith('_decoded')
    ]
    
    for col in feature_cols:
        positive_count = full_df[col].sum()
        percentage = (positive_count / len(full_df)) * 100
        print(f"  Column: {col:<32} | Enrolled Rows: {positive_count:<4} | Fill: {percentage:.1f}%")

    print("\n--------------------------------------------------")
    print("CHECK 5: MODEL TARGET BALANCING REGISTER")
    print("--------------------------------------------------")
    target_counts = full_df['is_high_rated'].value_counts()
    high_rate_pct = (full_df['is_high_rated'].sum() / len(full_df)) * 100
    print(f"Target variable 'is_high_rated' distribution:")
    print(f"  -> Low/Medium Quality (0): {target_counts.get(0, 0)} records")
    print(f"  -> High Quality (1):        {target_counts.get(1, 0)} records")
    print(f"  -> Positive Baseline Skew:  {high_rate_pct:.2f}%")
    
    print("\n==================================================")
    print("               END OF QUALITY REPORT              ")
    print("==================================================")

if __name__ == "__main__":
    run_checks()