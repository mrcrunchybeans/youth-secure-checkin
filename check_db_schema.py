import sqlite3
from pathlib import Path
import os

# Match app.py logic exactly
DATA_DIR = Path('data').resolve()
if DATA_DIR.exists():
    DB_PATH = DATA_DIR / 'checkin.db'
else:
    DB_PATH = Path('checkin.db').resolve()

print(f"Checking database at: {DB_PATH}")

if not DB_PATH.exists():
    print("Database file not found!")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(kids)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Columns in kids table: {columns}")
    
    if 'tlc_id' not in columns:
        print("Adding tlc_id column...")
        try:
            cursor.execute("ALTER TABLE kids ADD COLUMN tlc_id TEXT")
            conn.commit()
            print("Added tlc_id column.")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("tlc_id column already exists.")

    # Check checkins table for tlc_synced
    cursor.execute("PRAGMA table_info(checkins)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Columns in checkins table: {columns}")

    if 'tlc_synced' not in columns:
        print("Adding tlc_synced column...")
        try:
            cursor.execute("ALTER TABLE checkins ADD COLUMN tlc_synced BOOLEAN DEFAULT 0")
            conn.commit()
            print("Added tlc_synced column.")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("tlc_synced column already exists.")

    conn.close()