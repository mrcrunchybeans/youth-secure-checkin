# GitHub Repository Cleanup Script
# Removes old test files, migration scripts, and internal utilities

Write-Host "🧹 Cleaning up GitHub repository...`n" -ForegroundColor Cyan

# Files to remove from git tracking
$filesToRemove = @(
    # Old test/debug scripts
    "test_env.py",
    "check_db.py",
    "check_route.py",
    "add_override_setting.py",
    
    # Old migration scripts (already applied)
    "migrate_add_authorized_adults.py",
    "migrate_add_checkout_code.py",
    "migrate_add_default_adult.py",
    "migrate_add_kid_notes.py",
    "migrate_add_label_settings.py",
    "migrate_add_share_tokens.py",
    "migrate_to_configurable.py",
    
    # Old rename/replace scripts (no longer needed)
    "replace_colors.py",
    "replace_troop.py",
    "RENAME_INSTRUCTIONS.md",
    
    # Migration documentation (outdated)
    "MIGRATION_DEFAULT_ADULT.md",
    
    # Old deployment doc (replaced by DOCKER.md)
    "HOSTINGER_DEPLOYMENT.md",
    
    # Old feature docs (now in main docs)
    "FEATURE_KID_NOTES.md",
    "EXPORT_FEATURES.md",
    "LABEL_PRINTING_FEATURE.md",
    
    # VS Code workspace file (personal config)
    "troop_checkin.code-workspace",
    
    # Test files
    "tests/test_app.py"
)

Write-Host "Files to be removed from git:" -ForegroundColor Yellow
$filesToRemove | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

Write-Host "`nThis will:" -ForegroundColor Yellow
Write-Host "  1. Remove files from git tracking" -ForegroundColor Gray
Write-Host "  2. Keep files locally (not deleted from disk)" -ForegroundColor Gray
Write-Host "  3. Add to .gitignore to prevent re-adding" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continue with cleanup? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`nRemoving files from git...`n" -ForegroundColor Green

# Remove each file from git (but keep locally)
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "Removing: $file" -ForegroundColor Gray
        git rm --cached $file 2>$null
    }
}

Write-Host "`n✓ Files removed from git tracking`n" -ForegroundColor Green

# Update .gitignore
Write-Host "Updating .gitignore..." -ForegroundColor Yellow

$gitignoreAdditions = @"

# Old test and migration files (kept locally for reference)
test_env.py
check_db.py
check_route.py
add_override_setting.py
migrate_*.py
replace_*.py
RENAME_INSTRUCTIONS.md
MIGRATION_DEFAULT_ADULT.md
HOSTINGER_DEPLOYMENT.md
FEATURE_KID_NOTES.md
EXPORT_FEATURES.md
LABEL_PRINTING_FEATURE.md
troop_checkin.code-workspace
tests/test_app.py
"@

Add-Content -Path .gitignore -Value $gitignoreAdditions

Write-Host "✓ Updated .gitignore`n" -ForegroundColor Green

# Show git status
Write-Host "Git status:" -ForegroundColor Yellow
git status --short

Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git status" -ForegroundColor White
Write-Host "  2. Commit changes: git add . && git commit -m 'Clean up old test and migration files'" -ForegroundColor White
Write-Host "  3. Push to GitHub: git push" -ForegroundColor White
Write-Host ""
Write-Host "Note: Files are kept locally but removed from GitHub`n" -ForegroundColor Gray
