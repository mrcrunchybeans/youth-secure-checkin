# Docker Demo Deployment

This directory contains Docker configuration for running a demo instance of Youth Secure Check-in.

## Quick Start

1. **Build and run the demo**:
   ```bash
   docker-compose up -d
   ```

2. **Access the demo**:
   - Open browser to: http://localhost:5000
   - Admin login: `demo` / `demo123`
   - Phone lookup demo: Use any of these phone numbers:
     - 555-0101 (Johnson family - 2 kids)
     - 555-0102 (Smith family - 1 kid)
     - 555-0103 (Williams family - 2 kids)
     - 555-0104 (Brown family - 1 kid)
     - 555-0105 (Garcia family - 3 kids)
     - 555-0106 (Martinez family - 1 kid)
     - 555-0107 (Anderson family - 2 kids)
     - 555-0108 (Taylor family - 1 kid)

3. **Stop the demo**:
   ```bash
   docker-compose down
   ```

## Features

### Demo Data
- **8 families** with realistic names and phone numbers
- **15 kids** with various notes (allergies, special needs)
- **6 events** (past meetings, camping trip, upcoming activities)
- **Check-in history** for past events with realistic timestamps
- **Pre-configured settings** for Demo Troop 4603

### Auto-Reset
The database automatically resets every 24 hours (configurable) to keep the demo fresh.

### Demo Branding
- Troop name: "Demo Troop 4603"
- Banner: "This is a demonstration instance. Data resets every 24 hours."
- Demo login credentials displayed

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - RESET_INTERVAL_HOURS=24  # Database reset interval
  - DEMO_MODE=true           # Enables demo banner
  - SECRET_KEY=...           # Change for production
  - DEVELOPER_PASSWORD=...   # Admin access password
```

### Port Configuration

To use a different port (e.g., 8080):

```yaml
ports:
  - "8080:5000"
```

### Reset Interval

To reset every 12 hours instead of 24:

```yaml
environment:
  - RESET_INTERVAL_HOURS=12
```

## Manual Operations

### View logs
```bash
docker-compose logs -f demo-app
```

### Manually reset database
```bash
docker-compose exec demo-app python demo_seed.py
```

### Access container shell
```bash
docker-compose exec demo-app /bin/bash
```

### Rebuild after code changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### Using Docker Hub

1. **Build and tag**:
   ```bash
   docker build -t yourusername/youth-checkin-demo:latest .
   docker push yourusername/youth-checkin-demo:latest
   ```

2. **Deploy on server**:
   ```bash
   docker pull yourusername/youth-checkin-demo:latest
   docker run -d -p 5000:5000 --name demo \
     -e RESET_INTERVAL_HOURS=24 \
     -e DEMO_MODE=true \
     yourusername/youth-checkin-demo:latest
   ```

### Using Docker Compose (Recommended)

1. **Copy to server**:
   ```bash
   scp docker-compose.yml user@server:/opt/youth-checkin-demo/
   scp Dockerfile user@server:/opt/youth-checkin-demo/
   ```

2. **On server**:
   ```bash
   cd /opt/youth-checkin-demo
   docker-compose up -d
   ```

### Behind Reverse Proxy (nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name demo.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS with Let's Encrypt

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d demo.yourdomain.com
```

## Demo Credentials

The demo includes these pre-configured accounts:

### Admin Access
- **Password**: `demo123`
- **Developer Password**: `demo2025`

### Family Phone Numbers
All phone numbers follow the pattern `555-01XX`:
- **555-0101**: Johnson family (Sarah & Mike, 2 kids)
- **555-0102**: Smith family (Jennifer, 1 kid)
- **555-0103**: Williams family (David & Lisa, 2 kids)
- **555-0104**: Brown family (Robert, 1 kid)
- **555-0105**: Garcia family (Maria & Carlos, 3 kids)
- **555-0106**: Martinez family (Amanda, 1 kid)
- **555-0107**: Anderson family (James & Emily, 2 kids)
- **555-0108**: Taylor family (Patricia, 1 kid)

## Troubleshooting

### Database not resetting
Check the reset scheduler logs:
```bash
docker-compose logs demo-reset
```

### Port already in use
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Container won't start
Check logs:
```bash
docker-compose logs demo-app
```

Remove volumes and rebuild:
```bash
docker-compose down -v
docker-compose up -d --build
```

### Out of disk space
Clean up Docker:
```bash
docker system prune -a
```

## Customization

### Different Demo Data

Edit `demo_seed.py` to customize:
- Family names and phone numbers
- Event schedules and descriptions
- Troop information
- Settings and branding

### Custom Reset Schedule

The reset scheduler supports:
- Hourly resets: `RESET_INTERVAL_HOURS=1`
- Daily resets: `RESET_INTERVAL_HOURS=24`
- Weekly resets: `RESET_INTERVAL_HOURS=168`

### Disable Auto-Reset

Remove the `demo-reset` service from `docker-compose.yml` or set:
```yaml
environment:
  - RESET_INTERVAL_HOURS=999999  # Effectively disable
```

## Security Notes

⚠️ **This is a DEMO configuration** with relaxed security:
- Weak demo passwords
- No rate limiting
- Simplified authentication

For production use:
1. Change all passwords to strong values
2. Use proper SECRET_KEY (not "demo-secret-key")
3. Enable HTTPS
4. Configure proper authentication
5. Review security settings in app

## Support

For issues with the main application, visit:
https://github.com/yourusername/youth-secure-checkin

For Docker-specific issues, check:
- Docker logs: `docker-compose logs`
- Container status: `docker-compose ps`
- System resources: `docker stats`
