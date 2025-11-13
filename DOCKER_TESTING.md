# Docker Local Testing Guide

This guide will help you test the Docker container locally before pushing to a container registry.

## Prerequisites

✅ Docker installed (you have version 27.1.1)
✅ Docker Desktop running (check system tray icon)
✅ .env file configured (already exists)

## Step-by-Step Testing Process

### 1. Build the Docker Image Locally

```powershell
# Build the image with a test tag
docker build -t youth-secure-checkin:test .

# This will:
# - Read the Dockerfile
# - Install Python dependencies
# - Copy application files
# - Set up the container
# - Take 2-5 minutes on first build
```

### 2. Verify the Image Was Created

```powershell
# List Docker images
docker images youth-secure-checkin

# You should see:
# REPOSITORY               TAG     IMAGE ID       CREATED         SIZE
# youth-secure-checkin     test    <image-id>     X seconds ago   ~XXX MB
```

### 3. Test Run with Docker Compose

```powershell
# Start the container in the background
docker-compose up -d

# Check if container is running
docker-compose ps

# View logs
docker-compose logs -f web

# Press Ctrl+C to exit logs (container keeps running)
```

### 4. Access the Application

Open your browser to:
- **Main URL**: http://localhost:5000
- **Setup Wizard**: Should appear on first visit
- **Admin Panel**: http://localhost:5000/admin

### 5. Test Key Features

#### a. Initial Setup
- [ ] Complete the setup wizard
- [ ] Set organization name and colors
- [ ] Upload a logo (optional)
- [ ] Verify branding appears correctly

#### b. Family Management
- [ ] Add a test family from Admin → Families
- [ ] Edit the family
- [ ] Verify data persists after container restart

#### c. Event Management
- [ ] Add a test event from Admin → Events
- [ ] Check-in a kid to the event
- [ ] Verify check-in appears in history

#### d. Data Persistence Test
```powershell
# Stop the container
docker-compose down

# Start it again
docker-compose up -d

# Visit http://localhost:5000
# Verify: All your data should still be there
```

### 6. Test Container Logs

```powershell
# View real-time logs
docker-compose logs -f web

# View last 50 lines
docker-compose logs --tail=50 web

# Check for errors (should see no ERROR level messages)
```

### 7. Test Health Check

```powershell
# Check container health status
docker inspect --format='{{.State.Health.Status}}' youth-secure-checkin-web-1

# Should return: healthy
```

### 8. Test Database Backup

```powershell
# Copy database out of container for backup
docker cp youth-secure-checkin-web-1:/app/data/checkin.db ./backup-test.db

# Verify file exists and has data
dir backup-test.db
```

### 9. Test with Nginx (Optional)

```powershell
# Stop basic setup
docker-compose down

# Start with Nginx reverse proxy
docker-compose --profile with-nginx up -d

# Access via Nginx
# http://localhost (port 80)

# Check Nginx logs
docker-compose logs nginx
```

### 10. Performance Testing

```powershell
# Check resource usage
docker stats youth-secure-checkin-web-1

# Press Ctrl+C to exit

# Should see:
# - Memory usage: typically < 100MB
# - CPU usage: should be low when idle
```

## Common Issues and Solutions

### Issue: Build fails with "requirements.txt not found"
**Solution**: Make sure you're in the project directory with Dockerfile
```powershell
cd C:\Users\Brian\troop_checkin
```

### Issue: Port 5000 already in use
**Solution**: Stop the running Python development server
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Stop Docker containers
docker-compose down
```

### Issue: Container starts but exits immediately
**Solution**: Check logs for errors
```powershell
docker-compose logs web
```

### Issue: Database locked error
**Solution**: Make sure only one instance is running
```powershell
docker-compose down
# Wait 5 seconds
docker-compose up -d
```

### Issue: Changes not reflected after rebuild
**Solution**: Use --no-cache flag
```powershell
docker build --no-cache -t youth-secure-checkin:test .
docker-compose up -d --force-recreate
```

## Cleanup Commands

```powershell
# Stop and remove containers
docker-compose down

# Remove containers and volumes (deletes data!)
docker-compose down -v

# Remove the test image
docker rmi youth-secure-checkin:test

# View disk usage
docker system df

# Clean up unused images/containers (optional)
docker system prune
```

## Pre-Push Checklist

Before pushing to Docker Hub or another registry:

- [ ] Container builds without errors
- [ ] Application starts and shows setup wizard
- [ ] Can complete setup and access admin panel
- [ ] Can add families and events
- [ ] Check-in functionality works
- [ ] Data persists after container restart
- [ ] Health check shows "healthy"
- [ ] No critical errors in logs
- [ ] Database backup works
- [ ] Resource usage is reasonable
- [ ] All tests in "Test Key Features" section pass

## Quick Test Script

Run all tests at once:

```powershell
# Full test sequence
Write-Host "Building image..." -ForegroundColor Green
docker build -t youth-secure-checkin:test .

Write-Host "`nStarting container..." -ForegroundColor Green
docker-compose up -d

Write-Host "`nWaiting for startup..." -ForegroundColor Green
Start-Sleep -Seconds 5

Write-Host "`nChecking health..." -ForegroundColor Green
docker inspect --format='{{.State.Health.Status}}' youth-secure-checkin-web-1

Write-Host "`nContainer is ready at http://localhost:5000" -ForegroundColor Green
Write-Host "View logs with: docker-compose logs -f web" -ForegroundColor Yellow
```

## Next Steps: Pushing to Registry

Once all tests pass, see DOCKER.md section "Publishing to Docker Hub" for instructions on:
1. Tagging your image
2. Logging into Docker Hub
3. Pushing the image
4. Verifying the push

---

**Ready to start testing? Run:**
```powershell
docker build -t youth-secure-checkin:test .
docker-compose up -d
```

Then open http://localhost:5000 in your browser!
