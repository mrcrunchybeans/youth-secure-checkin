# Youth Secure Check-In v1.0.1 Release Notes

**Release Date:** December 30, 2025

## 🔐 Automatic Encryption Migration (NEW)

### Major Feature: Seamless Database Encryption on Update

When users update from v1.0.0 to v1.0.1+, encryption migration happens **completely automatically on startup**. No manual intervention required.

**What's encrypted:**
- Database at rest (AES-256 SQLCipher)
- Sensitive fields: phone numbers, email addresses, names, and notes (Fernet encryption)

**How it works:**
1. User pulls new Docker image and adds encryption keys to `.env`
2. User restarts container: `docker compose down && docker compose up -d`
3. App detects unencrypted database + encryption keys set
4. Automatic migration runs silently on startup
5. Backup created: `data/backups/checkin.db.backup-TIMESTAMP`
6. Database fully encrypted and app continues normally

**Key benefits:**
- ✅ Zero manual migration steps needed
- ✅ Automatic backup before encryption
- ✅ Clear logging of migration progress
- ✅ Option to use manual migration if preferred
- ✅ Easy rollback from backup if needed
- ✅ Completely transparent to users

**For users:** Just update, add keys, and restart. That's it!

**Documentation:**
- See [DOCKER_ENCRYPTION_MIGRATION.md](DOCKER_ENCRYPTION_MIGRATION.md) for complete guide
- See [DOCKER_ENCRYPTION_QUICK_REF.md](DOCKER_ENCRYPTION_QUICK_REF.md) for quick reference
- See [ENCRYPTION_SETUP.md](ENCRYPTION_SETUP.md) for key generation help

---

## 🎨 User Experience Improvements

### Improved Add/Edit Family Pages

**Problem solved:** The confusing "Group/Troop" field was causing users to enter last names instead of group information, making the form unclear.

**What changed:**
- ✅ Removed confusing "Group/Troop" field (kept hidden for backwards compatibility)
- ✅ Reorganized form with clear card-based sections:
  - **Authorization Settings** - Who can pick up the child
  - **Adults in Household** - Family members (for check-in)
  - **Children in Family** - Kids being checked in
- ✅ Improved labels with real-world examples:
  - "Name (e.g., John Smith)" instead of "Adult name"
  - "Child's name (e.g., Sarah Smith)" instead of "Kid name"
  - "Phone number (e.g., 555-123-4567)" with format example
- ✅ Added helpful context and tooltips:
  - "The name and phone are used for check-in and family lookup"
  - "Notes are visible during check-in to alert staff of any special considerations"
  - "List the names of all adults who are allowed to pick up the child(ren)"
- ✅ Better visual hierarchy with card-based layout
- ✅ Improved button text clarity ("+ Add Another Adult" vs "Add Adult")
- ✅ More intuitive spacing and grouping of related fields
- ✅ Data entry tips alert at the top of the form

**Impact:**
- Clearer data entry process for new users
- Reduced confusion about what information is required
- Better understanding of how data is used at check-in
- More professional appearance with organized sections

---

## 🔧 Technical Details

### Code Changes

**app.py**
- Added `auto_migrate_encryption()` function that:
  - Runs on Flask app startup automatically
  - Detects unencrypted database with encryption keys set
  - Creates automatic backup before migration
  - Calls migration silently (no user prompts)
  - Logs progress for visibility
  - Handles errors gracefully without crashing the app

**migrate_encrypt_database.py**
- Added `auto_mode` parameter to `migrate_database()` function
- When `auto_mode=True`: silent operation, no prompts
- When `auto_mode=False` (default): interactive mode with prompts
- Same core encryption logic works in both modes

**Templates**
- `templates/admin/add_family.html` - Redesigned for clarity
- `templates/admin/edit_family.html` - Consistent with add page
- Updated JavaScript for dynamic field addition

**Documentation**
- DOCKER_ENCRYPTION_MIGRATION.md - Complete migration guide
- DOCKER_ENCRYPTION_QUICK_REF.md - Quick reference
- DOCKER_UPDATE_CHECKLIST.md - Implementation checklist
- ENCRYPTION_SETUP.md - Key generation guide
- SECURITY_ENCRYPTION.md - Architecture details

---

## 📋 What You Need to Do

### For Existing Users (v1.0.0 → v1.0.1)

**Migration is automatic!** Just:

```bash
# 1. Add encryption keys to .env
DB_ENCRYPTION_KEY=$(openssl rand -hex 32)
FIELD_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "DB_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY" >> .env
echo "FIELD_ENCRYPTION_KEY=$FIELD_ENCRYPTION_KEY" >> .env

# 2. Pull and restart
docker compose pull
docker compose down
docker compose up -d

# 3. Watch the logs (optional)
docker compose logs -f
# You'll see: "Encryption migration: Completed successfully"
```

Done! Your database is now encrypted.

### For New Users

New deployments include encryption from the start. See [QUICKSTART.md](QUICKSTART.md) for setup instructions.

---

## 🛡️ Security

**Encryption keys:**
- Generate unique keys per instance: `openssl rand -hex 32`
- Store in `.env` (never commit to Git)
- Keep backups in a safe location
- Use a password manager to store keys

**Backups:**
- Created automatically before encryption
- Located in `data/backups/checkin.db.backup-TIMESTAMP`
- Keep secure - they contain unencrypted data temporarily
- Safe to delete after 30 days of stable operation

**Backwards Compatibility:**
- Old unencrypted databases still work
- Migration is non-destructive - original backed up first
- Can rollback by restoring from backup
- Existing encrypted databases are detected and skipped

---

## 📚 Documentation

All documentation has been updated to reflect the new features:

- **README.md** - Quick start with encryption note
- **DOCKER.md** - Docker deployment with encryption
- **DOCKER_ENCRYPTION_MIGRATION.md** - Complete migration guide (NEW)
- **DOCKER_ENCRYPTION_QUICK_REF.md** - Quick reference (NEW)
- **ENCRYPTION_SETUP.md** - Key generation (NEW)
- **SECURITY_ENCRYPTION.md** - Security architecture (NEW)

---

## ✅ Testing

### What to Test

1. **Add Family Form**
   - Clear sections for Authorization, Adults, Children
   - Helpful placeholders and examples
   - "Add Another" buttons work correctly
   - Form submits without the troop field

2. **Edit Family Form**
   - Loads existing data correctly
   - Updates save properly
   - Can add/remove adults and children
   - Layout matches add form

3. **Automatic Encryption Migration**
   - Pull new Docker image v1.0.1
   - Add encryption keys to .env
   - Restart container
   - Watch logs for migration messages
   - Verify backup created in data/backups/
   - Confirm app works normally after migration

4. **Manual Migration (Optional)**
   - Set `SKIP_AUTO_ENCRYPTION=1` environment variable
   - Start container without auto-migration
   - Run manual migration when ready
   - Verify same result as automatic

---

## 🐛 Bug Fixes

- N/A (all new features in this release)

---

## ⚠️ Breaking Changes

**None!** This release is fully backward compatible.

- Old unencrypted databases continue to work
- Migration to encrypted is automatic and transparent
- Existing forms still accept data the same way
- Hidden `troop` field maintains data compatibility

---

## 📦 Dependencies

No new dependencies added:
- `cryptography` - Already required for Fernet
- `sqlcipher3` - Already required for database encryption
- All other libraries unchanged

---

## 🚀 Upgrading

### From v1.0.0

```bash
# Pull latest image
docker compose pull

# Add encryption keys to .env (see above)

# Restart
docker compose down
docker compose up -d

# That's it! Migration happens automatically.
```

### From earlier versions

Same process. See [DOCKER_ENCRYPTION_MIGRATION.md](DOCKER_ENCRYPTION_MIGRATION.md) for detailed instructions.

---

## 📞 Support

**Questions about encryption?**
- See [DOCKER_ENCRYPTION_MIGRATION.md](DOCKER_ENCRYPTION_MIGRATION.md) - Complete guide with troubleshooting
- See [DOCKER_ENCRYPTION_QUICK_REF.md](DOCKER_ENCRYPTION_QUICK_REF.md) - Common commands

**Questions about the new family form?**
- Check placeholder text and helpful hints in the form
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development help

**Need to rollback?**
- Restore from backup: `cp data/backups/checkin.db.backup-* data/checkin.db`
- Restart container: `docker compose up -d`

---

## 📈 What's Next

- Performance optimizations for encrypted data queries
- Additional encryption options (local vs cloud backups)
- Two-factor authentication for admin access
- Audit logging for security events

---

## 🎉 Thank You

Thanks to all users for the feedback that led to these improvements!

**v1.0.1 Highlights:**
- ✨ Automatic encryption migration
- 🎨 Improved family data entry experience
- 🔒 Full database and field encryption
- 📚 Comprehensive documentation

---

**Version:** 1.0.1  
**Release Date:** December 30, 2025  
**Status:** Stable  
**Compatibility:** Docker, Bare Metal  
**License:** See LICENSE file
