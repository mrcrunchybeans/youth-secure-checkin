# Quick Docker Hub Publishing Script
# Run this step-by-step after starting Docker Desktop

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Youth Secure Check-in - Docker Hub Setup" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan

# Check if Docker Desktop is running
Write-Host "Step 1: Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker Desktop is running`n" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and run this script again.`n" -ForegroundColor Yellow
    exit 1
}

# Set Docker Hub username
Write-Host "Step 2: Docker Hub Username" -ForegroundColor Yellow
$username = "mrcrunchybeans"
Write-Host "Using Docker Hub username: $username`n" -ForegroundColor Cyan

# Login to Docker Hub
Write-Host "Step 3: Login to Docker Hub" -ForegroundColor Yellow
Write-Host "You will be prompted for your Docker Hub password...`n"
docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Login failed. Please check your credentials." -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Successfully logged in to Docker Hub`n" -ForegroundColor Green

# Build and tag the image
Write-Host "Step 4: Building Docker image..." -ForegroundColor Yellow
Write-Host "This will take 2-5 minutes...`n"

$imageName = "$username/youth-secure-checkin"
docker build -t "${imageName}:latest" -t "${imageName}:1.0.0" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Image built successfully`n" -ForegroundColor Green

# Test the image locally
Write-Host "Step 5: Testing image locally..." -ForegroundColor Yellow
Write-Host "Starting test container...`n"

# Stop any existing containers
docker stop youth-checkin-test 2>$null | Out-Null
docker rm youth-checkin-test 2>$null | Out-Null

# Generate a test secret key
$testSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# PowerShell-compatible docker run command (all on one line)
docker run -d -p 5001:5000 -e SECRET_KEY="$testSecret" -e DEVELOPER_PASSWORD="TestPass123" -v "${PWD}/data:/app/data" -v "${PWD}/uploads:/app/uploads" --name youth-checkin-test "${imageName}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Test container failed to start!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Test container started`n" -ForegroundColor Green
Write-Host "Waiting for container to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test if container is running
$containerStatus = docker inspect -f '{{.State.Running}}' youth-checkin-test 2>$null

if ($containerStatus -eq "true") {
    Write-Host "✓ Container is running!`n" -ForegroundColor Green
    Write-Host "Test URL: http://localhost:5001" -ForegroundColor Cyan
    Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:5001"
    
    $continue = Read-Host "`nDid the test work? (y/n)"
    
    if ($continue -ne "y") {
        Write-Host "`nCheck the logs with: docker logs youth-checkin-test" -ForegroundColor Yellow
        Write-Host "Stopping test container..." -ForegroundColor Yellow
        docker stop youth-checkin-test
        docker rm youth-checkin-test
        exit 1
    }
} else {
    Write-Host "✗ Container is not running!" -ForegroundColor Red
    Write-Host "Check logs with: docker logs youth-checkin-test`n" -ForegroundColor Yellow
    exit 1
}

# Clean up test container
Write-Host "`nCleaning up test container..." -ForegroundColor Yellow
docker stop youth-checkin-test
docker rm youth-checkin-test

# Push to Docker Hub
Write-Host "`nStep 6: Pushing to Docker Hub..." -ForegroundColor Yellow
Write-Host "This will take 3-10 minutes depending on your upload speed...`n"

docker push "${imageName}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Pushed latest tag`n" -ForegroundColor Green

Write-Host "Pushing version 1.0.0..." -ForegroundColor Yellow
docker push "${imageName}:1.0.0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Push failed!" -ForegroundColor Red
    exit 1
}

# Success!
Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "  🎉 SUCCESS! Image Published to Docker Hub" -ForegroundColor Green
Write-Host "===============================================`n" -ForegroundColor Green

Write-Host "Your image is now available at:" -ForegroundColor Cyan
Write-Host "  https://hub.docker.com/r/$username/youth-secure-checkin`n" -ForegroundColor White

Write-Host "Others can pull it with:" -ForegroundColor Cyan
Write-Host "  docker pull ${imageName}:latest`n" -ForegroundColor White

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Visit https://hub.docker.com/r/$username/youth-secure-checkin" -ForegroundColor White
Write-Host "  2. Add a description and README" -ForegroundColor White
Write-Host "  3. Update your GitHub README with Docker Hub badge" -ForegroundColor White
Write-Host "  4. Share with the community!`n" -ForegroundColor White

Write-Host "Opening Docker Hub in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "https://hub.docker.com/r/$username/youth-secure-checkin"

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
