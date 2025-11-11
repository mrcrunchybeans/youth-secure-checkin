#!/usr/bin/env python3
"""
Clear check-in history from the database.
This will delete all check-in records and optionally reset the ID counter.

Usage:
  python3 clear_checkin_history.py           # Delete all check-ins, keep ID counter
  python3 clear_checkin_history.py --reset   # Delete all check-ins and reset ID to 1
"""

import sqlite3
import sys

DB_PATH = '/var/www/troop_checkin/checkin.db'

def clear_history(reset_ids=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("SELECT COUNT(*) FROM checkins")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("No check-ins found in database. Nothing to clear.")
        conn.close()
        return
    
    cursor.execute("SELECT COUNT(*) FROM checkins WHERE checkout_time IS NULL")
    active_count = cursor.fetchone()[0]
    
    print(f"Found {count} total check-in(s) in history.")
    if active_count > 0:
        print(f"WARNING: {active_count} check-in(s) are still active (not checked out).")
    
    # Confirm deletion
    response = input("\nAre you sure you want to delete ALL check-in history? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        conn.close()
        return
    
    # Delete all check-ins
    cursor.execute("DELETE FROM checkins")
    deleted = cursor.rowcount
    
    # Optionally reset the ID counter
    if reset_ids:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='checkins'")
        print(f"\nDeleted {deleted} check-in record(s).")
        print("Auto-increment counter reset. Next check-in will have ID 1.")
    else:
        print(f"\nDeleted {deleted} check-in record(s).")
        print("ID counter preserved. Next check-in will continue from previous sequence.")
    
    conn.commit()
    conn.close()
    print("Check-in history cleared successfully!")

if __name__ == '__main__':
    reset = '--reset' in sys.argv or '-r' in sys.argv
    clear_history(reset_ids=reset)
