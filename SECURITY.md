# Youth Secure Check-in - Security Guide

## 🔐 Security Overview

Youth Secure Check-in implements multiple authentication levels to protect child safety while maintaining operational flexibility.

## 🎯 Authentication Levels

### 1. App Password (Primary Access)
- **Purpose**: Day-to-day check-in operations
- **Set during**: Initial setup wizard
- **Changeable**: Yes, through Admin → Security settings
- **Who needs it**: Volunteers, staff, authorized users

### 2. Admin Override Password
- **Purpose**: Administrative functions and settings
- **Set during**: Initial setup wizard
- **Changeable**: Yes, through Admin → Security settings
- **Who needs it**: Organization administrators only

### 3. Developer Password (Backup Access)
- **Purpose**: Emergency recovery if passwords are forgotten
- **Set in**: `.env` file (`DEVELOPER_PASSWORD`)
- **Changeable**: Yes, edit `.env` file
- **Who needs it**: System administrator only

## 🚀 Initial Setup Security

### First-Time Login

**Docker Deployment:**
```bash
# Start application
docker-compose up -d

# Access at http://localhost:5000
# Complete 4-step setup wizard
```

**Manual Deployment:**
```bash
# Start application
python app.py

# Access at http://localhost:5000
# Complete 4-step setup wizard
```

### Setup Wizard Steps

1. **Organization Details**: Configure name, type, branding
2. **Color Scheme**: Customize appearance
3. **Access Codes**: Set secure passwords
4. **Event Settings**: Configure calendar options

### Generating Strong Passwords

**PowerShell:**
```powershell
# Generate 32-character password
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Python:**
```python
import secrets
print(secrets.token_hex(32))
```

**Bash/Linux:**
```bash
openssl rand -base64 32
```

## 🔑 Environment Variables

### Required Security Variables

Create `.env` file with:

```bash
# Secret key for session encryption (64+ characters)
SECRET_KEY=your-generated-secret-key-here

# Developer backup password
DEVELOPER_PASSWORD=your-secure-developer-password-here
```

### Docker Environment

When using Docker, copy the template:

```bash
cp .env.docker .env
# Edit .env with your secure values
```

**⚠️ CRITICAL**: Never commit `.env` files to Git (already in .gitignore)

## 🛡️ Security Best Practices

### Password Management

- ✅ **Use strong, random passwords** (32+ characters recommended)
- ✅ **Change default passwords** immediately after setup
- ✅ **Keep developer password separate** from app password
- ✅ **Store passwords securely** (password manager recommended)
- ✅ **Rotate passwords periodically** (every 90-180 days)
- ❌ **Never share passwords** via email or messaging apps
- ❌ **Never use same password** for multiple systems

### Access Control

**App Password:**
- Share with authorized volunteers
- Change if compromised
- Update after staff changes

**Admin Override:**
- Limit to 2-3 administrators
- Required for sensitive operations
- Change quarterly or when admin changes

**Developer Password:**
- System administrator only
- Use only for emergency recovery
- Store in secure location (password manager)

### Checkout Security

**QR Codes:**
- Unique code per check-in
- Expires after use
- Displayed on-screen only

**Label Printing:**
- Physical security tokens
- One-time use codes
- Destroy after pickup

### Authorized Adults

- Configure per family
- Restrict who can pick up children
- Update as family situations change
- Admin Panel → Families → Edit Family

## 🌐 Production Deployment Security

### SSL/TLS Configuration

**Never run production without HTTPS!**

**Recommended Options:**

1. **Caddy** (easiest):
   - Automatic Let's Encrypt certificates
   - Zero configuration SSL
   - Automatic renewal

2. **Cloudflare Tunnel**:
   - Free SSL with DDoS protection
   - No firewall configuration needed
   - Global CDN

3. **Nginx + Let's Encrypt**:
   - Traditional reverse proxy
   - Manual certificate management
   - Full control

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed setup.

### Server Security

**Firewall Configuration:**
```bash
# Allow only necessary ports
# SSH (22), HTTP (80), HTTPS (443)
```

**Docker Security:**
```bash
# Keep images updated
docker-compose pull
docker-compose up -d

# Check for vulnerabilities
docker scan mrcrunchybeans/youth-secure-checkin:latest
```

**System Updates:**
```bash
# Update host system regularly
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
```

### Backup Security

**Built-in AES-256 Encryption:**

Youth Secure Check-in includes built-in backup encryption to protect sensitive child information:

1. **Enable Encryption:**
   - Go to **Admin → Backups**
   - Find the **"Backup Encryption"** section
   - Enter an encryption password (minimum 8 characters)
   - Click **"Enable"**

2. **All new backups are automatically encrypted** with AES-256 encryption
3. **Encrypted backups show a green shield icon** in the backup list
4. **To restore an encrypted backup**, the system uses the configured password automatically

**Important Notes:**
- Store your encryption password securely (password manager recommended)
- If you lose the encryption password, encrypted backups cannot be restored
- Existing unencrypted backups are not retroactively encrypted
- You can change or disable encryption at any time from the Backups page

**Opening Encrypted Backups Externally:**

Encrypted backup ZIP files can be opened with standard tools that support AES encryption:
- **Windows**: 7-Zip, WinRAR
- **macOS**: The Unarchiver, Keka
- **Linux**: 7z command-line tool

**Legacy Manual Backup (Optional):**

For additional security layers, you can still create manual encrypted backups:
```bash
# Create additional encrypted backup
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
gpg -c backup-$(date +%Y%m%d).tar.gz
docker-compose up -d
```

## 🚨 Security Incident Response

### If Passwords Are Compromised

1. **Immediate Action**:
   - Change app password via Admin → Security
   - Clear all active check-ins
   - Review check-in history for anomalies

2. **Recovery**:
   - Use developer password if locked out
   - Reset all checkout codes
   - Notify authorized users of new passwords

3. **Prevention**:
   - Review who has access
   - Update security procedures
   - Consider rotating all passwords

### If System Is Breached

1. **Stop the application**:
   ```bash
   docker-compose down
   ```

2. **Investigate**:
   - Review logs: `docker-compose logs`
   - Check database for unauthorized changes
   - Examine check-in history

3. **Restore**:
   - Restore from clean backup
   - Change all passwords
   - Update system and dependencies

4. **Notify**:
   - Inform organization leadership
   - Alert families if child data affected
   - Document incident

## 📋 Security Checklist

### Pre-Production

- [ ] Generated strong `SECRET_KEY` (64+ characters)
- [ ] Set unique `DEVELOPER_PASSWORD`
- [ ] Completed setup wizard with strong passwords
- [ ] Configured SSL/TLS (HTTPS)
- [ ] Tested backup and restore procedures
- [ ] Removed default/demo credentials
- [ ] Verified `.env` not in Git repository
- [ ] Configured firewall rules

### Regular Maintenance

- [ ] Update Docker images monthly: `docker-compose pull`
- [ ] Rotate passwords quarterly
- [ ] Review authorized users list
- [ ] Test backup restore procedure
- [ ] Check logs for suspicious activity
- [ ] Update server OS and dependencies
- [ ] Verify SSL certificate renewal

### After Incidents

- [ ] Change all passwords immediately
- [ ] Review access logs
- [ ] Restore from backup if needed
- [ ] Document incident details
- [ ] Update security procedures
- [ ] Notify affected parties

## 🆘 Emergency Recovery

### Forgot All Passwords

Use developer password from `.env` file:

**Docker:**
```bash
# View your developer password
cat .env | grep DEVELOPER_PASSWORD

# Login with that password
# Then reset app/admin passwords via Admin → Security
```

**Manual:**
```bash
# Check .env file
cat .env | grep DEVELOPER_PASSWORD

# Or check app.py for hardcoded value (legacy)
```

### Lost `.env` File

1. **Stop application**
2. **Copy template**: `cp .env.example .env`
3. **Generate new secrets** (see "Generating Strong Passwords")
4. **Restart application**
5. **Complete setup wizard again**
6. **Restore data from backup** (if needed)

### Database Corruption

```bash
# Stop containers
docker-compose down

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart
docker-compose up -d
```

## 📞 Reporting Security Issues

**Found a vulnerability?**

- 🚨 **DO NOT** open public GitHub issues
- ✅ **DO** use [GitHub Security Advisories](https://github.com/mrcrunchybeans/youth-secure-checkin/security/advisories/new)
- ✅ **DO** provide detailed reproduction steps
- ✅ **DO** allow time for patching before disclosure

## 📚 Additional Resources

- **Deployment Guide**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Docker Guide**: [DOCKER.md](DOCKER.md)
- **Backup Features**: See Admin Panel → Utilities → Export Data
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)

---

**Security is everyone's responsibility. Stay vigilant! 🛡️**
