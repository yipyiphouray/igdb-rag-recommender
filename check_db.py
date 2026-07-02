import sqlite3
from pathlib import Path

# Use the exact same path your training script uses
db_path = Path(__file__).resolve().parent / "data" / "database" / "igdb_games.db"

def check_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in {db_path.name}: {tables}")
        
        if ('user_interactions',) in tables:
            cursor.execute("SELECT COUNT(*) FROM user_interactions")
            count = cursor.fetchone()[0]
            print(f"Table 'user_interactions' exists with {count} rows.")
        else:
            print("Table 'user_interactions' NOT FOUND.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()