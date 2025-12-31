# YouthCheckIn - Docker Deployment Guide

## 🎯 What is YouthCheckIn?

YouthCheckIn is a **free, open-source check-in system** designed for youth organizations, churches, schools, and community groups. Parents quickly look up their family using the last 4 digits of their phone number, select their kids, and check them in with a single tap. Volunteers see real-time check-in status and checkout codes for accountability.

**Key Features:**
- ✅ **Free & Open Source** - MIT License, no subscriptions ever
- 🏠 **Self-Hosted** - Your data stays on your server (complete privacy)
- 🔒 **Enterprise Security** (v1.0.3+) - AES-256 encryption, rate limiting, account lockout
- ⚡ **Fast** - 10-second check-in process, minimal training needed
- 📱 **Mobile-Friendly** - Works great on phones, tablets, and desktops
- 🎨 **Customizable** - Your colors, logo, and terminology
- 📊 **Attendance Tracking** - History, reports, and export capabilities
- 🔄 **Calendar Integration** - Auto-syncs with Google Calendar or iCal

**Technology Stack:**
- **Backend**: Flask 3.1.1 (Python web framework)
- **Database**: SQLite with SQLCipher encryption (AES-256)
- **Frontend**: Bootstrap 5.3 + vanilla JavaScript
- **Deployment**: Docker + Docker Compose (one-command startup)

## 📖 This Deployment Guide

This guide walks you through deploying YouthCheckIn using Docker, which provides:
- ✅ **One-command startup** - `docker compose up -d`
- ✅ **No dependency conflicts** - Everything isolated in containers
- ✅ **Easy updates** - Pull new image and restart
- ✅ **Data persistence** - Your database and uploads survive container restarts
- ✅ **Multiple deployment options** - VPS, cloud, or local server

Whether you're trying the **demo first** or deploying to **production**, this guide has you covered.

---

## 📋 Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+
- 512 MB RAM minimum (1 GB recommended)
- 1 GB disk space

## 🚀 Quick Start

### Option 1: Pull from Docker Hub (Recommended)

```bash
# Pull the latest image
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Create docker-compose.yml
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.yml

# Generate encryption keys (required for v1.0.3+)
python -c "import secrets; print('DB_ENCRYPTION_KEY=' + secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Create .env file with your keys
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DEVELOPER_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
DB_ENCRYPTION_KEY=<paste-your-db-key-here>
FIELD_ENCRYPTION_KEY=<paste-your-field-key-here>
EOF

# Start the application
docker compose up -d
```

### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Generate encryption keys (required)
python -c "import secrets; print('DB_ENCRYPTION_KEY=' + secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Create .env file
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DEVELOPER_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
DB_ENCRYPTION_KEY=<your-key>
FIELD_ENCRYPTION_KEY=<your-key>
EOF

# Start application
docker compose up -d
```

### Access Application

Open your browser to: `http://localhost:5000`

The setup wizard will guide you through initial configuration:
1. Organization details and branding
2. Primary color scheme
3. Access code for check-in page
4. Admin password

## 🎭 Demo Mode

Want to try it with sample data first?

```bash
# Clone repository (required for demo)
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Run demo with pre-loaded data (no encryption keys needed for demo)
docker compose --profile demo up -d
```

**Demo credentials:**
- Check-in code: `demo123`
- Admin password: `demo123`
- Developer password: `demo2025`

**Test phone numbers:** 555-0101, 555-0102, 555-0103, 555-0104, etc.

**Demo features:**
- 8 pre-loaded families with kids
- 6 upcoming events
- Sample check-in history
- QR code checkout enabled
- Auto-resets every 24 hours

## 🔐 Encryption Keys (Required for Production)

**v1.0.3 and later require encryption keys for production use.**

### Generate Keys

**Option 1: Python**

```bash
# Database Encryption Key (64 hex characters)
python -c "import secrets; print('DB_ENCRYPTION_KEY=' + secrets.token_hex(32))"

# Field Encryption Key (44 base64 characters)
python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**Option 2: PowerShell (Windows)**

```powershell
# Database Encryption Key
$dbKey = -join ((0..9) + 'a'..'f' | Get-Random -Count 64)
Write-Host "DB_ENCRYPTION_KEY=$dbKey"

# Field Encryption Key (requires cryptography library)
python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### Store Keys Securely

Never commit `.env` to version control! It's already in `.gitignore`.

**Create `.env` file:**

```bash
SECRET_KEY=<your-secret-key-hex-64-chars>
DEVELOPER_PASSWORD=<your-secure-password>
DB_ENCRYPTION_KEY=<your-db-encryption-key-hex-64-chars>
FIELD_ENCRYPTION_KEY=<your-field-encryption-key-base64-44-chars>
```

## 🔧 Configuration Options

### Environment Variables

All variables in `.env` are required for production:

| Variable | Description | Length |
|----------|-------------|--------|
| `SECRET_KEY` | Flask session encryption key | 64 hex characters |
| `DEVELOPER_PASSWORD` | Emergency admin access | 16+ characters |
| `DB_ENCRYPTION_KEY` | Database-level AES-256 encryption | 64 hex characters |
| `FIELD_ENCRYPTION_KEY` | Field-level Fernet encryption | 44 base64 characters |

**Demo mode** uses hardcoded demo keys (no .env needed).

### Docker Compose Profiles

The `docker-compose.yml` uses profiles. Run without a profile for production:

```bash
# Production (default)
docker compose up -d

# Demo mode (with auto-reset)
docker compose --profile demo up -d

# Production with Nginx reverse proxy (optional)
docker compose --profile with-nginx up -d
```

### Customize Services

Edit `docker-compose.yml` to customize:

```yaml
services:
  web:
    image: mrcrunchybeans/youth-secure-checkin:latest
    container_name: youth-checkin
    ports:
      - "5000:5000"  # Change host port if needed
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
      - DB_ENCRYPTION_KEY=${DB_ENCRYPTION_KEY}
      - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY}
    volumes:
      - ./data:/app/data           # Database storage
      - ./uploads:/app/uploads     # Uploads (logos, etc)
    restart: unless-stopped
```

## 📁 Data Persistence

Data is stored in local directories (automatically created):

- **Database**: `./data/checkin.db` (encrypted SQLite database)
- **Uploads**: `./uploads/` (logos, favicons, custom branding images)

These directories persist between container restarts and updates.

### Backup Your Data

```bash
# Stop containers first (recommended)
docker compose down

# Backup everything
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/ .env

# Restart
docker compose up -d
```

**Or use the built-in backup feature:**
Admin Panel → Backups → Create Backup

### Restore from Backup

```bash
# Stop containers
docker compose down

# Extract backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart
docker compose up -d
```

**Or use Admin Panel → Backups → Restore from Backup**

## 🔐 Security Best Practices (v1.0.3+)

### Encryption Features

YouthCheckIn v1.0.3 includes enterprise-grade security:

- **SQLCipher**: AES-256 database-level encryption at rest
- **Fernet**: Field-level encryption for sensitive data (names, notes)
- **PBKDF2-SHA256**: Password hashing with automatic plaintext migration
- **Rate Limiting**: 5 attempts/minute prevents brute force attacks
- **Account Lockout**: 15-minute lockout after 5 failed attempts
- **HTTP Security Headers**: HSTS, CSP, X-Frame-Options, X-XSS-Protection

### Protect Your Secrets

1. **Never commit `.env` files** (already in .gitignore)
2. **Generate strong random keys** (see Encryption Keys section above)
3. **Use strong admin passwords** during initial setup wizard
4. **Keep images updated**:

```bash
docker compose pull
docker compose up -d
```

5. **Store encryption keys securely**:
   - Use secret management tools (Vault, AWS Secrets Manager, etc.)
   - Don't hardcode in scripts or config files
   - Rotate keys periodically

### SSL/TLS for Production

**Recommended Options:**

1. **Caddy** (easiest): Automatic Let's Encrypt certificates
2. **Cloudflare Tunnel**: Zero-config SSL + DDoS protection
3. **Nginx**: Use included Nginx profile for reverse proxy

```bash
# Configure nginx.conf and SSL certificates first
docker compose --profile with-nginx up -d
```

See `DEPLOYMENT_CHECKLIST.md` for detailed production hosting guides.

## 🛠️ Management Commands

### View Logs

```bash
# View recent logs
docker compose logs

# Follow logs (live updates)
docker compose logs -f

# Last 50 lines
docker compose logs --tail=50

# Specific service
docker compose logs web
```

### Restart Application

```bash
# Quick restart (keeps all data)
docker compose restart

# Full restart
docker compose down
docker compose up -d
```

### Update to Latest Version

```bash
# Pull new images from Docker Hub
docker compose pull

# Recreate containers with new image
docker compose up -d

# Verify update
docker compose ps
docker compose exec web python -c "from app import APP_VERSION; print(f'Version: {APP_VERSION}')"
```

### Stop Application

```bash
# Stop containers (all data is safe in ./data and ./uploads)
docker compose down

# ⚠️ Delete everything including volumes (use with caution)
docker compose down -v
```

### Shell Access (Debugging)

```bash
# Access running container
docker compose exec web /bin/sh

# Check database (if encrypted, SQLCipher is required)
docker compose exec web sqlite3 data/checkin.db ".tables"

# View Python version
docker compose exec web python --version

# Check application files
docker compose exec web ls -la /app/
```

## 📊 Monitoring

### Check Status

```bash
# View running containers
docker compose ps

# View resource usage
docker stats --no-stream

# Check health status
docker inspect --format='{{.State.Health.Status}}' youth-checkin
```

### Health Checks

```bash
# Test application response
curl http://localhost:5000

# Check health endpoint
curl http://localhost:5000/health
```

## 🔍 Troubleshooting

### Encryption Keys Not Set

**Error:** `FIELD_ENCRYPTION_KEY not set in environment`

**Solution:** Generate and add keys to `.env`:

```bash
python -c "import secrets; print('DB_ENCRYPTION_KEY=' + secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

Then restart: `docker compose up -d`

### Port Already in Use

**Windows PowerShell:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```

**Or change port in docker-compose.yml:**
```yaml
ports:
  - "5001:5000"  # Use 5001 instead
```

### Container Won't Start

```bash
# View detailed logs
docker compose logs web

# Check configuration
docker compose config

# Verify .env file exists and is valid
cat .env

# Recreate containers
docker compose down
docker compose up -d --force-recreate
```

### Can't Pull Docker Image

```bash
# Test Docker Hub connection
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Login if needed
docker login

# Check Docker daemon is running
docker ps
```

### Database Issues

```bash
# Stop containers
docker compose down

# Backup current database
cp data/checkin.db data/checkin.db.backup-$(date +%Y%m%d)

# Option 1: Let app recreate database
rm data/checkin.db
docker compose up -d

# Option 2: Restore from Admin Panel backup
docker compose up -d
# Then use Admin Panel → Backups → Restore
```

### Volume/Permission Issues

```bash
# Fix permissions (Linux/Mac)
sudo chown -R $(id -u):$(id -g) data/ uploads/
chmod -R 755 data/ uploads/

# Recreate volumes if corrupted
docker compose down -v
docker compose up -d
```

### Clean Up Disk Space

```bash
# Remove unused containers and images
docker system prune -a

# Remove specific stopped containers
docker compose down
docker container prune

# Check disk usage
docker system df
```

## 🚀 Advanced Configuration

### Change Port

Edit `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "8080:5000"  # External:Internal (container always uses 5000)
```

Then access at `http://localhost:8080`

### Resource Limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          memory: 256M
```

### Multiple Instances

Run multiple isolated instances with separate encryption keys:

```yaml
# docker-compose.troop123.yml
services:
  web:
    container_name: youth-checkin-troop123
    ports:
      - "5001:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY_TROOP123}
      - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD_TROOP123}
      - DB_ENCRYPTION_KEY=${DB_ENCRYPTION_KEY_TROOP123}
      - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY_TROOP123}
    volumes:
      - ./data-troop123:/app/data
      - ./uploads-troop123:/app/uploads
```

Start with:
```bash
docker compose -f docker-compose.troop123.yml up -d
```

### Performance Tuning

Gunicorn workers (formula: CPU cores × 2 + 1):

```yaml
command: gunicorn --bind 0.0.0.0:5000 --workers 5 --timeout 120 --max-requests 1000 wsgi:app
```

## 🌐 Production Deployment

### Pre-Deployment Checklist

Before going live:

- [ ] Generate strong `SECRET_KEY` (64 hex characters)
- [ ] Generate strong `DB_ENCRYPTION_KEY` (64 hex characters)
- [ ] Generate strong `FIELD_ENCRYPTION_KEY` (44 base64 characters)
- [ ] Set secure `DEVELOPER_PASSWORD` (16+ characters)
- [ ] Set strong admin password during setup wizard
- [ ] Configure SSL/HTTPS (Caddy/Cloudflare/Nginx)
- [ ] Set up automated backups
- [ ] Test backup restoration
- [ ] Configure custom branding (Admin Panel → Branding)
- [ ] Review and test all features
- [ ] Set up monitoring/alerts
- [ ] Document your deployment

### Hosting Options

Compatible with any Docker-capable host:

**VPS Providers:**
- DigitalOcean (Droplets)
- Linode
- Vultr
- Hetzner

**Cloud Platforms:**
- AWS (ECS, Lightsail)
- Google Cloud (Cloud Run, Compute Engine)
- Azure (Container Instances, App Service)

**Platform-as-a-Service:**
- Railway.app
- Render.com
- Fly.io

See `DEPLOYMENT_CHECKLIST.md` for platform-specific guides.

### Automated Backups

**Cron job (Linux):**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/youth-secure-checkin && docker compose down && tar -czf ~/backups/checkin-$(date +\%Y\%m\%d-\%H\%M).tar.gz data/ uploads/ .env && docker compose up -d
```

**Windows Task Scheduler:**

Create PowerShell script `backup.ps1`:
```powershell
cd C:\youth-secure-checkin
docker compose down
tar -czf "C:\backups\checkin-$(Get-Date -Format 'yyyyMMdd-HHmm').tar.gz" data, uploads
docker compose up -d
```

Schedule via Task Scheduler to run daily.

### Log Rotation

Create `/etc/logrotate.d/docker-youth-checkin`:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    maxsize 10M
    missingok
    delaycompress
    copytruncate
}
```

## 🐋 Docker Commands Reference

### Images

```bash
# Pull image
docker pull mrcrunchybeans/youth-secure-checkin:latest

# List images
docker images

# Remove image
docker rmi mrcrunchybeans/youth-secure-checkin:latest

# Build from Dockerfile
docker build -t youth-checkin .
```

### Containers

```bash
# Start production
docker compose up -d

# Start demo
docker compose --profile demo up -d

# Stop
docker compose down

# Restart
docker compose restart

# View logs
docker compose logs -f

# Execute command
docker compose exec web /bin/sh
```

### Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect youth-secure-checkin_data

# Remove unused volumes
docker volume prune
```

### Networks

```bash
# List networks
docker network ls

# Inspect network
docker network inspect youth-secure-checkin_checkin-network
```

## 📚 Quick Reference

### Common Commands

```bash
# Start production (requires .env with encryption keys)
docker compose up -d

# Start demo (no .env needed)
docker compose --profile demo up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Update
docker compose pull && docker compose up -d

# Backup
docker compose down && tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/ .env && docker compose up -d

# Shell access
docker compose exec web /bin/sh

# Check version
docker compose exec web python -c "from app import APP_VERSION; print(APP_VERSION)"
```

### File Locations

**In Container:**
- Application: `/app/`
- Database: `/app/data/checkin.db` (encrypted)
- Uploads: `/app/uploads/`
- Logs: stdout (view with `docker compose logs`)

**On Host:**
- Database: `./data/checkin.db`
- Uploads: `./uploads/`
- Configuration: `.env` (with encryption keys)
- Compose: `docker-compose.yml`

### Ports

- **5000**: Application (default, mapped from host)
- **80/443**: Nginx (if using with-nginx profile)

Change host port in docker-compose.yml: `"<host-port>:5000"`

## 🔒 Security Notes (v1.0.3+)

- **Encryption is mandatory**: DB_ENCRYPTION_KEY and FIELD_ENCRYPTION_KEY are required
- **Automatic migration**: Plaintext passwords are automatically hashed to PBKDF2-SHA256 on first run
- **Rate limiting**: 5 login attempts per minute per IP address
- **Account lockout**: 15-minute lockout after 5 failed admin login attempts
- **HTTP headers**: HSTS, CSP, X-Frame-Options, X-XSS-Protection configured automatically
- **Database encryption**: SQLCipher AES-256 encrypts the entire database at rest
- **Field encryption**: Sensitive fields use Fernet encryption for defense-in-depth

## 🆘 Need Help?

- **Application Guide**: See `README.md` for features and usage
- **Deployment Guide**: See `DEPLOYMENT_CHECKLIST.md` for hosting platforms
- **Security Guide**: See `SECURITY.md` for best practices
- **Encryption Details**: See `DOCKER_ENCRYPTION_QUICK_REF.md` for key generation
- **Issues**: [GitHub Issues](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)
- **Docker Docs**: [docs.docker.com](https://docs.docker.com/)
- **Docker Compose**: [docs.docker.com/compose](https://docs.docker.com/compose/)

## 📝 Notes

- Docker Compose V2 uses `docker compose` (no hyphen), V1 uses `docker-compose`
- Always stop containers before backing up database files
- Demo mode auto-resets every 24 hours and should not be used for production
- Production uses local directories for data persistence
- The application runs on port 5000 inside the container (not configurable)
- Health checks run every 30 seconds with 3 retries
- Default worker count is 3 for production, 2 for demo
- **v1.0.3+**: Encryption keys are required for production deployments
