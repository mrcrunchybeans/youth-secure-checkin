# 🚀 Youth Secure Check-in + YOURLS - Quick Start Guide

## One-Command Docker Deployment

### Production Setup
```bash
# 1. Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# 2. Create environment file
cp .env.example .env
nano .env  # Edit SECRET_KEY and passwords

# 3. Start everything (check-in + YOURLS)
docker compose --profile production up -d

# 4. Access applications
# Youth Check-in: http://localhost:5000
# YOURLS Admin:   http://localhost:8080/admin
```

### Demo Mode Setup
```bash
# Start demo with pre-loaded data
docker compose -f docker-compose.demo.yml up -d

# Demo credentials:
# Check-in: demo123
# Admin: demo123
# YOURLS: admin/admin

# Access:
# Youth Check-in: http://localhost:5000
# YOURLS Admin:   http://localhost:8080/admin
```

## 5-Minute YOURLS Configuration

1. **Install YOURLS** (first-time only)
   - Visit: http://localhost:8080/admin
   - Click "Install YOURLS"
   - Wait 10 seconds for installation

2. **Get API Token**
   - Login to YOURLS admin
   - Navigate to: Tools → API
   - Copy your signature token

3. **Configure Youth Check-in**
   - Login to: http://localhost:5000
   - Go to: Admin → Security → URL Shortener
   - Enter:
     ```
     YOURLS API URL: http://yourls/yourls-api.php
     API Signature:  [paste token from step 2]
     ```
   - Click "Save YOURLS Settings"

4. **Test Integration**
   - Check-in a family
   - View QR code modal
   - Short URL appears below QR code! 🎉

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Youth Check-in | 5000 | http://localhost:5000 |
| YOURLS | 8080 | http://localhost:8080/admin |
| MySQL (internal) | 3306 | (Not exposed) |

## Container Reference

### Production
- `youth-checkin` - Main application
- `youth-checkin-yourls` - URL shortener
- `youth-checkin-yourls-db` - MySQL database

### Demo
- `youth-checkin-demo` - Demo application
- `youth-checkin-demo-reset` - Auto-reset service
- `youth-checkin-demo-yourls` - URL shortener
- `youth-checkin-demo-yourls-db` - MySQL database

## Common Commands

```bash
# View logs
docker logs youth-checkin
docker logs youth-checkin-yourls

# Stop all services
docker compose --profile production down

# Update to latest version
docker compose --profile production pull
docker compose --profile production up -d

# Backup data
docker exec youth-checkin-yourls-db \
  mysqldump -u yourls -pyourlspass yourls > yourls-backup.sql

# View running containers
docker ps | grep youth
```

## Troubleshooting

### YOURLS not accessible
```bash
# Check if container is running
docker ps | grep yourls

# View logs
docker logs youth-checkin-yourls

# Restart YOURLS
docker restart youth-checkin-yourls
```

### Database connection errors
```bash
# Wait 30 seconds for MySQL to initialize (first start)
sleep 30

# Check database logs
docker logs youth-checkin-yourls-db

# Verify database is ready
docker exec youth-checkin-yourls-db mysql -u yourls -pyourlspass -e "SHOW DATABASES;"
```

### Short URLs not working
1. Verify YOURLS API URL: `http://yourls/yourls-api.php`
2. Check signature token in Youth Check-in settings
3. Test YOURLS manually:
   ```bash
   docker exec youth-checkin curl "http://yourls/yourls-api.php?signature=YOUR_TOKEN&action=shorturl&url=https://google.com&format=json"
   ```

## Environment Variables (.env)

Required for production:
```env
SECRET_KEY=generate_with_secrets_module
DEVELOPER_PASSWORD=your_dev_password

YOURLS_DB_PASSWORD=yourlspass
YOURLS_DB_ROOT_PASSWORD=rootpass
YOURLS_USER=admin
YOURLS_PASSWORD=change_this_securely
```

## What Gets Created

### Docker Volumes
- `youth-secure-checkin_yourls-data` - YOURLS files
- `youth-secure-checkin_yourls-db-data` - MySQL data

### Demo Volumes (separate)
- `youth-secure-checkin_demo-yourls-data`
- `youth-secure-checkin_demo-yourls-db-data`

### Local Directories (production)
- `./data/` - SQLite database
- `./uploads/` - Logos and images

## Upgrading

```bash
# Production
docker compose --profile production down
docker compose --profile production pull
docker compose --profile production up -d

# Demo
docker compose -f docker-compose.demo.yml down
docker compose -f docker-compose.demo.yml pull
docker compose -f docker-compose.demo.yml up -d
```

## Removing Everything

```bash
# Stop and remove containers
docker compose --profile production down -v

# Remove images
docker rmi mrcrunchybeans/youth-secure-checkin:latest
docker rmi yourls:latest
docker rmi mysql:8.0

# Remove local data (careful!)
rm -rf data/ uploads/
```

## Production Checklist

- [ ] Changed default passwords in .env
- [ ] SECRET_KEY is randomly generated
- [ ] YOURLS_PASSWORD is secure
- [ ] Ports 5000 and 8080 are accessible
- [ ] Firewall rules configured
- [ ] SSL/HTTPS configured (if using reverse proxy)
- [ ] Backup strategy in place
- [ ] Tested check-in flow end-to-end
- [ ] Verified QR codes show short URLs
- [ ] Documented admin credentials securely

## Documentation

- **DOCKER.md** - Comprehensive Docker deployment guide
- **YOURLS_SETUP.md** - Detailed YOURLS setup (Docker + bare-metal)
- **README.md** - General project information
- **DEPLOYMENT_CHECKLIST.md** - Production deployment steps

## Support

- GitHub Issues: https://github.com/mrcrunchybeans/youth-secure-checkin/issues
- YOURLS Docs: https://docs.yourls.org/
- Docker Docs: https://docs.docker.com/

---

**Total setup time:** ~10 minutes from clone to fully functional system with URL shortening! 🚀
