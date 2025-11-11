#!/usr/bin/env python3
"""
Migration: Add checkout_code column to checkins table
This supports the optional label printing feature where parents receive
a unique code to verify checkout.
"""

import sqlite3

DB_PATH = '/var/www/troop_checkin/checkin.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(checkins)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'checkout_code' in columns:
        print("Column 'checkout_code' already exists in checkins table.")
    else:
        print("Adding 'checkout_code' column to checkins table...")
        cursor.execute("ALTER TABLE checkins ADD COLUMN checkout_code TEXT")
        print("Column added successfully!")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
