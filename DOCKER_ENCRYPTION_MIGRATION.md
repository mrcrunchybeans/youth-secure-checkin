# Docker Encryption Migration Guide

## 📢 Important: Updating to Encrypted Version

**Version:** 1.0.1+ (as of Dec 30, 2025)

**🎉 GOOD NEWS:** Encryption migration is now **fully automatic**! When you update to v1.0.1+, the application will detect unencrypted data and migrate it automatically on startup.

---

## ⚠️ What Changed

The application now includes **mandatory encryption**:
- Database encrypted at rest (AES-256 SQLCipher)
- Sensitive fields encrypted (phone, email, names, notes)
- Unique encryption keys required per deployment

### If You Don't Update:
❌ Old images will NOT work with encrypted data
❌ New images REQUIRE encryption keys in `.env`

### If You Do Update:
✅ Existing unencrypted data will be migrated **automatically on startup**
✅ New instances are encrypted from first startup
✅ Backups are created automatically before migration
✅ No manual migration script needed (optional if you prefer manual control)
✅ You can roll back if needed

---

## 🚀 Quick Update (3 Steps - Fully Automatic!)

### Step 1: Add Encryption Keys to .env

```bash
# Navigate to your instance directory
cd /path/to/youth-checkin

# Generate encryption keys
DB_ENCRYPTION_KEY=$(openssl rand -hex 32)
FIELD_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Add to .env
cat >> .env << EOF
DB_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY
FIELD_ENCRYPTION_KEY=$FIELD_ENCRYPTION_KEY
EOF

# Verify they were added
grep "ENCRYPTION_KEY" .env
```

### Step 2: Pull Latest Image and Restart

```bash
# Pull the latest image
docker compose pull

# Restart the container
docker compose down
docker compose up -d
```

### Step 3: Watch the Magic Happen

```bash
# Check the logs - migration happens automatically!
docker compose logs -f

# You'll see messages like:
# "Encryption migration: Detected unencrypted database with encryption keys set"
# "Encryption migration: Starting automatic migration..."
# "Encryption migration: Database backed up to data/backups/checkin.db.backup-TIMESTAMP"
# "Encryption migration: Completed successfully"
```

**That's it!** No manual migration script needed. The app handles everything automatically.

---

## 🔄 What Happens Automatically During Startup

When the container starts with encryption keys in .env:

1. **Detection**: App checks if database is unencrypted but encryption keys are set
2. **Backup**: Original database is backed up to `data/backups/checkin.db.backup-TIMESTAMP`
3. **Migration**: Encrypts database and all sensitive fields
4. **Verification**: Verifies data integrity
5. **Startup**: App continues normally with fully encrypted database

Watch it happen in the logs - the whole process takes 30 seconds to 2 minutes depending on database size.

---

## 📋 Detailed Update Process (If You Prefer More Control)
FIELD_ENCRYPTION_KEY=44-character-base64-string-here
```

⚠️ **IMPORTANT:** Never share these keys. Treat them like passwords.

### Advanced: Manual Migration (Optional)

If you prefer to manually control the migration instead of letting it happen automatically:

```bash
# Set environment variable to SKIP automatic migration
export SKIP_AUTO_ENCRYPTION=1

# Start the container
docker compose up -d

# Then manually run the migration whenever you're ready
docker compose exec web python migrate_encrypt_database.py

# Follow all the prompts - the script will guide you through the process
```

**When to use manual:**
- You want full control over timing
- You prefer to see prompts and confirmations
- You're migrating during specific maintenance windows
- You want detailed logs of each step

---

## 🐳 Docker-Specific Notes

```bash
# New (v2) - use with space
docker compose up -d
docker compose logs

# Old (v1) - use with hyphen
docker-compose up -d
docker-compose logs

# Check your version
docker compose version
```

The new version (v2) is recommended.

### Multi-Container Setup

If you're running multiple instances:

```bash
# Instance 1
cd instance-1
# Generate UNIQUE keys
# Update .env
# docker compose up -d
# docker compose exec web python migrate_encrypt_database.py --confirm

# Instance 2
cd instance-2
# Generate DIFFERENT keys (very important!)
# Update .env
# docker compose up -d
# docker compose exec web python migrate_encrypt_database.py --confirm
```

⚠️ **Each instance MUST have unique encryption keys.**

---

## 🔄 Rolling Back (If Needed)

If something goes wrong:

```bash
# Stop current container
docker compose stop

# Restore from backup
rm -r data
cp -r data.pre-encryption-backup-* data

# Use old image (revert to previous version)
# Edit docker-compose.yml:
# Change: image: mrcrunchybeans/youth-secure-checkin:latest
# To: image: mrcrunchybeans/youth-secure-checkin:v1.0.0

# Remove encryption keys from .env temporarily
# Remove DB_ENCRYPTION_KEY and FIELD_ENCRYPTION_KEY lines

# Start with old image
docker compose down
docker compose up -d
```

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'"

The image wasn't updated correctly.

---

## ⚠️ Troubleshooting Automatic Migration

### "Encryption migration: Failed with error..."

Check the logs immediately:

```bash
docker compose logs -f

# Common causes:
# 1. Database locked (app is accessing it)
# 2. Insufficient disk space
# 3. Backup directory not writable
# 4. Invalid encryption key format
```

### "Encryption keys not set" on restart

The `.env` file isn't being loaded properly.

```bash
# Verify .env exists and has correct keys
cat .env | grep ENCRYPTION_KEY

# Verify Docker is reading it
docker compose config | grep -A2 "ENCRYPTION_KEY"

# If missing, add to .env and restart
docker compose down
docker compose up -d
```

### Migration seems stuck

Check if it's still processing:

```bash
# Watch the logs
docker compose logs --follow

# Check CPU/memory usage
docker stats

# If truly stuck (no activity for 5+ minutes):
docker compose stop
docker compose up -d
# It will retry the migration

# If it fails again, see manual migration option above
```

### Rollback After Migration

If something goes wrong, you can rollback:

```bash
# Stop the container
docker compose stop

# Restore from backup
rm -r data/checkin.db
cp data/backups/checkin.db.backup-* data/checkin.db

# Clear the migration flag (optional)
rm -f data/.encryption_migrated

# Restart
docker compose up -d
```

---

## ✅ Success Indicators

After migration, you should see:

1. ✅ Logs show "Encryption migration: Completed successfully"
2. ✅ `/health` endpoint returns `{"status": "ok"}`
3. ✅ Web interface loads at http://localhost:5000
4. ✅ Can view and create check-ins normally
5. ✅ Database file exists: `data/checkin.db` (encrypted)
6. ✅ Backup exists: `data/backups/checkin.db.backup-TIMESTAMP`

---

## 📖 How It Works (Technical Details)

The automatic migration process is implemented in the Flask app startup:

1. **Detection Phase**:
   - Check if `DB_ENCRYPTION_KEY` and `FIELD_ENCRYPTION_KEY` are set
   - Connect to database and verify if it's encrypted
   - If already encrypted → skip migration and startup normally

2. **Backup Phase**:
   - Create `/data/backups/` directory if needed
   - Copy database to `checkin.db.backup-TIMESTAMP`
   - Verify backup integrity

3. **Migration Phase**:
   - Encrypt database using SQLCipher
   - Encrypt sensitive fields (phone, email, names, notes)
   - Update indexes for encrypted data
   - Verify all data is correctly encrypted

4. **Verification Phase**:
   - Test database connectivity with new encryption
   - Verify data integrity
   - Log success message to console and logs

5. **Startup Continuation**:
   - If migration succeeded → app continues normally
   - If migration failed → app exits with error (won't serve unencrypted data)
   - On restart, it tries migration again (important: keys must be valid)

---

## 📋 Pre-Update Checklist

Before updating, ensure you have:

- [ ] Full backup of your instance directory
- [ ] Database backup created
- [ ] Note of current SECRET_KEY and DEVELOPER_PASSWORD
- [ ] Time to run migration (30 minutes recommended)
- [ ] `openssl` and `python3` installed
- [ ] Know how to access Docker logs if needed
- [ ] Have the encryption keys written down somewhere safe
- [ ] Test environment (optional but recommended)

---

## 🔐 Security Best Practices

### Encryption Keys

- ✅ Store keys in `.env` (file mode 600)
- ✅ Keep `.env` out of Git (add to .gitignore)
- ✅ Backup keys separately from database
- ✅ Never share keys via email or chat
- ✅ Use a password manager to store keys
- ⚠️ Don't hardcode keys in docker-compose.yml
- ⚠️ Don't commit keys to Git
- ⚠️ Don't log keys in Docker output

### Backup Strategy

```bash
# Create encrypted backup of everything
tar czf youth-checkin-backup-$(date +%Y%m%d).tar.gz \
  data/ \
  .env \
  docker-compose.yml

# Store securely (encrypted drive, safe location)
```

### Testing in Staging

For important deployments:

```bash
# Test migration on a copy first
cp -r instance instance-test

cd instance-test

# Use test database
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DEVELOPER_PASSWORD=test-password
DB_ENCRYPTION_KEY=$(openssl rand -hex 32)
FIELD_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF

# Test migration
docker compose up -d
docker compose exec web python migrate_encrypt_database.py --confirm

# Verify
docker compose exec web python -c "from app import get_db; print('✓ OK')"

# If successful, apply same steps to production
```

---

## 📞 Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review Docker logs: `docker compose logs --tail 50`
3. Check `.env` file syntax
4. Verify encryption keys are in `.env`
5. See [SECURITY_ENCRYPTION.md](SECURITY_ENCRYPTION.md) for architecture details
6. See [ENCRYPTION_SETUP.md](ENCRYPTION_SETUP.md) for key generation help

---

## 📚 Related Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker deployment guide
- [SECURITY_ENCRYPTION.md](SECURITY_ENCRYPTION.md) - Encryption architecture
- [ENCRYPTION_SETUP.md](ENCRYPTION_SETUP.md) - Encryption key setup
- [README.md](README.md) - Project overview

---

**Last Updated:** Dec 30, 2025  
**Version:** 1.0  
**Applies to:** youth-secure-checkin v1.0.1+
