# Cloud Backup Configuration Guide

This guide explains how to set up cloud backups to Google Drive, Dropbox, and OneDrive.

## Overview

The cloud backup feature automatically backs up your entire database (including all families, check-in/check-out history, events, and configuration) to one or more cloud storage services.

**Features:**
- Automatic scheduled backups (hourly, daily, weekly, monthly)
- Manual backup triggers
- Support for Google Drive, Dropbox, and OneDrive
- Per-service success/failure tracking
- Encrypted data transmission

## Prerequisites

All required packages are already in `requirements.txt`:
- `google-auth-oauthlib==1.2.1` - Google OAuth
- `google-auth-httplib2==0.2.0` - Google HTTP transport
- `google-api-python-client==2.115.0` - Google Drive API
- `dropbox==12.0.2` - Dropbox SDK
- `APScheduler==3.10.4` - Scheduled job execution

Run: `pip install -r requirements.txt`

## Environment Variables

Add the following to your `.env` file (or set as environment variables):

### Google Drive

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

**Setup Instructions:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Google Drive API**
4. Create OAuth 2.0 credentials:
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: Add `https://your-domain.com/admin/oauth/google/callback`
   - Copy the Client ID and Client Secret to `.env`

### Dropbox

```
DROPBOX_OAUTH_CLIENT_ID=your-dropbox-app-id
DROPBOX_OAUTH_CLIENT_SECRET=your-dropbox-app-secret
```

**Setup Instructions:**
1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access" and "Full Dropbox"
4. Give your app a name
5. Go to "OAuth 2" settings
6. Add redirect URI: `https://your-domain.com/admin/oauth/dropbox/callback`
7. Copy App Key and App Secret to `.env`

### OneDrive (Microsoft 365)

```
ONEDRIVE_OAUTH_CLIENT_ID=your-azure-client-id
ONEDRIVE_OAUTH_CLIENT_SECRET=your-azure-client-secret
```

**Setup Instructions:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Name: "Youth Check-in Cloud Backup"
5. Supported account types: "Accounts in any organizational directory"
6. Click "Register"
7. In the app overview, copy "Application (client) ID" to `.env` as `ONEDRIVE_OAUTH_CLIENT_ID`
8. Go to "Certificates & secrets" → "Client secrets"
9. Click "New client secret" and copy the value to `.env` as `ONEDRIVE_OAUTH_CLIENT_SECRET`
10. Go to "API permissions"
11. Click "Add a permission" → "Microsoft Graph"
12. Select "Delegated permissions"
13. Search for and add: `Files.ReadWrite`
14. Go to "Authentication" → "Redirect URIs"
15. Click "Add URI" and add: `https://your-domain.com/admin/oauth/onedrive/callback`

## Using Cloud Backup

### Access Cloud Backup Settings

1. Log in to the admin panel
2. Click "Cloud Backup" from the admin dashboard
3. Configure each service by clicking the "Connect" button

### OAuth Flow

1. Click "Connect [Service]"
2. You'll be redirected to the service's login page
3. Log in and authorize the app
4. You'll be redirected back to the cloud backup page
5. Confirmation message will show the service is connected

### Manual Backup

Once at least one service is configured:
1. Click the "Backup Now" button
2. The system will create a backup and upload to all configured services
3. Results show per-service success/failure

### Scheduled Backups

1. Go to "Backup Schedule" section
2. Select frequency: Hourly, Daily, Weekly, or Monthly
3. Select time (UTC)
4. Click "Save Schedule"
5. Backups will automatically run on the configured schedule

### Disconnecting Services

1. From the service's card, click "Disconnect"
2. Confirm the action
3. The stored token is deleted
4. Backups will no longer go to that service

## Database Schema

The `settings` table stores backup configuration:

```sql
-- Backup schedule
INSERT INTO settings (key, value) VALUES ('backup_frequency', 'daily');  -- hourly|daily|weekly|monthly
INSERT INTO settings (key, value) VALUES ('backup_hour', '2');           -- 0-23 UTC

-- OAuth tokens (stored as JSON)
INSERT INTO settings (key, value) VALUES ('google_drive_token', '{...}');
INSERT INTO settings (key, value) VALUES ('dropbox_token', '{...}');
INSERT INTO settings (key, value) VALUES ('onedrive_token', '{...}');

-- Last backup status
INSERT INTO settings (key, value) VALUES ('last_backup_info', '{
  "success": true,
  "timestamp": "2024-01-15 14:30:00",
  "google_drive": {"success": true, "message": "..."},
  "dropbox": {"success": true, "message": "..."},
  "onedrive": {"success": false, "message": "..."}
}');
```

## Backup Contents

Each backup includes:
- Complete SQLite database file
- All family records
- Complete check-in/check-out history
- All events
- System configuration and settings
- User preferences and branding

**Note:** Backups are uploaded as binary database files. They're encrypted in transit via HTTPS/TLS.

## Troubleshooting

### "OAuth credentials not configured"

**Problem:** OAuth button shows error about missing credentials.

**Solution:** 
1. Verify environment variables are set correctly in `.env`
2. Restart the Flask application
3. Check `/admin/cloud-backup` page for updated status

### "Token exchange failed"

**Problem:** OAuth flow starts but fails at authorization.

**Solution:**
1. Verify redirect URIs exactly match in OAuth app settings (including https://)
2. Check your internet connection
3. Verify the OAuth app credentials haven't been revoked
4. Check application logs for detailed error

### "Backup completed with issues"

**Problem:** Backup runs but shows failure for some services.

**Solution:**
1. Check if that service is properly authorized
2. Try "Test Connection" button for that service
3. Verify you haven't exceeded cloud storage quota
4. Check service-specific API limits (e.g., Dropbox rate limits)

### Scheduled backups not running

**Problem:** Scheduled time passes but backup doesn't execute.

**Solution:**
1. Verify APScheduler is running (should start automatically)
2. Check application logs for scheduler errors
3. Verify at least one cloud service is configured
4. Try manual backup first to verify connectivity works

## API Routes

These routes are available for cloud backup management:

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/cloud-backup` | GET/POST | Configuration page |
| `/admin/backup/now` | POST | Trigger manual backup |
| `/admin/oauth/google` | GET | Start Google OAuth flow |
| `/admin/oauth/google/callback` | GET | Handle Google OAuth callback |
| `/admin/oauth/dropbox` | GET | Start Dropbox OAuth flow |
| `/admin/oauth/dropbox/callback` | GET | Handle Dropbox OAuth callback |
| `/admin/oauth/onedrive` | GET | Start OneDrive OAuth flow |
| `/admin/oauth/onedrive/callback` | GET | Handle OneDrive OAuth callback |
| `/admin/cloud-backup/disconnect/<service>` | POST | Disconnect service |

## Security Considerations

1. **OAuth Tokens:** Tokens are stored in the SQLite database. Use database encryption in production.
2. **HTTPS Required:** OAuth flows must use HTTPS URLs in production.
3. **Environment Variables:** Never commit `.env` files to version control.
4. **Scopes:** OAuth scopes are limited to backup-related permissions only.
5. **Rotation:** Tokens automatically refresh when needed.

## Production Deployment

### On Your Ubuntu Server:

1. **Update `.env` file with OAuth credentials:**
   ```bash
   ssh user@your-server
   cd /var/www/youth-secure-checkin
   nano .env
   # Add GOOGLE_OAUTH_CLIENT_ID, etc.
   ```

2. **Install/upgrade packages:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart youth-secure-checkin.service
   ```

4. **Verify in logs:**
   ```bash
   sudo journalctl -u youth-secure-checkin.service -f
   ```

5. **Access at:**
   ```
   https://your-domain.com/admin/cloud-backup
   ```

## Monitoring

### Check Last Backup Status

```sql
SELECT value FROM settings WHERE key = 'last_backup_info';
```

### Check Scheduled Jobs (from Python)

```python
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
for job in scheduler.get_jobs():
    print(f"Job: {job.id}, Next run: {job.next_run_time}")
```

### Application Logs

```bash
# On Ubuntu server
sudo journalctl -u youth-secure-checkin.service -f -n 100
```

## Support

For issues with specific cloud services:
- **Google Drive:** [Google Cloud Console](https://console.cloud.google.com)
- **Dropbox:** [Dropbox Developer Documentation](https://www.dropbox.com/developers/documentation)
- **OneDrive:** [Microsoft Graph Documentation](https://docs.microsoft.com/en-us/graph)
