# Project Rename: troop_checkin → youth-secure-checkin

## Steps to Complete the Rename

### 1. Local Rename (DONE)
- Updated `__init__.py` package references
- Updated workspace file name needed: `troop_checkin.code-workspace` → `youth-secure-checkin.code-workspace`

### 2. GitHub Repository Rename
1. Go to https://github.com/mrcrunchybeans/troop_checkin/settings
2. In "Repository name" field, change to: `youth-secure-checkin`
3. Click "Rename"
4. Update local remote URL:
   ```bash
   git remote set-url origin https://github.com/mrcrunchybeans/youth-secure-checkin.git
   ```

### 3. Server Deployment Path Update
On the server at 192.168.2.159, run:

```bash
# Stop the service
sudo systemctl stop troop_checkin

# Rename the directory
sudo mv /var/www/troop_checkin /var/www/youth-secure-checkin

# Update systemd service file
sudo mv /etc/systemd/system/troop_checkin.service /etc/systemd/system/youth-secure-checkin.service

# Edit the service file
sudo nano /etc/systemd/system/youth-secure-checkin.service
# Update all paths from /var/www/troop_checkin to /var/www/youth-secure-checkin

# If using nginx, update nginx config
sudo nano /etc/nginx/sites-available/troop_checkin
# Update paths, then:
sudo mv /etc/nginx/sites-available/troop_checkin /etc/nginx/sites-available/youth-secure-checkin
sudo rm /etc/nginx/sites-enabled/troop_checkin
sudo ln -s /etc/nginx/sites-available/youth-secure-checkin /etc/nginx/sites-enabled/

# Reload systemd and restart services
sudo systemctl daemon-reload
sudo systemctl enable youth-secure-checkin
sudo systemctl start youth-secure-checkin
sudo nginx -t
sudo systemctl reload nginx

# Verify
sudo systemctl status youth-secure-checkin
```

### 4. Update Git Remote in Server
```bash
cd /var/www/youth-secure-checkin
git remote set-url origin https://github.com/mrcrunchybeans/youth-secure-checkin.git
git pull
```

### 5. Local Folder Rename
Rename your local folder:
- Windows: `C:\Users\Brian\troop_checkin` → `C:\Users\Brian\youth-secure-checkin`
- Or close VS Code, rename folder, reopen

### 6. Update Documentation References
Files that reference the old name (for documentation purposes):
- DEPLOYMENT.md
- HOSTINGER_DEPLOYMENT.md
- LABEL_PRINTING_FEATURE.md
- Migration scripts (these can keep old paths as they're utilities)

### 7. Workspace File Rename
Rename: `troop_checkin.code-workspace` → `youth-secure-checkin.code-workspace`

## Summary
The project is now called **Youth Secure Check-In** - a flexible, organization-agnostic check-in system with secure checkout codes!
