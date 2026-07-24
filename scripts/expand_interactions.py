import json
import sqlite3
import random
from pathlib import Path

def expand_interactions():
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "database" / "igdb_games.db"
    json_path = project_root / "tests" / "golden_dataset.json"

    with open(json_path, 'r') as f:
        archetypes = json.load(f)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DROP TABLE IF EXISTS user_interactions")
    cursor.execute("""
        CREATE TABLE user_interactions (
            user_id TEXT,
            game_id TEXT,
            time_played REAL
        )
    """)

    print(f"Generating expanded data into {db_path}...")

    # Expanded generation
    for arch_name, data in archetypes.items():
        user_id = data['user_id']
        # Generate 150 interactions per archetype for a total of 450 rows
        for _ in range(150):
            game_id = random.randint(1000, 300000) # Representative of IGDB game IDs
            
            # Logic: Assign time_played based on archetype behavior
            if arch_name == "StrategyFan":
                # Prefers deep, long-form games
                time = random.uniform(80.0, 400.0)
            elif arch_name == "ActionJunkie":
                # Prefers quick, snackable play
                time = random.uniform(2.0, 40.0)
            else:
                # Balanced/Casual
                time = random.uniform(10.0, 150.0)
                
            cursor.execute("INSERT INTO user_interactions VALUES (?, ?, ?)", 
                           (user_id, str(game_id), time))

    conn.commit()
    conn.close()
    print("Expansion complete: 450 rows of synthetic interaction data created.")

if __name__ == "__main__":
    expand_interactions()