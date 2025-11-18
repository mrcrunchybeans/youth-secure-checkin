# Cloud Backup Configuration Guide

This guide explains how to set up cloud backups to Google Drive, Dropbox, and OneDrive with secure credential management.

## Overview

The cloud backup feature automatically backs up your entire database (including all families, check-in/check-out history, events, and configuration) to one or more cloud storage services.

**Features:**
- ✓ Automatic scheduled backups (hourly, daily, weekly, monthly)
- ✓ Manual backup triggers
- ✓ Support for Google Drive, Dropbox, and OneDrive
- ✓ Per-service success/failure tracking
- ✓ Encrypted data transmission
- ✓ **Credentials secured behind developer password**
- ✓ **No hardcoded environment variables needed**

## Prerequisites

All required packages are already in `requirements.txt`:
- `google-auth-oauthlib==1.2.1` - Google OAuth
- `google-auth-httplib2==0.2.0` - Google HTTP transport
- `google-api-python-client==2.115.0` - Google Drive API
- `dropbox==12.0.2` - Dropbox SDK
- `APScheduler==3.10.4` - Scheduled job execution

Run: `pip install -r requirements.txt`

## Secure Credential Management

### Security Model

All OAuth credentials are now:
- ✓ **Protected by developer password** - Only accessible when unlocked with DEVELOPER_PASSWORD
- ✓ **Stored securely in database** - Never in environment variables or code
- ✓ **Masked when locked** - Credentials are obscured in the UI when not unlocked
- ✓ **Never logged** - Credentials never appear in application logs
- ✓ **Encrypted in transit** - All OAuth flows use HTTPS/TLS

### First-Time Setup

1. **Optional: Set Developer Password** (recommended for production)
   ```bash
   # Add to .env file on your production server
   DEVELOPER_PASSWORD=your-very-secure-password
   ```

2. **Access Credentials Configuration**
   - Log in to admin panel at `https://your-domain.com/admin`
   - Click **"Cloud Backup"** card on dashboard
   - Click **"Credentials"** button (yellow button, top right)

3. **Unlock Credentials** (if DEVELOPER_PASSWORD is set)
   - Enter your developer password in the "Developer Password" field
   - Click "Unlock"
   - Credentials input fields become editable

4. **Add OAuth Credentials**
   - Create OAuth apps (see instructions below)
   - Copy Client ID and Client Secret for each service
   - Paste into the corresponding fields
   - Click "Save Credentials"

5. **Connect Services**
   - Go back to **"Cloud Backup"** page
   - Click **"Connect [Service]"** for each service
   - You'll be redirected to the service's login page
   - Authorize the app
   - Return to Cloud Backup page with confirmation

### No Environment Variables for Credentials!

Unlike typical OAuth setups, you **do NOT** need environment variables for OAuth credentials:

❌ Don't set these:
```bash
GOOGLE_OAUTH_CLIENT_ID=xxx      # NO - use web UI instead
GOOGLE_OAUTH_CLIENT_SECRET=xxx  # NO - use web UI instead
DROPBOX_OAUTH_CLIENT_ID=xxx     # NO - use web UI instead
```

✅ Only optional environment variable:
```bash
DEVELOPER_PASSWORD=your-secure-password  # Optional - adds security layer
```

## Creating OAuth Applications

### Google Drive Setup

**Step 1: Create OAuth App**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable the **Google Drive API**:
   - Search for "Google Drive API"
   - Click "Enable"

**Step 2: Create Credentials**
1. Go to "Credentials" in the left menu
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, create an OAuth consent screen first:
   - User type: "External"
   - Fill in app name and contact
   - Add scope: `https://www.googleapis.com/auth/drive`
   - Continue and finish

**Step 3: Set Redirect URI**
1. In OAuth 2.0 Client IDs, click "Create Credentials" → "OAuth client ID" again
2. Application type: **"Web application"**
3. Name: "Youth Check-in"
4. Under "Authorized redirect URIs", add:
   ```
   https://your-domain.com/admin/oauth/google/callback
   ```
5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

### Dropbox Setup

**Step 1: Create OAuth App**
1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose:
   - **API:** Scoped access
   - **Access type:** Full Dropbox
4. Give your app a name (e.g., "Youth Check-in Backup")
5. Click "Create app"

**Step 2: Configure OAuth**
1. Go to "Settings"
2. Under "OAuth 2", set **Redirect URIs** to:
   ```
   https://your-domain.com/admin/oauth/dropbox/callback
   ```
3. Copy your **App key** and **App secret**

### OneDrive (Microsoft 365) Setup

**Step 1: Create Azure App**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **"Azure Active Directory"** → **"App registrations"**
3. Click **"New registration"**
4. Fill in:
   - Name: "Youth Check-in Cloud Backup"
   - Supported account types: "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
5. Click "Register"

**Step 2: Add Credentials**
1. Go to **"Certificates & secrets"**
2. Click **"New client secret"**
3. Description: "Backup Credentials"
4. Expires: "Never" or your preference
5. Click "Add"
6. **Copy the Value** (not the Secret ID)

**Step 3: Set Permissions**
1. Go to **"API permissions"**
2. Click **"Add a permission"**
3. Select **"Microsoft Graph"**
4. Choose **"Delegated permissions"**
5. Search for **"Files.ReadWrite"** and add it
6. Click "Add permissions"

**Step 4: Set Redirect URI**
1. Go to **"Authentication"**
2. Under "Redirect URIs", click **"Add URI"**
3. Add:
   ```
   https://your-domain.com/admin/oauth/onedrive/callback
   ```
4. Check "Access tokens" and "ID tokens"
5. Click "Save"
6. Go back to "Overview" and copy **Application (client) ID**

## Using Cloud Backup

### Quick Start Checklist

- [ ] Set developer password in .env (optional but recommended)
- [ ] Create OAuth apps for each service you want
- [ ] Access Admin > Cloud Backup > Credentials
- [ ] Enter developer password and unlock
- [ ] Paste OAuth credentials and save
- [ ] Connect each service from Cloud Backup page
- [ ] Set backup schedule
- [ ] Test with "Backup Now" button

### Manual Backup

Once at least one service is configured:
1. Go to **Cloud Backup** page
2. Click **"Backup Now"** button
3. Wait for completion
4. Check status - shows per-service success/failure
5. Verify backup appears in cloud storage

### Scheduled Backups

1. On **Cloud Backup** page, find **"Backup Schedule"** section
2. Select **Frequency**: Hourly, Daily, Weekly, or Monthly
3. Select **Time** (UTC timezone)
4. Click **"Save Schedule"**
5. Backups automatically run at scheduled times

**Example:** Daily at 2:00 AM UTC
- Frequency: Daily
- Time: 02:00
- Save

### Disconnecting Services

1. On **Cloud Backup** page, find the service card
2. Click **"Disconnect"** button
3. Confirm deletion
4. Token is removed
5. Service will no longer receive backups

### Updating Credentials

1. Go to **Cloud Backup** → **Credentials**
2. Enter developer password
3. Click **"Unlock"**
4. Update the credentials (can edit individual fields)
5. Click **"Save Credentials"**
6. Existing connections remain active

## Database Schema

The `settings` table stores configuration:

```sql
-- Credentials (access controlled by developer password)
google_oauth_client_id          -- OAuth app client ID
google_oauth_client_secret      -- OAuth app secret
dropbox_oauth_client_id         -- Dropbox app key
dropbox_oauth_client_secret     -- Dropbox app secret
onedrive_oauth_client_id        -- Azure application ID
onedrive_oauth_client_secret    -- Azure secret value

-- Backup schedule
backup_frequency                -- 'hourly'|'daily'|'weekly'|'monthly'
backup_hour                     -- '0'-'23' (UTC hour)

-- OAuth tokens (from connected services)
google_drive_token              -- Access token from Google
dropbox_token                   -- Access token from Dropbox
onedrive_token                  -- Access token from Microsoft

-- Last backup status
last_backup_info                -- JSON with results and timestamps
```

## Backup Contents

Each backup file includes:
- ✓ Complete SQLite database file
- ✓ All family records and contact information
- ✓ Complete check-in/check-out history
- ✓ All events and schedules
- ✓ System configuration and settings
- ✓ User preferences and branding
- ✓ All administrator settings

**Size Estimate:** Usually 1-10 MB depending on history length

**Encryption:** Data encrypted in transit via HTTPS/TLS

## Troubleshooting

### "Credentials are locked"

**Problem:** Can't edit credentials page.

**Solution:** 
1. Scroll to "Access Control" section
2. Enter developer password
3. Click "Unlock"
4. Input fields now editable
5. Edit and click "Save Credentials"
6. Auto-locks after you're done

### "OAuth credentials not configured"

**Problem:** "Connect [Service]" button shows error.

**Solution:**
1. Go to Cloud Backup → Credentials
2. Unlock with developer password
3. Make sure Client ID field is not empty
4. Make sure Client Secret field is not empty
5. Click "Save Credentials"
6. Return to Cloud Backup and try connecting again

### "Invalid developer password"

**Problem:** Wrong password when trying to unlock.

**Solution:**
1. Check .env file for DEVELOPER_PASSWORD value
2. Enter exact password (case-sensitive)
3. If forgotten, update .env on server:
   ```bash
   nano /var/www/youth-secure-checkin/.env
   DEVELOPER_PASSWORD=new-password
   sudo systemctl restart youth-secure-checkin.service
   ```

### "Token exchange failed"

**Problem:** OAuth flow starts but fails during authorization.

**Solution:**
1. Verify **Redirect URI exactly matches** (including https:// and /callback ending)
2. Check URL in browser matches configured redirect URI
3. Verify OAuth app credentials are copied correctly
4. Check application logs for error details
5. Try creating a new OAuth app

### "Backup completed with issues"

**Problem:** Backup runs but shows failure for a service.

**Solution:**
1. Check if that service's credentials are still valid
2. Verify token hasn't been revoked in that service's settings
3. Check cloud storage quota (may be full)
4. Check service-specific API rate limits
5. Disconnect and reconnect the service

### Scheduled backups not running

**Problem:** Backup schedule time passes but nothing happens.

**Solution:**
1. Verify at least one cloud service is connected
2. Check that you've saved the backup schedule
3. Check application logs:
   ```bash
   sudo journalctl -u youth-secure-checkin.service -f
   ```
4. Try manual "Backup Now" button to test connectivity
5. Verify APScheduler is running (check logs)

## API Routes

Available endpoints for cloud backup:

| Route | Method | Purpose | Auth |
|-------|--------|---------|------|
| `/admin/cloud-backup/credentials` | GET/POST | Configure OAuth credentials | ✓ |
| `/admin/cloud-backup` | GET/POST | Configure backups & schedule | ✓ |
| `/admin/backup/now` | POST | Manual backup trigger | ✓ |
| `/admin/oauth/google` | GET | Start Google OAuth | ✓ |
| `/admin/oauth/google/callback` | GET | Google OAuth callback | ✓ |
| `/admin/oauth/dropbox` | GET | Start Dropbox OAuth | ✓ |
| `/admin/oauth/dropbox/callback` | GET | Dropbox OAuth callback | ✓ |
| `/admin/oauth/onedrive` | GET | Start OneDrive OAuth | ✓ |
| `/admin/oauth/onedrive/callback` | GET | OneDrive OAuth callback | ✓ |
| `/admin/cloud-backup/disconnect/<service>` | POST | Disconnect service | ✓ |

## Security Best Practices

✓ **Developer Password:** Set a strong DEVELOPER_PASSWORD in .env
✓ **HTTPS Only:** All URLs must use https:// in production
✓ **Database Encryption:** Enable database encryption at rest (optional but recommended)
✓ **Access Control:** Only admin users can access these settings
✓ **Token Rotation:** Periodically disconnect and reconnect to refresh tokens
✓ **Scope Limitation:** OAuth apps limited to backup-only permissions
✓ **Environment Variables:** No OAuth credentials in .env - only DEVELOPER_PASSWORD

## Production Deployment

### Step 1: Pull Latest Code
```bash
cd /var/www/youth-secure-checkin
git pull
```

### Step 2: Install Packages
```bash
pip install -r requirements.txt --upgrade
```

### Step 3: Set Developer Password (Recommended)
```bash
nano .env
# Add or update:
DEVELOPER_PASSWORD=your-very-secure-password-here
```

### Step 4: Restart Service
```bash
sudo systemctl restart youth-secure-checkin.service
```

### Step 5: Verify
```bash
# Check logs
sudo journalctl -u youth-secure-checkin.service -n 20

# Visit in browser
https://your-domain.com/admin/cloud-backup
```

### Step 6: Configure Credentials
1. Click "Credentials" button
2. Enter your developer password
3. Add OAuth credentials from your OAuth apps
4. Save

### Step 7: Connect Services
1. Back on Cloud Backup page
2. Click "Connect" for each service
3. Authorize each OAuth app
4. Set backup schedule
5. Test with "Backup Now"

## Monitoring

### View Last Backup Status
```bash
# SSH to server
ssh user@your-domain.com

# Check database
sqlite3 /var/www/youth-secure-checkin/checkin.db
SELECT value FROM settings WHERE key='last_backup_info';
```

### Check Application Logs
```bash
# View recent logs
sudo journalctl -u youth-secure-checkin.service -n 50

# Follow logs (live)
sudo journalctl -u youth-secure-checkin.service -f
```

### Test Connectivity
1. Go to Admin > Cloud Backup
2. Click "Backup Now"
3. Check per-service status
4. Look for any error messages

## Support

For specific cloud service issues:

- **Google Drive:** [Google Cloud Console Help](https://support.google.com/cloudconsole)
- **Dropbox:** [Dropbox Developer Docs](https://www.dropbox.com/developers/documentation)
- **OneDrive:** [Microsoft Graph Documentation](https://docs.microsoft.com/en-us/graph)

For application issues:
- Check logs: `sudo journalctl -u youth-secure-checkin.service -f`
- Check credentials are saved in database
- Verify developer password is set correctly
- Test manual backup first before relying on scheduled backups
