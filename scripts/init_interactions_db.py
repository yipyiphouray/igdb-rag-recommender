import json
import sqlite3
import os
from pathlib import Path

def init_db():
    # Use the same path as train_predictive_model.py (data/database/igdb_games.db)
    # This assumes your project root is one level above the 'scripts' folder
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "database" / "igdb_games.db"
    
    print(f"Connecting to database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute("DROP TABLE IF EXISTS user_interactions")
    cursor.execute("""
        CREATE TABLE user_interactions (
            user_id TEXT,
            game_id TEXT,
            time_played REAL
        )
    """)
    
    # Load your JSON data
    json_path = project_root / "tests" / "golden_dataset.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Populate
    for archetype, user_data in data.items():
        for interaction in user_data['interactions']:
            cursor.execute(
                "INSERT INTO user_interactions VALUES (?, ?, ?)",
                (user_data['user_id'], str(interaction['game_id']), float(interaction['time_played']))
            )
            
    conn.commit()
    conn.close()
    print("Success: user_interactions table created and populated.")

if __name__ == "__main__":
    init_db()