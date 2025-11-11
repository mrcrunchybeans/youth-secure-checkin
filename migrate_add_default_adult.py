"""
Migration script to add default_adult_id column to families table.
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
    cursor.execute("PRAGMA table_info(families)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'default_adult_id' in columns:
        print("Column 'default_adult_id' already exists in families table.")
        conn.close()
        return
    
    # Add the column
    print("Adding default_adult_id column to families table...")
    cursor.execute("""
        ALTER TABLE families 
        ADD COLUMN default_adult_id INTEGER 
        REFERENCES adults(id) ON DELETE SET NULL
    """)
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
