# Docker Hub Repository Cleanup Guide

## Current Image Status

### Local Images (as of Nov 19, 2025)
```
mrcrunchybeans/youth-secure-checkin:demo      5ace5e4c06a2   624MB (NEW - demo mode)
mrcrunchybeans/youth-secure-checkin:latest    08b4c426f59a   520MB (current)
mrcrunchybeans/youth-secure-checkin:1.0.0     08b4c426f59a   520MB (same as latest)
mrcrunchybeans/youth-secure-checkin:v1        4a313a3ab34a   520MB (old/redundant)
```

## Recommended Docker Hub Tag Strategy

### ✅ Keep These Tags:
1. **`latest`** - Always the most recent stable release (auto-updated)
2. **`demo`** - Demo mode with auto-reset and test data
3. **`1.0.0`, `1.1.0`, etc.** - Semantic version tags for stability

### ❌ Remove These Tags:
- **`v1`** - Redundant (use `1.0.0` instead)
- Any untagged or test images
- Old version tags that are no longer needed

## Cleanup Steps

### Option 1: Docker Hub Web Interface (Easiest)

1. Go to: https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin/tags
2. Login to your Docker Hub account
3. Find tags to delete:
   - Look for `v1` tag
   - Look for any test tags (test, dev, etc.)
   - Look for old unneeded versions
4. Click the trash icon next to each tag to delete
5. Confirm deletion

### Option 2: Docker Hub CLI (if installed)

```bash
# Install hub-tool if needed
# https://github.com/docker/hub-tool

# Login
docker login

# List all tags
curl -s "https://hub.docker.com/v2/repositories/mrcrunchybeans/youth-secure-checkin/tags/" | jq -r '.results[].name'

# Delete specific tag (requires API token)
# Get token: https://hub.docker.com/settings/security
# Then use Docker Hub API to delete
```

### Option 3: PowerShell Script (Uses Docker Hub API)

```powershell
# Docker Hub credentials
$username = "mrcrunchybeans"
$repository = "youth-secure-checkin"
$token = "YOUR_DOCKER_HUB_API_TOKEN"  # Get from: https://hub.docker.com/settings/security

# Tags to delete
$tagsToDelete = @("v1")  # Add more as needed

# Delete each tag
foreach ($tag in $tagsToDelete) {
    Write-Host "Deleting tag: $tag"
    $uri = "https://hub.docker.com/v2/repositories/$username/$repository/tags/$tag/"
    
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    try {
        Invoke-RestMethod -Uri $uri -Method Delete -Headers $headers
        Write-Host "✅ Deleted: $tag" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to delete: $tag - $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

## Best Practices Going Forward

### Tagging Strategy

1. **Semantic Versioning** (Recommended)
   ```bash
   docker tag local-image:latest mrcrunchybeans/youth-secure-checkin:1.0.0
   docker tag local-image:latest mrcrunchybeans/youth-secure-checkin:latest
   docker push mrcrunchybeans/youth-secure-checkin:1.0.0
   docker push mrcrunchybeans/youth-secure-checkin:latest
   ```

2. **Demo Mode**
   ```bash
   docker tag demo-image:demo mrcrunchybeans/youth-secure-checkin:demo
   docker push mrcrunchybeans/youth-secure-checkin:demo
   ```

3. **Never Use These Patterns**
   - ❌ `v1`, `v2` (use `1.0.0`, `2.0.0`)
   - ❌ `test`, `dev` in production repo
   - ❌ Date-based tags (hard to track versions)

### Publishing Workflow

```bash
# Build new version
docker build -t mrcrunchybeans/youth-secure-checkin:1.1.0 .
docker tag mrcrunchybeans/youth-secure-checkin:1.1.0 mrcrunchybeans/youth-secure-checkin:latest

# Test locally
docker run -p 5000:5000 mrcrunchybeans/youth-secure-checkin:1.1.0

# Push both tags
docker push mrcrunchybeans/youth-secure-checkin:1.1.0
docker push mrcrunchybeans/youth-secure-checkin:latest

# Update demo if needed
docker build -f Dockerfile -t mrcrunchybeans/youth-secure-checkin:demo .
docker push mrcrunchybeans/youth-secure-checkin:demo
```

## Current Local Cleanup

To clean up redundant local images:

```powershell
# Remove old v1 tag locally
docker rmi mrcrunchybeans/youth-secure-checkin:v1

# Remove old 1.0.0 if you have latest
# (Keep 1.0.0 if you want version history)
# docker rmi mrcrunchybeans/youth-secure-checkin:1.0.0

# Remove dangling images
docker image prune -f

# Remove all unused images (careful!)
# docker image prune -a
```

## Recommended Final State

### Docker Hub Tags:
```
latest         -> Current stable release (auto-updated)
demo           -> Demo mode (updated separately)
1.0.0          -> First stable release (keep for history)
1.1.0          -> Next release (when ready)
1.2.0          -> Future releases
```

### Local Tags:
```
latest         -> Matches Docker Hub latest
demo           -> For building demo updates
[version]      -> Current working version
```

## Image Size Optimization (Future)

Your images are quite large. Consider multi-stage builds:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

This could reduce size from 624MB → ~300MB.

## Quick Actions Now

1. **Go to Docker Hub**: https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin/tags
2. **Delete `v1` tag** (click trash icon)
3. **Verify you have**: `latest`, `demo`, and `1.0.0`
4. **Clean local**: `docker rmi mrcrunchybeans/youth-secure-checkin:v1`

## Documentation Updates Needed

Update these files to reflect new tagging:
- [ ] README.md - Docker pull commands
- [ ] DOCKER_QUICKSTART.md - Tag references
- [ ] DOCKER.md - Version examples
- [ ] DOCKER_DEMO_README.md - Demo tag usage
