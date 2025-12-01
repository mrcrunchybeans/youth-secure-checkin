# Docker Hub Tag Cleanup Script
# Deletes specified tags from Docker Hub repository

param(
    [Parameter(Mandatory=$false)]
    [string]$Username = "mrcrunchybeans",
    
    [Parameter(Mandatory=$false)]
    [string]$Repository = "youth-secure-checkin",
    
    [Parameter(Mandatory=$false)]
    [string]$Token = "",
    
    [Parameter(Mandatory=$false)]
    [string[]]$TagsToDelete = @("v1")
)

Write-Host "🧹 Docker Hub Tag Cleanup Tool" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if token is provided
if ([string]::IsNullOrEmpty($Token)) {
    Write-Host "❌ Error: Docker Hub API token is required" -ForegroundColor Red
    Write-Host ""
    Write-Host "To get your token:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://hub.docker.com/settings/security" -ForegroundColor Yellow
    Write-Host "2. Click 'New Access Token'" -ForegroundColor Yellow
    Write-Host "3. Give it a name (e.g., 'cleanup-script')" -ForegroundColor Yellow
    Write-Host "4. Set permissions to 'Read, Write, Delete'" -ForegroundColor Yellow
    Write-Host "5. Copy the token and run this script with -Token parameter" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage: .\cleanup-docker-hub.ps1 -Token 'your-token-here'" -ForegroundColor Cyan
    exit 1
}

Write-Host "Repository: $Username/$Repository" -ForegroundColor White
Write-Host "Tags to delete: $($TagsToDelete -join ', ')" -ForegroundColor White
Write-Host ""

# Confirm deletion
$confirm = Read-Host "Are you sure you want to delete these tags? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green
Write-Host ""

# Delete each tag
$successCount = 0
$failCount = 0

foreach ($tag in $TagsToDelete) {
    Write-Host "🗑️  Deleting tag: $tag..." -NoNewline
    
    $uri = "https://hub.docker.com/v2/repositories/$Username/$Repository/tags/$tag/"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $uri -Method Delete -Headers $headers -ErrorAction Stop
        Write-Host " ✅ Deleted" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Successfully deleted: $successCount" -ForegroundColor Green
Write-Host "❌ Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 All tags cleaned up successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tags failed to delete. Check errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "View your Docker Hub repository:" -ForegroundColor Cyan
Write-Host "https://hub.docker.com/r/$Username/$Repository/tags" -ForegroundColor Blue
