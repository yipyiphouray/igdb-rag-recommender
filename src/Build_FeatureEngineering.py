import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Setup authoritative directory boundaries
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "database" / "igdb_games.db"
OUTPUT_DIR = ROOT_DIR / "data" / "analytics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_confidence_label(count):
    if count is None or count == 0:
        return "No Rating Evidence"
    elif count < 10:
        return "Very Low Confidence"
    elif count < 50:
        return "Low Confidence"
    elif count < 200:
        return "Medium Confidence"
    else:
        return "Higher Confidence"

def get_playtime_label(seconds):
    if seconds is None or seconds == 0:
        return "Unknown Playtime"
    hours = seconds / 3600.0
    if hours <= 5:
        return "Very Short"
    elif hours <= 15:
        return "Short"
    elif hours <= 30:
        return "Medium"
    elif hours <= 60:
        return "Long"
    else:
        return "Very Long"

def build_analytics_tables():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    # MASTER QUERY: Aggregate related many-to-many attributes once per game_id.
    query = """
    WITH
    genre_agg AS (
        SELECT
            gg.game_id,
            IFNULL(REPLACE(GROUP_CONCAT(DISTINCT gn.name), ',', ', '), 'Not Listed') AS genres
        FROM game_genres gg
        JOIN genres gn ON gg.genre_id = gn.genre_id
        GROUP BY gg.game_id
    ),
    theme_agg AS (
        SELECT
            gth.game_id,
            IFNULL(REPLACE(GROUP_CONCAT(DISTINCT t.name), ',', ', '), 'Not Listed') AS themes
        FROM game_themes gth
        JOIN themes t ON gth.theme_id = t.theme_id
        GROUP BY gth.game_id
    ),
    platform_agg AS (
        SELECT
            gp.game_id,
            IFNULL(REPLACE(GROUP_CONCAT(DISTINCT p.name), ',', ', '), 'Not Listed') AS platforms
        FROM game_platforms gp
        JOIN platforms p ON gp.platform_id = p.platform_id
        GROUP BY gp.game_id
    ),
    company_role_agg AS (
        SELECT
            ic.game_id,
            IFNULL(
                REPLACE(
                    GROUP_CONCAT(DISTINCT CASE WHEN IFNULL(ic.publisher, 0) = 1 THEN c.name END),
                    ',',
                    ', '
                ),
                'Not Listed'
            ) AS publishers,
            IFNULL(
                REPLACE(
                    GROUP_CONCAT(DISTINCT CASE WHEN IFNULL(ic.developer, 0) = 1 THEN c.name END),
                    ',',
                    ', '
                ),
                'Not Listed'
            ) AS developers
        FROM involved_companies ic
        JOIN companies c ON ic.company_id = c.company_id
        GROUP BY ic.game_id
    )
    SELECT 
        g.game_id,
        g.name,
        g.slug,
        g.summary,
        g.storyline,
        g.first_release_date_iso,
        g.release_year,
        g.total_rating,
        g.total_rating_count,
        g.game_type_id AS category_id,
        g.game_status_id AS status_id,
        
        IFNULL(gt.type_name, 'Main Game') AS category_decoded,
        IFNULL(gs.status_name, 'Released') AS status_decoded,
        
        IFNULL(AVG(p_prim.value), 0.0) AS popularity,
        MAX(gtb.normally) as playtime_normally,
        
        IFNULL(MAX(mp.campaign_coop), 0) AS mp_campaign_coop,
        IFNULL(MAX(mp.split_screen), 0) AS mp_splitscreen,
        IFNULL(MAX(mp.online_coop), 0) AS mp_online_coop,
        IFNULL(MAX(mp.offline_coop), 0) AS mp_offline_coop,
        IFNULL(MAX(mp.online_max), 0) AS mp_max_online_players,
        
        IFNULL(ga.genres, 'Not Listed') AS genres,
        IFNULL(ta.themes, 'Not Listed') AS themes,
        IFNULL(pa.platforms, 'Not Listed') AS platforms,
        IFNULL(cra.publishers, 'Not Listed') AS publishers,
        IFNULL(cra.developers, 'Not Listed') AS developers
        
    FROM games g
    LEFT JOIN game_types gt ON g.game_type_id = gt.game_type_id
    LEFT JOIN game_statuses gs ON g.game_status_id = gs.game_status_id
    LEFT JOIN popularity_primitives p_prim ON g.game_id = p_prim.game_id
    LEFT JOIN game_time_to_beats gtb ON g.game_id = gtb.game_id
    LEFT JOIN multiplayer_modes mp ON g.game_id = mp.game_id
    LEFT JOIN genre_agg ga ON g.game_id = ga.game_id
    LEFT JOIN theme_agg ta ON g.game_id = ta.game_id
    LEFT JOIN platform_agg pa ON g.game_id = pa.game_id
    LEFT JOIN company_role_agg cra ON g.game_id = cra.game_id
    GROUP BY g.game_id;
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Loaded {len(df)} row files out of storage layer indices.")

    # Apply standard processing bins
    df["rating_confidence"] = df["total_rating_count"].apply(get_confidence_label)
    df["playtime_length"] = df["playtime_normally"].apply(get_playtime_label)
    
    fill_cols = ["genres", "themes", "platforms", "publishers", "developers"]
    for col in fill_cols:
        df[col] = df[col].fillna("Not Listed")

    # Construct RAG profile grounding documentation
    print("Writing markdown tracking summaries for RAG embedding engine arrays...")
    def generate_rag_profile(row):
        summary_text = row["summary"] if pd.notna(row["summary"]) and row["summary"].strip() != "" else "Metadata profile summary not provided by catalog."
        story_text = f"\nStoryline: {row['storyline']}" if pd.notna(row["storyline"]) and row["storyline"].strip() != "" else ""
        mp_status = "Available" if (row["mp_campaign_coop"] or row["mp_splitscreen"] or row["mp_online_coop"]) else "Not Supported / Single Player Only"
        
        return (
            f"Title: {row['name']}\nType: {row['category_decoded']}\nStatus: {row['status_decoded']}\n"
            f"Release Year: {row['release_year']}\nDeveloper: {row['developers']}\n"
            f"Publisher: {row['publishers']}\nPlatforms: {row['platforms']}\nGenres: {row['genres']}\n"
            f"Themes: {row['themes']}\nPlaytime Scale: {row['playtime_length']}\n"
            f"Multiplayer Support: {mp_status}\nSummary: {summary_text}{story_text}"
        )
    df["rag_text_profile"] = df.apply(generate_rag_profile, axis=1)

    # Materialize full rich dataset view back into SQL database
    df.to_sql("analytics_ready_games", conn, if_exists="replace", index=False)
    print("Successfully materialized unified `analytics_ready_games` view inside SQLite database.")

    # ==========================================
    # FEATURE DESIGN LAYER
    # ==========================================
    print("Engineering modeling feature spaces...")
    df["is_high_rated"] = (df["total_rating"] >= 80.0).astype(int)
    
    ml_features = df[[
        "game_id", "name", "slug", "first_release_date_iso", "release_year",
        "category_decoded", "status_decoded", "is_high_rated", 
        "rating_confidence", "playtime_length",
        "genres", "themes", "platforms", "developers", "publishers",
        "mp_campaign_coop", "mp_splitscreen", "mp_online_coop", "mp_offline_coop", "mp_max_online_players"
    ]].copy()
    
    ml_features["summary_length"] = df["summary"].fillna("").str.len()
    ml_features["storyline_length"] = df["storyline"].fillna("").str.len()
    
    ml_features["category_is_main_game"] = (df["category_id"] == 0).astype(int)
    ml_features["category_is_variant_or_special"] = (df["category_id"] != 0).astype(int)
    
    target_platforms = ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X|S", "Nintendo Switch"]
    for plat in target_platforms:
        clean_name = f"platform_{plat.lower().replace(' ', '_').replace('|', '_')}"
        ml_features[clean_name] = df["platforms"].apply(lambda x: 1 if plat in x else 0)
        
    ml_features["genre_action"] = df["themes"].apply(lambda x: 1 if "Action" in x else 0)
    target_genres = ["Adventure", "Role-playing (RPG)", "Strategy", "Shooter", "Indie", "Simulator", "Platform"]
    for genre in target_genres:
        clean_name = f"genre_{genre.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}"
        ml_features[clean_name] = df["genres"].apply(lambda x: 1 if genre in x else 0)
        
    ml_features["dev_nintendo"] = df["developers"].apply(lambda x: 1 if "nintendo" in x.lower() else 0)
    ml_features["dev_ubisoft"] = df["developers"].apply(lambda x: 1 if "ubisoft" in x.lower() else 0)
    ml_features["dev_electronic_arts"] = df["developers"].apply(lambda x: 1 if "electronic arts" in x.lower() or "ea " in x.lower() else 0)
    ml_features["dev_sony"] = df.apply(lambda row: 1 if "sony" in row["developers"].lower() or "sony" in row["publishers"].lower() else 0, axis=1)
    ml_features["dev_square_enix"] = df["developers"].apply(lambda x: 1 if "square enix" in x.lower() else 0)
    ml_features["dev_capcom"] = df["developers"].apply(lambda x: 1 if "capcom" in x.lower() else 0)
    ml_features["dev_valve"] = df["developers"].apply(lambda x: 1 if "valve" in x.lower() else 0)

    train_df = ml_features.sample(frac=0.8, random_state=42)
    test_df = ml_features.drop(train_df.index)
    
    train_df.to_csv(OUTPUT_DIR / "modeling_train_features.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "modeling_test_features.csv", index=False)
    
    print(f"Gold processing executed successfully! Generated {len(ml_features.columns)} total layout metrics.")
    conn.close()

if __name__ == "__main__":
    build_analytics_tables()
