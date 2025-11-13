# Docker Deployment Guide

This guide explains how to deploy Youth Secure Check-in using Docker containers.

## 📋 Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+
- 512 MB RAM minimum (1 GB recommended)
- 2 GB disk space

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.docker .env

# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Edit .env and paste the generated key
nano .env  # or your preferred editor
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application

Open your browser to: `http://localhost:5000`

The setup wizard will guide you through initial configuration!

## 🔧 Configuration Options

### Basic Deployment (Default)

Just the web application:

```bash
docker-compose up -d
```

Access at: `http://localhost:5000`

### With Nginx Reverse Proxy

Includes Nginx for SSL/TLS:

```bash
docker-compose --profile with-nginx up -d
```

Access at: `http://localhost` (port 80) or `https://localhost` (port 443)

## 📁 Data Persistence

Data is stored in Docker volumes:

- **Database**: `./data/checkin.db`
- **Uploads**: `./uploads/` (logos, favicons)

These directories are created automatically and persist between container restarts.

### Backup Data

```bash
# Backup database
docker cp youth-checkin:/app/data/checkin.db ./backup-$(date +%Y%m%d).db

# Or backup everything
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
docker-compose up -d
```

### Restore Data

```bash
docker-compose down
tar -xzf backup-YYYYMMDD.tar.gz
docker-compose up -d
```

## 🔐 Security Considerations

### Environment Variables

Never commit `.env` to version control:

```bash
# Already in .gitignore, but verify:
echo ".env" >> .gitignore
```

### Production Secrets

Generate strong secrets:

```bash
# SECRET_KEY (64 characters)
python3 -c "import secrets; print(secrets.token_hex(32))"

# DEVELOPER_PASSWORD (use password manager)
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

### SSL/TLS Setup

For production with Nginx:

1. **Create Nginx Config**:
   ```bash
   mkdir -p nginx/ssl
   ```

2. **Get SSL Certificate** (Let's Encrypt):
   ```bash
   # Using certbot
   sudo certbot certonly --standalone -d yourdomain.com
   
   # Copy certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
   ```

3. **Create nginx.conf**:
   ```nginx
   events {
       worker_connections 1024;
   }

   http {
       upstream app {
           server web:5000;
       }

       server {
           listen 80;
           server_name yourdomain.com;
           return 301 https://$server_name$request_uri;
       }

       server {
           listen 443 ssl;
           server_name yourdomain.com;

           ssl_certificate /etc/nginx/ssl/fullchain.pem;
           ssl_certificate_key /etc/nginx/ssl/privkey.pem;

           location / {
               proxy_pass http://app;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }
       }
   }
   ```

4. **Start with Nginx**:
   ```bash
   docker-compose --profile with-nginx up -d
   ```

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Web app only
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Application

```bash
# Restart all services
docker-compose restart

# Restart web app only
docker-compose restart web
```

### Stop Application

```bash
# Stop (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v  # ⚠️ This deletes data!
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Shell Access

```bash
# Access container shell
docker-compose exec web /bin/bash

# Or using docker directly
docker exec -it youth-checkin /bin/bash

# Run Python commands
docker-compose exec web python -c "from app import init_db; init_db()"
```

## 📊 Monitoring

### Health Checks

Check container health:

```bash
docker ps
# Look for "healthy" status
```

### Resource Usage

```bash
# Real-time stats
docker stats youth-checkin

# Detailed info
docker inspect youth-checkin
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Port 5000 already in use
docker-compose down
sudo lsof -i :5000  # Find and kill process

# 2. Permission issues with volumes
sudo chown -R $USER:$USER data/ uploads/

# 3. Missing .env file
cp .env.docker .env
```

### Database Locked

```bash
# Stop all containers
docker-compose down

# Remove any stale locks
rm -f data/checkin.db-*

# Restart
docker-compose up -d
```

### Can't Access Application

```bash
# Check container is running
docker ps | grep youth-checkin

# Check port binding
docker port youth-checkin

# Test from inside container
docker-compose exec web curl http://localhost:5000

# Check firewall
sudo ufw allow 5000  # If using UFW
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
df -h
du -sh data/ uploads/
```

## 🚀 Advanced Configuration

### Custom Port

Edit `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "8080:5000"  # Change 8080 to your desired port
```

### Multiple Workers

For high traffic, increase Gunicorn workers:

Edit `Dockerfile` CMD:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "5", "wsgi:app"]
```

### Memory Limits

Add resource limits to `docker-compose.yml`:

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

### Auto-Restart Policy

Already configured as `unless-stopped`. Other options:

```yaml
restart: always  # Always restart
restart: on-failure  # Only on failure
restart: "no"  # Never restart
```

## 🌐 Production Deployment

### Recommended Stack

1. **Application**: Docker Compose
2. **Reverse Proxy**: Nginx with SSL
3. **SSL Certificate**: Let's Encrypt (certbot)
4. **Firewall**: UFW or iptables
5. **Monitoring**: Docker health checks + external monitoring

### Deployment Checklist

- [ ] Set strong SECRET_KEY and DEVELOPER_PASSWORD
- [ ] Configure SSL/TLS certificates
- [ ] Set up automated backups (cron job)
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Test backup restoration
- [ ] Configure monitoring/alerting
- [ ] Document access procedures
- [ ] Test failover scenarios

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

### Exec

```bash
docker-compose exec web bash      # Shell in container
docker-compose exec web python    # Python REPL
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Security](https://docs.docker.com/engine/security/)

## 🆘 Getting Help

- **Issues**: [GitHub Issues](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mrcrunchybeans/youth-secure-checkin/discussions)
- **Docker Forum**: [Docker Community](https://forums.docker.com/)

---

**Happy Dockerizing! 🐳**
