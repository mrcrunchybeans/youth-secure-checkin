import sqlite3

conn = sqlite3.connect('checkin.db')

# Check if admin_override_password exists
result = conn.execute("SELECT value FROM settings WHERE key = 'admin_override_password'").fetchone()

if result:
    print("admin_override_password already exists:", result[0])
else:
    # Get the current app_password to use as default
    app_password = conn.execute("SELECT value FROM settings WHERE key = 'app_password'").fetchone()
    if app_password:
        # Add the admin_override_password setting (initially same as app_password)
        conn.execute("INSERT INTO settings (key, value) VALUES ('admin_override_password', ?)", (app_password[0],))
        conn.commit()
        print(f"Added admin_override_password setting (set to same as app_password: {app_password[0]})")
        print("You can change this separately in the admin settings page.")
    else:
        print("ERROR: No app_password found in settings!")

conn.close()
