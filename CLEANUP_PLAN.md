# Repository Cleanup Plan

## Files to Remove from Public GitHub

### 🗑️ Test & Debug Scripts (24 files)
These are development/testing tools not needed by users:

- `test_env.py` - Environment testing
- `check_db.py` - Database inspection tool
- `check_route.py` - Route testing
- `add_override_setting.py` - Old setup script
- `tests/test_app.py` - Unit tests (incomplete)

### 🗑️ Old Migration Scripts (7 files)
Already applied, users don't need these:

- `migrate_add_authorized_adults.py`
- `migrate_add_checkout_code.py`
- `migrate_add_default_adult.py`
- `migrate_add_kid_notes.py`
- `migrate_add_label_settings.py`
- `migrate_add_share_tokens.py`
- `migrate_to_configurable.py`

### 🗑️ Old Rename/Replace Scripts (2 files)
Used for project rename, no longer needed:

- `replace_colors.py`
- `replace_troop.py`

### 🗑️ Outdated Documentation (5 files)
Information now consolidated elsewhere:

- `RENAME_INSTRUCTIONS.md` - Project already renamed
- `MIGRATION_DEFAULT_ADULT.md` - Old migration docs
- `HOSTINGER_DEPLOYMENT.md` - Replaced by DOCKER.md
- `FEATURE_KID_NOTES.md` - Now in main docs
- `EXPORT_FEATURES.md` - Now in main docs
- `LABEL_PRINTING_FEATURE.md` - Now in main docs

### 🗑️ Personal Config Files (1 file)
IDE-specific, not useful to others:

- `troop_checkin.code-workspace` - VS Code workspace file

---

## ✅ Files to Keep

### Core Application
- `app.py` - Main application
- `wsgi.py` - Production server entry
- `schema.sql` - Database schema
- `requirements.txt` - Python dependencies
- `requirements_label_printing.txt` - Optional printer support
- `__init__.py` - Package marker
- `Procfile` - Deployment config

### Utility Scripts (Keep - Users Need These)
- `label_printer.py` - Label printing functionality
- `mark_setup_complete.py` - Setup helper
- `cleanup_orphaned_checkins.py` - Database maintenance
- `clear_checkin_history.py` - Data cleanup
- `reset_checkin_ids.py` - ID reset utility

### Docker Files
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

### Documentation
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `SECURITY.md`
- `DEPLOYMENT.md`
- `DOCKER.md`
- `DOCKER_QUICK_START.md`
- `DOCKER_TESTING.md`
- `docs/FAQ.md`
- `docs/WIKI.md`

### Templates & Static Files
- All `templates/` files
- All `static/` files

### Configuration Examples
- `.env.example`
- `.env.docker`
- `.gitignore`

---

## Summary

**Remove from GitHub:** 24 files (old tests, migrations, outdated docs)
**Keep:** All production code, utilities users need, and current documentation

---

## Run the Cleanup

Execute the cleanup script:

```powershell
.\cleanup-repo.ps1
```

This will:
1. Remove files from git tracking
2. Keep files locally (for your reference)
3. Update `.gitignore` to prevent re-adding
4. Show you what changed

Then commit and push:

```powershell
git add .
git commit -m "Clean up old test and migration files"
git push
```
