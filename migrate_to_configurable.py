"""
Migration script to add customization settings for open-source release
Adds organization branding, colors, and terminology configuration
"""
import sqlite3
import sys

def migrate_database(db_path='checkin.db'):
    """Add new configuration settings to existing database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # New settings with defaults (Trail Life themed for existing installations)
    new_settings = [
        ('organization_name', 'Trail Life WI-4603'),
        ('organization_type', 'youth_group'),  # youth_group, church, sports_team, school, other
        ('primary_color', '#79060d'),     # Main brand color (burgundy/red)
        ('secondary_color', '#003b59'),   # Secondary brand color (dark blue)
        ('accent_color', '#4a582d'),      # Accent color (olive green)
        ('group_term', 'Troop'),          # What to call groups (Troop/Class/Team/Group)
        ('group_term_lower', 'troop'),    # Lowercase version
        ('is_setup_complete', 'false'),   # Will be true after setup wizard
    ]
    
    print(f"Migrating database: {db_path}")
    print("Adding new configuration settings...")
    
    for key, value in new_settings:
        # Check if setting already exists
        existing = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if existing:
            print(f"  ✓ {key} already exists (value: {existing['value']})")
        else:
            conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
            print(f"  + Added {key} = {value}")
    
    conn.commit()
    print("\n✅ Migration complete!")
    print("\nNew customizable settings:")
    print("  - Organization name and type")
    print("  - Brand colors (primary, secondary, accent)")
    print("  - Group terminology (Troop/Class/Team/Group)")
    print("\nYou can now customize these in Admin Settings → Branding")
    
    conn.close()

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'checkin.db'
    migrate_database(db_path)
