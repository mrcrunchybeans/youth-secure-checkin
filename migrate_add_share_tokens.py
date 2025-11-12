#!/usr/bin/env python3
"""Migration script to add share_tokens table"""
import sqlite3

conn = sqlite3.connect('checkin.db')

# Create share_tokens table
conn.execute("""
CREATE TABLE IF NOT EXISTS share_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    family_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    checkin_ids TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
)
""")

conn.commit()
conn.close()

print("✅ Migration complete: share_tokens table created")
