# Docker Encryption Quick Reference

## 🚀 New Docker Installation (Encryption Included)

```bash
# 1. Create instance directory
mkdir youth-checkin && cd youth-checkin
mkdir -p data uploads

# 2. Download docker-compose.yml
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.yml

# 3. Create .env with encryption keys
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DEVELOPER_PASSWORD=your-secure-password-here
DB_ENCRYPTION_KEY=$(openssl rand -hex 32)
FIELD_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF

# 4. Start (database initializes encrypted)
docker compose up -d

# 5. Verify
docker compose logs | grep -i "database initialized"
curl http://localhost:5000/health
```

✅ **Done!** Your instance is encrypted from the start.

---

## 🔄 Updating Existing Installation (v1.0.0 → v1.0.1+)

**🎉 Migration is automatic - no manual steps needed!**

```bash
# 1. Backup (just to be safe)
cp -r data data.backup-$(date +%Y%m%d)

# 2. Add encryption keys to .env
DB_ENCRYPTION_KEY=$(openssl rand -hex 32)
FIELD_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "DB_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY" >> .env
echo "FIELD_ENCRYPTION_KEY=$FIELD_ENCRYPTION_KEY" >> .env

# 3. Pull latest image and restart
docker compose pull
docker compose down
```

✅ **Done!** The app automatically migrated your data to encrypted on startup.

### If You Prefer Manual Control

If you want to manually trigger migration instead:

```bash
# Set skip flag
export SKIP_AUTO_ENCRYPTION=1
docker compose up -d

# Then manually run migration when ready
docker compose exec web python migrate_encrypt_database.py
```

---

## 🛠️ Common Commands

```bash
# View logs
docker compose logs -f

# Check health
curl http://localhost:5000/health

# View database stats
docker compose exec web python -c "
from app import get_db
db = get_db()
print(f'Kids: {db.execute(\"SELECT COUNT(*) FROM kids\").fetchone()[0]}')
"

# Stop instance
docker compose stop

# Start instance
docker compose start

# Full restart
docker compose restart

# Delete everything (careful!)
docker compose down -v
```

---

## ⚠️ Key Safety

```bash
# ✅ DO
- Store .env in a safe location
- Make .env readable only by you: chmod 600 .env
- Back up encryption keys separately
- Use unique keys for each instance

# ❌ DON'T
- Commit .env to Git
- Share keys via email or chat
- Mix keys between instances
- Reuse keys from different backups
```

---

## 🚨 If Something Goes Wrong

```bash
# Restore from backup
docker compose stop
rm -r data
cp -r data.backup-* data
docker compose up -d

# Or: Use old image (remove encryption keys from .env first)
# Edit docker-compose.yml and change:
# image: mrcrunchybeans/youth-secure-checkin:v1.0.0
```

---

**For detailed help:** See [DOCKER_ENCRYPTION_MIGRATION.md](DOCKER_ENCRYPTION_MIGRATION.md)
