# Quick Publish to Docker Hub - One Command
# This builds and pushes the image to mrcrunchybeans/youth-secure-checkin

Write-Host "`n🚀 Publishing to Docker Hub...`n" -ForegroundColor Cyan

# Login
Write-Host "Step 1: Login to Docker Hub" -ForegroundColor Yellow
docker login
if ($LASTEXITCODE -ne 0) { exit 1 }

# Build
Write-Host "`nStep 2: Building image..." -ForegroundColor Yellow
docker build -t mrcrunchybeans/youth-secure-checkin:latest -t mrcrunchybeans/youth-secure-checkin:1.0.0 .
if ($LASTEXITCODE -ne 0) { exit 1 }

# Push latest
Write-Host "`nStep 3: Pushing to Docker Hub..." -ForegroundColor Yellow
docker push mrcrunchybeans/youth-secure-checkin:latest
if ($LASTEXITCODE -ne 0) { exit 1 }

# Push version
docker push mrcrunchybeans/youth-secure-checkin:1.0.0
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n✅ Successfully published!`n" -ForegroundColor Green
Write-Host "View at: https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin`n" -ForegroundColor Cyan
