#!/usr/bin/env python3
"""
Reset the auto-increment counter for the checkins table.
This will make the next check-in start from ID 1.

WARNING: Only run this when there are NO check-ins in the database,
or the next ID will be max(existing_id) + 1.
"""

import sqlite3

DB_PATH = '/var/www/troop_checkin/checkin.db'

def reset_checkin_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if there are any check-ins
    cursor.execute("SELECT COUNT(*) FROM checkins")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"WARNING: There are {count} check-in(s) in the database.")
        print("The next ID will be the highest current ID + 1.")
        cursor.execute("SELECT MAX(id) FROM checkins")
        max_id = cursor.fetchone()[0]
        print(f"Current maximum ID: {max_id}")
        print(f"Next ID will be: {max_id + 1}")
    else:
        print("No check-ins found in database.")
    
    # Reset the auto-increment counter
    # In SQLite, deleting from sqlite_sequence resets the counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='checkins'")
    
    conn.commit()
    conn.close()
    
    if count == 0:
        print("\nAuto-increment counter reset successfully!")
        print("Next check-in will have ID 1.")
    else:
        print("\nNote: To truly start from ID 1, you need to delete all check-ins first.")
        print("You can do this from the admin panel or by running:")
        print("  DELETE FROM checkins;")
        print("  DELETE FROM sqlite_sequence WHERE name='checkins';")

if __name__ == '__main__':
    reset_checkin_ids()
