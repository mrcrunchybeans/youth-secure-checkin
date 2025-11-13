# Quick Docker Test - Start Here!

## Step 1: Start Docker Desktop

⚠️ **Docker Desktop is not currently running**

1. Open **Docker Desktop** from your Start menu
2. Wait for the whale icon in system tray to show "Docker Desktop is running"
3. This may take 1-2 minutes on first start

## Step 2: Build and Test

Once Docker Desktop is running, open PowerShell in this directory and run:

```powershell
# Build the image
docker build -t youth-secure-checkin:test .

# Start the container
docker-compose up -d

# Check if it's running
docker-compose ps

# View the application
# Open browser to: http://localhost:5000
```

## Step 3: View Logs

```powershell
# See what's happening
docker-compose logs -f web

# Press Ctrl+C to exit (container keeps running)
```

## Step 4: Stop When Done

```powershell
# Stop the container
docker-compose down
```

## Full Testing Guide

See **DOCKER_TESTING.md** for comprehensive testing instructions including:
- Health checks
- Data persistence testing
- Performance monitoring
- Troubleshooting
- Pre-push checklist

---

**Current Status**: Docker Desktop needs to be started before testing can begin.

**After starting Docker Desktop**: Run the commands in Step 2 above.
