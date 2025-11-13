import sqlite3

conn = sqlite3.connect('checkin.db')
tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("Existing tables:", tables)

# Check if settings table exists
if 'settings' not in tables:
    print("\nMISSING: settings table")
else:
    print("\nSettings table exists")
    # Check what settings are in there
    settings = conn.execute("SELECT key, value FROM settings").fetchall()
    print("Settings:", settings)

conn.close()
