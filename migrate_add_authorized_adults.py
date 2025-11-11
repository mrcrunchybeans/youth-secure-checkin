"""
Migration script to move authorized_adults from kids table to families table.
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
    
    # Check if families table already has authorized_adults
    cursor.execute("PRAGMA table_info(families)")
    family_columns = [col[1] for col in cursor.fetchall()]
    
    if 'authorized_adults' in family_columns:
        print("Column 'authorized_adults' already exists in families table.")
        
        # Check if we need to remove it from kids table
        cursor.execute("PRAGMA table_info(kids)")
        kid_columns = [col[1] for col in cursor.fetchall()]
        
        if 'authorized_adults' in kid_columns:
            print("Removing authorized_adults column from kids table...")
            # SQLite doesn't support DROP COLUMN directly, need to recreate table
            cursor.execute("""
                CREATE TABLE kids_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    family_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (family_id) REFERENCES families(id)
                )
            """)
            cursor.execute("""
                INSERT INTO kids_new (id, family_id, name, notes)
                SELECT id, family_id, name, notes FROM kids
            """)
            cursor.execute("DROP TABLE kids")
            cursor.execute("ALTER TABLE kids_new RENAME TO kids")
            conn.commit()
            print("Removed authorized_adults from kids table.")
        
        conn.close()
        return
    
    # Add authorized_adults column to families table
    print("Adding authorized_adults column to families table...")
    cursor.execute("ALTER TABLE families ADD COLUMN authorized_adults TEXT")
    
    # Check if kids table has authorized_adults column
    cursor.execute("PRAGMA table_info(kids)")
    kid_columns = [col[1] for col in cursor.fetchall()]
    
    if 'authorized_adults' in kid_columns:
        print("Migrating data from kids.authorized_adults to families.authorized_adults...")
        # For each family, combine all unique authorized_adults from their kids
        cursor.execute("""
            UPDATE families
            SET authorized_adults = (
                SELECT GROUP_CONCAT(DISTINCT k.authorized_adults, ', ')
                FROM kids k
                WHERE k.family_id = families.id 
                AND k.authorized_adults IS NOT NULL 
                AND k.authorized_adults != ''
            )
        """)
        
        # Now remove the column from kids table
        print("Removing authorized_adults column from kids table...")
        cursor.execute("""
            CREATE TABLE kids_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (family_id) REFERENCES families(id)
            )
        """)
        cursor.execute("""
            INSERT INTO kids_new (id, family_id, name, notes)
            SELECT id, family_id, name, notes FROM kids
        """)
        cursor.execute("DROP TABLE kids")
        cursor.execute("ALTER TABLE kids_new RENAME TO kids")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
