# Encryption Keys Setup Guide

## Quick Start

### 1. Generate Encryption Keys

```bash
# Database encryption key
DB_KEY=$(openssl rand -hex 32)
echo "DB_ENCRYPTION_KEY=$DB_KEY"

# Field encryption key
FIELD_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "FIELD_ENCRYPTION_KEY=$FIELD_KEY"
```

### 2. Add to .env

```bash
cat >> .env << EOF

# Database encryption key (AES-256 with SQLCipher)
DB_ENCRYPTION_KEY=$DB_KEY

# Field encryption key (Fernet for sensitive fields)
FIELD_ENCRYPTION_KEY=$FIELD_KEY
EOF
```

### 3. Install Dependencies

```bash
pip install sqlcipher3-binary cryptography
# Or update all dependencies:
pip install -r requirements.txt
```

### 4. Migrate Database

```bash
# Review migration
python migrate_encrypt_database.py

# Execute migration
python migrate_encrypt_database.py --confirm
```

### 5. Test

```bash
flask run
# Test family lookup, verify phone lookup works, check database is encrypted
```

---

## For Self-Hosted Deployments

### Using Docker

Add to `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      - DB_ENCRYPTION_KEY=${DB_ENCRYPTION_KEY}
      - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY}
```

Create `.env.production`:
```env
DB_ENCRYPTION_KEY=<your-generated-key>
FIELD_ENCRYPTION_KEY=<your-generated-key>
```

**Important**: Keep `.env.production` secure, don't commit to Git.

### Multiple Server Setup

If running multiple instances:
1. **Generate keys once**
2. **Use same keys on all servers** (for replication/clustering)
3. **Store .env in encrypted vault** (HashiCorp Vault, AWS Secrets Manager, etc.)
4. **Never commit .env to Git**
5. **Backup .env separately** from database

---

## Key Rotation (Advanced)

To change encryption keys (e.g., if compromised):

```bash
# 1. Generate new keys
NEW_DB_KEY=$(openssl rand -hex 32)
NEW_FIELD_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# 2. Create backup with old keys
cp data/checkin.db data/checkin.db.before-rotation

# 3. Stop the app

# 4. Update .env with new keys
sed -i "s/DB_ENCRYPTION_KEY=.*/DB_ENCRYPTION_KEY=$NEW_DB_KEY/" .env
sed -i "s/FIELD_ENCRYPTION_KEY=.*/FIELD_ENCRYPTION_KEY=$NEW_FIELD_KEY/" .env

# 5. Run migration to re-encrypt with new keys
# (This will use old keys from env, then encrypt with new keys)
python migrate_encrypt_database.py --confirm

# 6. Test thoroughly
flask run

# 7. Delete old backup
rm data/checkin.db.before-rotation
```

---

## Verification Commands

### Check Keys are Set

```bash
echo "DB_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY"
echo "FIELD_ENCRYPTION_KEY=$FIELD_ENCRYPTION_KEY"
```

### Test Encryption

```bash
python -c "
from encryption import DatabaseEncryption, FieldEncryption
print('✅ DB keys valid:', end=' ')
try:
    DatabaseEncryption.validate_keys()
    print('YES')
except: print('NO')

print('✅ Field keys valid:', end=' ')
try:
    fe = FieldEncryption()
    test = fe.encrypt('test')
    fe.decrypt(test)
    print('YES')
except: print('NO')
"
```

### Check Encrypted Database

```bash
python -c "
from encryption import get_encrypted_db_connection
conn = get_encrypted_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) as count FROM families')
print(f'Families in encrypted DB: {cursor.fetchone()[0]}')
cursor.execute('SELECT phone FROM families LIMIT 1')
phone = cursor.fetchone()[0] if cursor.fetchone() else None
if phone:
    print(f'Sample encrypted phone: {phone[:30]}...')
    print(f'Is encrypted: {phone.startswith(\"gAAAAAB\")}')
"
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sqlcipher3'"

```bash
pip install sqlcipher3-binary
```

### "DB_ENCRYPTION_KEY not set"

Check .env exists and has the key:
```bash
grep DB_ENCRYPTION_KEY .env
# If not found, add it:
echo "DB_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
```

### "Invalid FIELD_ENCRYPTION_KEY format"

Key must be in Fernet format (base64-encoded):
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy this output to .env
```

### "file is not a database" error

Old database isn't encrypted yet. Run migration:
```bash
python migrate_encrypt_database.py --confirm
```

---

## Backup Strategy

### Before Encryption
```bash
# Backup unencrypted (reference only, don't keep long-term)
cp data/checkin.db data/checkin.db.unencrypted.backup
cp .env .env.backup
```

### After Encryption
```bash
# Regular backups are now encrypted at 2 layers:
# 1. SQLCipher encryption (in database file)
# 2. Backup zip encryption (pyzipper AES-256)

# Keep .env backup in separate secure location
# (Not with database backups)
gpg --symmetric .env.backup  # or use password manager
```

---

## Disaster Recovery

If you lose your .env keys:

```
⚠️ WITHOUT THE ENCRYPTION KEYS:
- Database is permanently unreadable
- No recovery possible (by design)
- Keep backups of .env in secure location!
```

**Prevention:**
1. Store .env in password manager (1Password, Vault, etc.)
2. Backup .env to encrypted external drive
3. Document recovery process
4. Test recovery process yearly

---

## Resources

- [Encryption Security Guide](SECURITY_ENCRYPTION.md)
- [SQLCipher Documentation](https://www.zetetic.net/sqlcipher/)
- [Cryptography Library](https://cryptography.io/)
