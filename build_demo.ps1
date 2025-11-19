# Build and test demo Docker image

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Building Demo Docker Image" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Build the image
Write-Host "`nStep 1: Building Docker image..." -ForegroundColor Yellow
docker build -t youth-checkin-demo:latest .

Write-Host "`nStep 2: Starting demo container..." -ForegroundColor Yellow
docker-compose --profile demo up -d

Write-Host "`nStep 3: Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nStep 4: Checking demo-app health..." -ForegroundColor Yellow
docker-compose --profile demo logs demo-app --tail 20

Write-Host "`nStep 5: Testing database setup..." -ForegroundColor Yellow
docker-compose --profile demo exec demo-app python test_demo.py

Write-Host "`n================================" -ForegroundColor Green
Write-Host "✓ Demo Build Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "`nAccess the demo at: http://localhost:5000" -ForegroundColor White
Write-Host "`nLogin credentials:" -ForegroundColor White
Write-Host "  Username: demo" -ForegroundColor Gray
Write-Host "  Password: demo123" -ForegroundColor Gray
Write-Host "`nTest phone numbers:" -ForegroundColor White
Write-Host "  555-0101 (Johnson - 2 kids)" -ForegroundColor Gray
Write-Host "  555-0102 (Smith - 1 kid)" -ForegroundColor Gray
Write-Host "  555-0103 (Williams - 2 kids)" -ForegroundColor Gray
Write-Host "  555-0105 (Garcia - 3 kids)" -ForegroundColor Gray
Write-Host "`nTo stop the demo:" -ForegroundColor White
Write-Host "  docker-compose --profile demo down" -ForegroundColor Gray
Write-Host ""
