import sqlite3
import os

DB_PATH = os.path.join('data', 'checkin.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("SELECT tlc_synced FROM checkins LIMIT 1")
        print("Column 'tlc_synced' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'tlc_synced' column to checkins table...")
        cursor.execute("ALTER TABLE checkins ADD COLUMN tlc_synced BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
