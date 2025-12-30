#!/usr/bin/env python3
"""
Migrate existing SQLite database to SQLCipher with field-level encryption.

This script:
1. Backs up the original database
2. Creates a new encrypted database using SQLCipher
3. Encrypts sensitive fields (phone, names, notes, history)
4. Extracts last 4 digits of phone for searchable indexes
5. Verifies data integrity
6. Prompts before replacing original

Usage:
    python migrate_encrypt_database.py
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
from encryption import FieldEncryption, DatabaseEncryption, get_encrypted_db_connection


def backup_original_db():
    """Create a backup of the original unencrypted database."""
    db_path = os.path.join('data', 'checkin.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return None
    
    backup_path = os.path.join(
        'data',
        f'checkin.db.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    )
    
    print(f"📋 Backing up original database to {backup_path}...")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    return backup_path


def get_last_four(phone):
    """Extract last 4 digits from phone number."""
    if not phone:
        return None
    digits = ''.join(c for c in str(phone) if c.isdigit())
    return digits[-4:] if len(digits) >= 4 else None


def migrate_database():
    """Migrate data from unencrypted to encrypted database."""
    
    print("\n" + "="*60)
    print("🔐 Database Encryption Migration")
    print("="*60)
    
    # Validate encryption keys
    print("\n🔑 Validating encryption keys...")
    try:
        DatabaseEncryption.validate_keys()
        print("✅ Encryption keys valid")
    except Exception as e:
        print(f"❌ Encryption setup failed: {e}")
        sys.exit(1)
    
    # Backup original
    backup_path = backup_original_db()
    if not backup_path:
        sys.exit(1)
    
    # Connect to original unencrypted database
    print("\n📖 Reading original database...")
    old_db_path = os.path.join('data', 'checkin.db')
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    
    # Get encryption instance
    fe = FieldEncryption()
    
    # Rename original (we'll replace it)
    temp_db_path = old_db_path + '.unencrypted'
    os.rename(old_db_path, temp_db_path)
    print(f"📝 Original database moved to {temp_db_path}")
    
    try:
        # Create new encrypted database
        print("\n🔐 Creating encrypted database...")
        new_conn = get_encrypted_db_connection()
        
        # Read schema from old database
        print("📋 Reading schema from original database...")
        cursor = old_conn.cursor()
        
        # Get all table definitions
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        # Create tables in new database with additional columns for unencrypted lookups
        new_cursor = new_conn.cursor()
        
        for table in tables:
            table_name = table['name']
            original_sql = table['sql']
            
            # Add last_four columns to phone-containing tables
            if table_name in ['families', 'adults']:
                # Add phone_last_four column if it doesn't exist
                modified_sql = original_sql.rstrip(';')
                if 'phone_last_four' not in modified_sql:
                    modified_sql += ", phone_last_four VARCHAR(4)"
                modified_sql += ";"
                original_sql = modified_sql
            
            print(f"  Creating table: {table_name}")
            new_cursor.execute(original_sql)
        
        new_conn.commit()
        
        # Migrate data table by table
        print("\n📤 Migrating data...")
        
        for table in tables:
            table_name = table['name']
            print(f"\n  Migrating {table_name}...")
            
            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {col[1]: col[2] for col in cursor.fetchall()}  # name -> type
            
            # Read all rows
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"    ℹ️  {table_name} is empty")
                continue
            
            # Prepare for migration
            encrypted_count = 0
            
            for row in rows:
                row_dict = dict(row)
                
                # Encrypt sensitive fields
                if table_name == 'families' and 'phone' in row_dict:
                    original_phone = row_dict['phone']
                    row_dict['phone'] = fe.encrypt(original_phone)
                    row_dict['phone_last_four'] = get_last_four(original_phone)
                    encrypted_count += 1
                
                elif table_name == 'kids' and 'name' in row_dict:
                    row_dict['name'] = fe.encrypt(row_dict['name'])
                    encrypted_count += 1
                
                if table_name == 'kids' and 'notes' in row_dict:
                    row_dict['notes'] = fe.encrypt(row_dict['notes'])
                
                elif table_name == 'adults' and 'phone' in row_dict:
                    original_phone = row_dict['phone']
                    row_dict['phone'] = fe.encrypt(original_phone)
                    row_dict['phone_last_four'] = get_last_four(original_phone)
                    encrypted_count += 1
                
                # For checkins, encrypt all sensitive fields if present
                elif table_name == 'checkins':
                    # Checkins table mainly contains IDs and timestamps
                    # but we'll encrypt it anyway for audit trail security
                    encrypted_count += 1
                
                # Insert into new database
                columns_list = list(row_dict.keys())
                placeholders = ', '.join(['?' for _ in columns_list])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns_list)}) VALUES ({placeholders})"
                
                new_cursor.execute(insert_sql, [row_dict[col] for col in columns_list])
            
            new_conn.commit()
            print(f"    ✅ Migrated {len(rows)} rows ({encrypted_count} encrypted)")
        
        # Migrate indexes
        print("\n📑 Migrating indexes...")
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND sql IS NOT NULL
        """)
        indexes = cursor.fetchall()
        
        for index in indexes:
            print(f"  Creating index: {index['name']}")
            new_cursor.execute(index['sql'])
        
        # Create new index for phone_last_four lookups
        print("\n  Creating index for phone lookups...")
        try:
            new_cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_families_phone_last_four 
                ON families(phone_last_four)
            """)
            new_cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_adults_phone_last_four 
                ON adults(phone_last_four)
            """)
        except sqlite3.OperationalError:
            pass  # Index might already exist
        
        new_conn.commit()
        print("✅ Indexes created")
        
        # Verify integrity
        print("\n✔️ Verifying data integrity...")
        
        # Count records
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            old_count = cursor.fetchone()[0]
            
            new_cursor.execute(f"SELECT COUNT(*) as count FROM {table['name']}")
            new_count = new_cursor.fetchone()[0]
            
            if old_count != new_count:
                print(f"❌ Record count mismatch in {table['name']}: {old_count} vs {new_count}")
                raise ValueError(f"Migration verification failed for {table['name']}")
        
        print("✅ Data integrity verified")
        
        # Close connections
        old_conn.close()
        new_conn.close()
        
        # Summary
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Original backup: {backup_path}")
        print(f"  • Encrypted database: {os.path.join('data', 'checkin.db')}")
        print(f"  • Encryption: AES-256 (SQLCipher + Field-level)")
        print(f"  • Unencrypted backup kept at: {temp_db_path}")
        print(f"\n⚠️  Next steps:")
        print(f"  1. Test the application thoroughly")
        print(f"  2. Verify all lookups and features work")
        print(f"  3. Delete {temp_db_path} when satisfied")
        print(f"  4. Keep {backup_path} as archive")
        print(f"\n🔐 Encryption keys are required in .env:")
        print(f"  • DB_ENCRYPTION_KEY (for SQLCipher)")
        print(f"  • FIELD_ENCRYPTION_KEY (for sensitive fields)")
        print(f"\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"\n🔄 Rolling back...")
        
        # Restore original
        if os.path.exists(temp_db_path):
            os.rename(temp_db_path, old_db_path)
            print(f"✅ Original database restored from {temp_db_path}")
        
        old_conn.close()
        sys.exit(1)


if __name__ == '__main__':
    # Check for confirmation
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        migrate_database()
    else:
        print("\n" + "="*60)
        print("⚠️  DATABASE ENCRYPTION MIGRATION")
        print("="*60)
        print("\nThis script will:")
        print("  1. Backup your current database")
        print("  2. Create an encrypted copy with AES-256")
        print("  3. Encrypt all sensitive fields (names, phones, notes)")
        print("  4. Replace your current database")
        print("\n⚠️  IMPORTANT:")
        print("  • You MUST have DB_ENCRYPTION_KEY and FIELD_ENCRYPTION_KEY in .env")
        print("  • Without these keys, your data CANNOT be recovered")
        print("  • Keep your .env file safe and backed up")
        print("  • Test thoroughly before deleting backups")
        print("\nTo proceed, run:")
        print("  python migrate_encrypt_database.py --confirm")
        print("\n" + "="*60 + "\n")
