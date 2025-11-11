"""
Migration script to add authorized_adults column to kids table.
Run this once to update existing databases.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'checkin.db'

def migrate():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(kids)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'authorized_adults' in columns:
        print("Column 'authorized_adults' already exists in kids table.")
        conn.close()
        return
    
    # Add the column
    print("Adding authorized_adults column to kids table...")
    cursor.execute("ALTER TABLE kids ADD COLUMN authorized_adults TEXT")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
