#!/usr/bin/env python3
"""
Cleanup script to remove orphaned check-in records.
Deletes check-ins where the kid_id no longer exists in the kids table.
"""

import sqlite3

DB_PATH = '/var/www/troop_checkin/checkin.db'

def cleanup_orphaned_checkins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find orphaned check-ins
    cursor.execute("""
        SELECT c.id, c.kid_id, c.checkin_time 
        FROM checkins c 
        LEFT JOIN kids k ON c.kid_id = k.id 
        WHERE k.id IS NULL
    """)
    orphaned = cursor.fetchall()
    
    if not orphaned:
        print("No orphaned check-ins found.")
        conn.close()
        return
    
    print(f"Found {len(orphaned)} orphaned check-in(s):")
    for checkin_id, kid_id, checkin_time in orphaned:
        print(f"  Check-in ID {checkin_id}: kid_id={kid_id}, time={checkin_time}")
    
    # Delete orphaned check-ins
    cursor.execute("""
        DELETE FROM checkins 
        WHERE id IN (
            SELECT c.id 
            FROM checkins c 
            LEFT JOIN kids k ON c.kid_id = k.id 
            WHERE k.id IS NULL
        )
    """)
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"\nDeleted {deleted_count} orphaned check-in record(s).")
    print("Cleanup complete!")

if __name__ == '__main__':
    cleanup_orphaned_checkins()
