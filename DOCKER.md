# YouthCheckIn - Docker Deployment Guide

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

# Create docker-compose.yml or download it
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.yml

# Start the production service
docker compose --profile production up -d
```

### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Start with docker compose (uses profile)
docker compose --profile production up -d
```

### Access Application

**Youth Check-in:** `http://localhost:5000`
**YOURLS (URL Shortener):** `http://localhost:8080/admin`

The setup wizard will guide you through initial configuration:
1. Organization details and branding
2. Primary color scheme
3. Access code for check-in page
4. Admin password

**Services started:**
- Youth Secure Check-in (port 5000)
- YOURLS URL Shortener (port 8080)
- MySQL database for YOURLS

## 🎭 Demo Mode

Want to try it with sample data first?

```bash
# Pull demo image
docker pull mrcrunchybeans/youth-secure-checkin:demo

# Download demo compose file
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.demo.yml

# Run demo with pre-loaded data
docker compose -f docker-compose.demo.yml up -d
```

**Demo credentials:**
- Check-in code: `demo123`
- Admin password: `demo123`
- Developer password: `demo2025`

**Test phone numbers:** 555-0101, 555-0102, 555-0103, 555-0104, etc.

**Demo features:**
- 8 pre-loaded families with kids
- 8 upcoming events
- Sample check-in history
- QR code checkout enabled
- Auto-resets every 24 hours

## 🔗 URL Shortener (YOURLS)

YOURLS creates short URLs for checkout QR codes, making them easier to scan and type.

**Included automatically** in both production and demo modes! 

- Access: http://localhost:8080/admin
- Default credentials: `admin` / `admin`

**Setup steps:**
1. Visit http://localhost:8080/admin and click "Install YOURLS"
2. Go to Tools → API and copy your signature token
3. In Youth Check-in: Admin → Security → URL Shortener
4. Enter API URL: `http://yourls/yourls-api.php`
5. Paste your signature token and save

**See `YOURLS_SETUP.md` for detailed setup and bare-metal installation.**

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file for production secrets:

```bash
# Generate secure keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DEVELOPER_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
YOURLS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(12))")

# Create .env file
cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}

# YOURLS Configuration
YOURLS_DB_PASSWORD=${YOURLS_PASSWORD}
YOURLS_DB_ROOT_PASSWORD=${YOURLS_PASSWORD}
YOURLS_USER=admin
YOURLS_PASSWORD=change_this_password
EOF
```

**Important:** Never commit `.env` to version control! It's already in `.gitignore`.

### Docker Compose Configuration

The main `docker-compose.yml` uses profiles. Available profiles:

- **production** - Production web service (default recommended)
- **demo** - Demo mode with sample data and auto-reset
- **with-nginx** - Nginx reverse proxy with SSL support

Edit `docker-compose.yml` to customize production service:

```yaml
services:
  web:
    build: .
    container_name: youth-checkin
    ports:
      - "5000:5000"  # Change port mapping if needed
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
    volumes:
      - ./data:/app/data           # Database storage
      - ./uploads:/app/uploads     # Logo/favicon uploads
    restart: unless-stopped
    profiles:
      - production
```

## 📁 Data Persistence

Data is stored in local directories (automatically created):

- **Database**: `./data/checkin.db` (SQLite database)
- **Uploads**: `./uploads/` (logos, favicons, custom branding images)

**Note:** Volume paths differ between production and demo:
- Production: `./uploads` → `/app/uploads`
- Demo: Docker volumes `demo-uploads` → `/app/static/uploads`

These directories persist between container restarts and updates.

### Backup Your Data

```bash
# Stop containers first (recommended)
docker compose --profile production down

# Backup everything
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/

# Restart
docker compose --profile production up -d
```

**Or use the built-in backup feature:**
Admin Panel → Backups → Create Backup

### Restore from Backup

```bash
# Stop containers
docker compose --profile production down

# Extract backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart
docker compose --profile production up -d
```

**Or use Admin Panel → Backups → Restore from Backup**

## 🔐 Security Best Practices

### Protect Your Secrets

1. **Never commit `.env` files** (already in .gitignore)
2. **Generate strong random secrets**:

```powershell
# PowerShell (Windows)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

```bash
# Bash (Linux/Mac)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

3. **Use strong admin passwords** during initial setup
4. **Keep images updated**:

```bash
docker compose pull
docker compose --profile production up -d
```

### SSL/TLS for Production

**Recommended Options:**

1. **Caddy** (easiest): Automatic Let's Encrypt certificates
2. **Cloudflare Tunnel**: Zero-config SSL + DDoS protection  
3. **Nginx/Traefik**: Manual SSL setup
4. **Built-in Nginx profile**:

```bash
# Set up nginx.conf and SSL certificates first
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
# Quick restart (keeps data)
docker compose restart

# Full restart
docker compose down
docker compose --profile production up -d
```

### Update to Latest Version

```bash
# Pull new images from Docker Hub
docker compose pull

# Recreate containers with new image
docker compose --profile production up -d

# Verify update
docker compose ps
docker compose exec web python -c "from app import APP_VERSION; print(f'Version: {APP_VERSION}')"
```

### Stop Application

```bash
# Stop containers (data is safe)
docker compose down

# ⚠️ Delete everything including volumes
docker compose down -v
```

### Shell Access (Debugging)

```bash
# Access running container
docker compose exec web /bin/sh

# Check database
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

### Port Already in Use

**Windows PowerShell:**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (use PID from above)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find process
sudo lsof -i :5000

# Kill process
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

# Verify .env file exists
cat .env

# Recreate containers
docker compose down
docker compose --profile production up -d --force-recreate
```

### Can't Pull Docker Image

```bash
# Test Docker Hub connection
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Login if needed (for private images)
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
docker compose --profile production up -d

# Option 2: Restore from Admin Panel backup
docker compose --profile production up -d
# Then use Admin Panel → Backups → Restore
```

### Volume/Permission Issues

```bash
# Fix permissions (Linux/Mac)
sudo chown -R $(id -u):$(id -g) data/ uploads/
chmod -R 755 data/ uploads/

# Recreate volumes if corrupted
docker compose down -v
docker compose --profile production up -d
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

Run multiple isolated instances:

```yaml
# docker-compose.troop123.yml
services:
  web:
    container_name: youth-checkin-troop123
    ports:
      - "5001:5000"
    volumes:
      - ./data-troop123:/app/data
      - ./uploads-troop123:/app/uploads
```

Start with:
```bash
docker compose -f docker-compose.troop123.yml --profile production up -d
```

### Performance Tuning

Add to `.env`:

```bash
# Number of Gunicorn workers (formula: CPU cores * 2 + 1)
GUNICORN_WORKERS=5

# Worker timeout (seconds)
GUNICORN_TIMEOUT=120

# Max requests per worker (memory leak protection)
GUNICORN_MAX_REQUESTS=1000
```

Update Dockerfile CMD or compose command:
```yaml
command: gunicorn --bind 0.0.0.0:5000 --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-120} --max-requests ${GUNICORN_MAX_REQUESTS:-1000} wsgi:app
```

## 🌐 Production Deployment

### Quick Checklist

Before going live:

- [ ] Generate strong `SECRET_KEY` in `.env`
- [ ] Set secure `DEVELOPER_PASSWORD` in `.env`
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
0 2 * * * cd /path/to/youth-secure-checkin && docker compose down && tar -czf ~/backups/checkin-$(date +\%Y\%m\%d-\%H\%M).tar.gz data/ uploads/ && docker compose --profile production up -d
```

**Windows Task Scheduler:**

Create PowerShell script `backup.ps1`:
```powershell
cd C:\youth-secure-checkin
docker compose down
tar -czf "C:\backups\checkin-$(Get-Date -Format 'yyyyMMdd-HHmm').tar.gz" data, uploads
docker compose --profile production up -d
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
docker pull mrcrunchybeans/youth-secure-checkin:demo

# List images
docker images

# Remove image
docker rmi mrcrunchybeans/youth-secure-checkin:latest

# Build from Dockerfile
docker build -t youth-checkin .
```

### Containers

```bash
# Start
docker compose --profile production up -d

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
# Start production
docker compose --profile production up -d

# Start demo
docker compose -f docker-compose.demo.yml up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Update
docker compose pull && docker compose --profile production up -d

# Backup
docker compose down && tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/ && docker compose --profile production up -d

# Shell access
docker compose exec web /bin/sh

# Check version
docker compose exec web python -c "from app import APP_VERSION; print(APP_VERSION)"
```

### File Locations

**In Container:**
- Application: `/app/`
- Database: `/app/data/checkin.db`
- Uploads: `/app/uploads/` (production) or `/app/static/uploads/` (demo)
- Logs: stdout (view with `docker compose logs`)

**On Host:**
- Database: `./data/checkin.db`
- Uploads: `./uploads/`
- Configuration: `.env`
- Compose: `docker-compose.yml` or `docker-compose.demo.yml`

### Ports

- **5000**: Application (default, mapped from host to container)
- **80/443**: Nginx (if using with-nginx profile)

Change host port in docker-compose.yml: `"<host-port>:5000"`

## 🆘 Need Help?

- **Application Guide**: See `README.md` for features and usage
- **Deployment Guide**: See `DEPLOYMENT_CHECKLIST.md` for hosting platforms  
- **Security Guide**: See `SECURITY.md` for best practices
- **Issues**: [GitHub Issues](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)
- **Docker Docs**: [docs.docker.com](https://docs.docker.com/)
- **Docker Compose**: [docs.docker.com/compose](https://docs.docker.com/compose/)

## 📝 Notes

- Docker Compose V2 uses `docker compose` (no hyphen), V1 uses `docker-compose`
- Always stop containers before backing up database files
- Demo mode auto-resets every 24 hours and should not be used for production
- Production uses local directories; demo uses named Docker volumes
- The application runs on port 5000 inside the container (not configurable)
- Health checks run every 30 seconds with 3 retries
- Default worker count is 3 for production, 2 for demo
