# Cloud Backup Feature - Quick Reference

## What's New

✅ **Cloud Backup** - Automatic and manual backups to Google Drive, Dropbox, and OneDrive
✅ **Secure Credentials** - OAuth credentials protected by developer password, stored in database
✅ **No Environment Variables** - Configure everything through web UI, no hardcoding

## Quick Start

### 1. Set Developer Password (Optional but Recommended)

Add to `.env` file on your production server:

```bash
DEVELOPER_PASSWORD=your-very-secure-password
```

### 2. Create OAuth Applications

For each cloud service (Google Drive, Dropbox, OneDrive):
- Create an OAuth app on the service's developer console
- Copy the Client ID and Client Secret
- **Important:** Set redirect URI to `https://your-domain.com/admin/oauth/[service]/callback`

See **`CLOUD_BACKUP_SETUP_SECURE.md`** for detailed instructions for each service.

### 3. Install Dependencies

```bash
pip install -r requirements.txt --upgrade
```

Adds: `APScheduler==3.10.4` for scheduled backups

### 4. Restart Application

```bash
sudo systemctl restart youth-secure-checkin.service
```

### 5. Configure Cloud Backup Credentials

1. Log in to admin panel
2. Click **"Cloud Backup"** card on dashboard
3. Click **"Credentials"** button (yellow, top right)
4. Enter your developer password and unlock
5. Paste OAuth credentials for each service
6. Click **"Save Credentials"**

### 6. Connect Services

1. Go back to **"Cloud Backup"** page
2. For each service, click **"Connect [Service]"**
3. Authorize the OAuth app when redirected
4. Return to see "Connected" status

### 7. Set Up Backup Schedule

1. On Cloud Backup page, find **"Backup Schedule"** section
2. Select frequency (Hourly, Daily, Weekly, Monthly)
3. Select time (UTC)
4. Click **"Save Schedule"**

### 8. Test Manual Backup

1. Click **"Backup Now"** button
2. Wait for completion
3. Check status for each service
4. Verify backup files in cloud storage

## Key Features

| Feature | Details |
|---------|---------|
| **Services** | Google Drive, Dropbox, OneDrive (mix and match) |
| **Frequency** | Hourly, Daily, Weekly, or Monthly |
| **Manual Trigger** | "Backup Now" button for immediate backup |
| **Scheduling** | APScheduler runs automatically on schedule |
| **What's Backed Up** | Entire database + all history + configuration |
| **Status Tracking** | Per-service success/failure indicators |
| **Security** | Developer password protected, secure database storage |
| **Credentials** | Stored in database, configurable via web UI |

## File Changes

### New Files
- `cloud_backup.py` - Cloud service classes (unchanged)
- `templates/admin/cloud_backup.html` - Configuration UI (unchanged)
- `templates/admin/cloud_backup_credentials.html` - **NEW - Credential config page**
- `CLOUD_BACKUP_SETUP_SECURE.md` - **NEW - Secure setup guide**
- `CLOUD_BACKUP_QUICKREF.md` - This file

### Modified Files
- `app.py` - Added helper functions, credential routes, OAuth using database
- `requirements.txt` - APScheduler (unchanged)
- `templates/admin/index.html` - Cloud Backup card (unchanged)

## API Routes

```
GET/POST  /admin/cloud-backup/credentials         - Configure OAuth credentials
GET/POST  /admin/cloud-backup                     - Configuration page
POST      /admin/backup/now                       - Manual backup
GET       /admin/oauth/google                     - Start Google OAuth
GET       /admin/oauth/google/callback            - Google callback
GET       /admin/oauth/dropbox                    - Start Dropbox OAuth
GET       /admin/oauth/dropbox/callback           - Dropbox callback
GET       /admin/oauth/onedrive                   - Start OneDrive OAuth
GET       /admin/oauth/onedrive/callback          - OneDrive callback
POST      /admin/cloud-backup/disconnect/<service> - Disconnect
```

## Security Features

✓ Developer password protection
✓ Credentials masked in locked UI
✓ Tokens never in environment variables
✓ HTTPS/TLS for all OAuth
✓ Credentials stored in secure database
✓ Per-service token management
✓ Access control via @require_auth

## Troubleshooting

**Credentials locked - can't edit**
- Enter developer password on credentials page
- Click "Unlock"

**"OAuth credentials not configured"**
- Go to Credentials page
- Unlock with developer password
- Add Client ID and Secret
- Save

**"Invalid developer password"**
- Check .env for DEVELOPER_PASSWORD value
- Password is case-sensitive
- Restart app after changing .env

**OAuth flow fails**
- Verify redirect URI exactly matches OAuth app settings
- Check credentials were copied correctly
- Try creating a new OAuth app

**Scheduled backup not running**
- Verify at least one service is connected
- Check application logs
- Test manual backup first
- Verify schedule was saved

## Environment Variables

Only one optional environment variable needed:

```bash
DEVELOPER_PASSWORD=your-secure-password  # Optional - protects credentials
```

**NOT needed anymore:**
- ~~GOOGLE_OAUTH_CLIENT_ID~~ - Use web UI
- ~~GOOGLE_OAUTH_CLIENT_SECRET~~ - Use web UI
- ~~DROPBOX_OAUTH_CLIENT_ID~~ - Use web UI
- ~~DROPBOX_OAUTH_CLIENT_SECRET~~ - Use web UI
- ~~ONEDRIVE_OAUTH_CLIENT_ID~~ - Use web UI
- ~~ONEDRIVE_OAUTH_CLIENT_SECRET~~ - Use web UI

## Database

Settings table stores:
```sql
google_oauth_client_id              -- Stored in database
google_oauth_client_secret          -- Stored in database
dropbox_oauth_client_id             -- Stored in database
dropbox_oauth_client_secret         -- Stored in database
onedrive_oauth_client_id            -- Stored in database
onedrive_oauth_client_secret        -- Stored in database
backup_frequency                    -- 'daily', 'hourly', etc.
backup_hour                         -- '0'-'23' (UTC)
google_drive_token                  -- Access token (OAuth)
dropbox_token                       -- Access token (OAuth)
onedrive_token                      -- Access token (OAuth)
last_backup_info                    -- Status of last backup
```

## Next Steps

1. **Development:**
   - Test each service's OAuth flow
   - Verify scheduled backups execute
   - Test credential locking/unlocking

2. **Production:**
   - Push code to server
   - Set DEVELOPER_PASSWORD in .env
   - Restart service
   - Configure credentials through UI
   - Connect services and test

3. **Monitoring:**
   - Check logs: `sudo journalctl -u youth-secure-checkin.service -f`
   - Manual backup before relying on schedule
   - Monitor cloud storage quota

## Documentation

- **Detailed Setup:** See `CLOUD_BACKUP_SETUP_SECURE.md`
- **Implementation Details:** See `CLOUD_BACKUP_IMPLEMENTATION.md`
- **Code:** See `cloud_backup.py` and `app.py` (routes starting line 1955)

## Support

For specific cloud service setup:
- **Google Drive:** https://console.cloud.google.com
- **Dropbox:** https://www.dropbox.com/developers/apps
- **OneDrive:** https://portal.azure.com

For app issues:
```bash
sudo journalctl -u youth-secure-checkin.service -f -n 100
```

