import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "igdb_games.db"


def check_db() -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in {DATABASE_PATH.name}: {tables}")

            if ("user_interactions",) in tables:
                cursor.execute("SELECT COUNT(*) FROM user_interactions")
                count = cursor.fetchone()[0]
                print(f"Table 'user_interactions' exists with {count} rows.")
            else:
                print("Table 'user_interactions' NOT FOUND.")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    check_db()

