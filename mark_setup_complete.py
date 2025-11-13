"""
Mark setup as complete for existing installations that have already been configured.
Run this on existing databases that already have the branding settings.
"""
import sqlite3
import sys

def mark_complete(db_path='checkin.db'):
    """Mark setup as complete in database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Check if is_setup_complete setting exists
        cur = conn.execute("SELECT value FROM settings WHERE key = 'is_setup_complete'")
        row = cur.fetchone()
        
        if row:
            current_value = row['value']
            if current_value == 'true':
                print(f"✓ Setup is already marked as complete in {db_path}")
            else:
                conn.execute("UPDATE settings SET value = 'true' WHERE key = 'is_setup_complete'")
                conn.commit()
                print(f"✓ Marked setup as complete in {db_path}")
        else:
            # Add the setting
            conn.execute("INSERT INTO settings (key, value) VALUES ('is_setup_complete', 'true')")
            conn.commit()
            print(f"✓ Added is_setup_complete=true to {db_path}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'checkin.db'
    success = mark_complete(db_path)
    sys.exit(0 if success else 1)
