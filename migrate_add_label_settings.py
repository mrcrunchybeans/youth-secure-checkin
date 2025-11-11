#!/usr/bin/env python3
"""
Migration: Add label printing settings to settings table
Adds: require_checkout_code, label_printer_type, label_width, label_height
"""

import sqlite3

DB_PATH = '/var/www/troop_checkin/checkin.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    settings = {
        'require_checkout_code': 'false',
        'label_printer_type': 'dymo',
        'label_width': '2.0',
        'label_height': '1.0'
    }
    
    for key, default_value in settings.items():
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result is None:
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, default_value))
            print(f"Added setting: {key} = {default_value}")
        else:
            print(f"Setting '{key}' already exists with value: {result[0]}")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
