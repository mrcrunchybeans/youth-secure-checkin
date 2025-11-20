# YouthCheckIn - Docker Deployment Guide

This guide explains how to deploy YouthCheckIn using Docker containers.

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

# Start the application
docker-compose up -d
```

### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Start with docker-compose
docker-compose up -d
```

### Access Application

Open your browser to: `http://localhost:5000`

The setup wizard will guide you through initial configuration:
1. Organization details and branding
2. Primary color scheme
3. Access code for check-in page
4. Event settings (calendar integration)

## 🎭 Demo Mode

Want to try it with sample data first?

```bash
# Pull demo image
docker pull mrcrunchybeans/youth-secure-checkin:demo

# Run demo with pre-loaded data
docker-compose -f docker-compose.demo.yml up -d
```

**Demo credentials:**
- Check-in code: `demo123`
- Admin password: `demo123`
- Developer password: `demo2025`

**Test phone numbers:** 555-0101, 555-0102, 555-0103, etc.

Demo data auto-resets every 24 hours.

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file for production secrets:

```bash
# Generate secure keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DEVELOPER_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

# Create .env file
cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
EOF
```

**Important:** Never commit `.env` to version control! It's already in `.gitignore`.

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

```yaml
version: '3.8'
services:
  web:
    image: mrcrunchybeans/youth-secure-checkin:latest
    container_name: youth-checkin
    ports:
      - "5000:5000"  # Change port here if needed
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./uploads:/app/static/uploads
    restart: unless-stopped
```

## 📁 Data Persistence

Data is stored in local directories (automatically created):

- **Database**: `./data/checkin.db` (SQLite database)
- **Uploads**: `./uploads/` (logos, favicons, custom branding)

These directories persist between container restarts and updates.

### Backup Your Data

```bash
# Quick backup (recommended)
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
docker-compose up -d

# Or use the built-in export feature:
# Admin Panel → Utilities → Export Data
```

### Restore from Backup

```bash
# Stop containers
docker-compose down

# Extract backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart
docker-compose up -d

# Or use Admin Panel → Utilities → Restore from Backup
```

## 🔐 Security Best Practices

### Protect Your Secrets

1. **Never commit `.env` files** (already in .gitignore)
2. **Generate strong random secrets**:

```powershell
# Generate SECRET_KEY (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

```bash
# Or use Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

3. **Use strong admin passwords** during initial setup
4. **Keep images updated**:

```bash
docker-compose pull
docker-compose up -d
```

### SSL/TLS for Production

**Recommended Options:**

1. **Caddy** (easiest): Automatic Let's Encrypt certificates
2. **Cloudflare Tunnel**: Zero-config SSL + DDoS protection  
3. **Nginx/Traefik**: Manual SSL setup

See `DEPLOYMENT_CHECKLIST.md` for detailed production hosting guides
   ```

4. **Start with Nginx**:
   ```bash
   docker-compose --profile with-nginx up -d
   ```

## 🛠️ Management Commands

### View Logs

```bash
# View recent logs
docker-compose logs

# Follow logs (live updates)
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50
```

### Restart Application

```bash
# Quick restart (keeps data)
docker-compose restart

# Full restart
docker-compose down
docker-compose up -d
```

### Update to Latest Version

```bash
# Pull new images from Docker Hub
docker-compose pull

# Apply updates
docker-compose up -d

# Verify version
docker-compose ps
```

### Stop Application

```bash
# Stop containers (data safe)
docker-compose down

# ⚠️ Delete everything including data
docker-compose down -v
```

### Shell Access (Debugging)

```bash
# Access container
docker-compose exec web /bin/sh

# Check database
docker-compose exec web sqlite3 data/checkin.db ".tables"
```

## 📊 Monitoring

### Check Status

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats --no-stream
```

### Health Checks

```bash
# Check if container is healthy
docker ps

# Test application response
curl http://localhost:5000
```

## 🔍 Troubleshooting

### Port Already in Use

```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (use PID from above)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 instead
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs

# Check for missing .env file
docker-compose config

# Recreate containers
docker-compose down
docker-compose up -d
```

### Can't Pull Docker Image

```bash
# Check Docker Hub connection
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Try alternative registry
# (if configured in docker-compose.yml)
```

### Database Issues

```bash
# Stop containers
docker-compose down

# Backup and reset database
mv data/checkin.db data/checkin.db.backup
docker-compose up -d

# Restore from backup if needed
```

### Clean Up Disk Space

```powershell
# Remove old images and containers
docker system prune -a

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
      - "8080:5000"  # Use port 8080 instead of 5000
```

### Resource Limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Performance Tuning

Environment variables in `.env`:

```bash
# Number of worker processes (CPU cores * 2 + 1)
GUNICORN_WORKERS=4

# Max requests per worker (memory leak protection)
GUNICORN_MAX_REQUESTS=1000
```

## 🌐 Production Deployment

### Quick Checklist

Before going live:

- [ ] Generate strong `SECRET_KEY` in `.env`
- [ ] Set secure admin password during setup
- [ ] Configure SSL (Caddy/Cloudflare/Let's Encrypt)
- [ ] Set up automated backups (see Backup section)
- [ ] Test backup restoration
- [ ] Configure custom branding (Admin Panel → Branding)
- [ ] Review firewall rules

### Hosting Options

See `DEPLOYMENT_CHECKLIST.md` for detailed guides:

- **VPS** (DigitalOcean, Linode, Vultr)
- **Cloud** (AWS, Google Cloud, Azure)
- **Managed** (Railway, Render, Fly.io)

All support Docker deployment!

### Automated Backups

Create cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/youth-secure-checkin && tar -czf ~/backups/checkin-$(date +\%Y\%m\%d).tar.gz data/ uploads/
```

### Log Rotation

Create `/etc/logrotate.d/docker-compose`:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=10M
    missingok
    delaycompress
    copytruncate
}
```

## 🐋 Docker Commands Reference

### Build

```bash
docker-compose build              # Build all services
docker-compose build --no-cache   # Build without cache
docker build -t youth-checkin .   # Build image directly
```

### Run

```bash
docker-compose up                 # Start (foreground)
docker-compose up -d              # Start (background)
docker-compose up --build         # Build and start
```

### Stop

```bash
docker-compose stop               # Stop services
docker-compose down               # Stop and remove containers
docker-compose down -v            # Stop and remove volumes
```

### Logs

```bash
docker-compose logs               # View all logs
docker-compose logs -f            # Follow logs
docker-compose logs --tail=50     # Last 50 lines
```

### Shell Access

```bash
docker-compose exec web /bin/sh   # Container shell
docker-compose exec web python    # Python REPL
```

## 📚 Quick Reference

### Most Used Commands

```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Update to latest
docker-compose pull && docker-compose up -d

# Backup data
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
docker-compose up -d
```

## 🆘 Need Help?

- **Features**: See `README.md` for application documentation
- **Deployment**: See `DEPLOYMENT_CHECKLIST.md` for hosting guides  
- **Issues**: [GitHub Issues](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)
- **Docker Docs**: [docs.docker.com](https://docs.docker.com/)

---

**Deploy from Docker Hub in 30 seconds! 🚀**
