# Deploying to Hostinger

Hostinger supports Python applications on their **VPS** and **Cloud Hosting** plans. Unfortunately, their shared hosting plans do NOT support Python Flask applications.

## Check Your Hostinger Plan

1. **Shared Hosting (Premium, Business)** → ❌ Does NOT support Python/Flask
2. **VPS Hosting** → ✅ Full support for Python applications
3. **Cloud Hosting** → ✅ Full support for Python applications

---

## If You Have Hostinger VPS or Cloud Hosting

### Step 1: Connect to Your Server via SSH

1. Log into Hostinger control panel (hPanel)
2. Go to **VPS** → **SSH Access**
3. Note your SSH credentials:
   - Host: `your-server-ip`
   - Port: `22` (default)
   - Username: `root` or your username
   - Password: Your SSH password

4. Connect from your local terminal:
   ```bash
   ssh root@your-server-ip
   ```

### Step 2: Prepare the Server

Update system and install required packages:
```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3 python3-pip python3-venv nginx -y

# Install supervisor (for process management)
apt install supervisor -y
```

### Step 3: Upload Your Application

**Option A: Using SCP (from your local machine):**
```bash
cd /workspaces/86075287
scp -r troop_checkin root@your-server-ip:/var/www/
```

**Option B: Using Git (on the server):**
```bash
cd /var/www
git clone https://github.com/yourusername/your-repo.git troop_checkin
cd troop_checkin
```

**Option C: Using Hostinger File Manager:**
1. Compress your `troop_checkin` folder to a ZIP file
2. Upload via hPanel → File Manager
3. Extract in `/var/www/troop_checkin`

### Step 4: Set Up Python Environment

```bash
cd /var/www/troop_checkin

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install flask icalendar pytz requests gunicorn
```

### Step 5: Update Security Settings

Edit `app.py` on the server:
```bash
nano /var/www/troop_checkin/app.py
```

Update these lines:
```python
# Generate a secure secret key first:
# python -c "import secrets; print(secrets.token_hex(32))"
app.secret_key = 'YOUR-GENERATED-SECRET-KEY-HERE'

# Change developer password
DEVELOPER_PASSWORD = 'your-new-secure-developer-password'

# Update the last line to production mode:
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8000)
```

Save with `CTRL+X`, then `Y`, then `Enter`.

### Step 6: Initialize the Database

```bash
cd /var/www/troop_checkin
source venv/bin/activate
python3 -c "from app import init_db; init_db()"

# Set proper permissions
chmod 664 checkin.db
chown www-data:www-data checkin.db
```

### Step 7: Configure Supervisor (Keep App Running)

Create supervisor configuration:
```bash
nano /etc/supervisor/conf.d/troop_checkin.conf
```

Add this content:
```ini
[program:troop_checkin]
directory=/var/www/troop_checkin
command=/var/www/troop_checkin/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/troop_checkin.err.log
stdout_logfile=/var/log/troop_checkin.out.log
```

Start the app:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start troop_checkin
supervisorctl status  # Check it's running
```

### Step 8: Configure Nginx

Create Nginx configuration:
```bash
nano /etc/nginx/sites-available/troop_checkin
```

Add this content (replace `your-domain.com` with your actual domain):
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional: serve static files directly (if you add a static folder)
    location /static {
        alias /var/www/troop_checkin/static;
        expires 30d;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/troop_checkin /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

### Step 9: Point Your Domain

In Hostinger hPanel:
1. Go to **Domains** → **DNS/Nameservers**
2. Add/Update **A Record**:
   - Type: `A`
   - Name: `@` (or subdomain like `checkin`)
   - Points to: Your VPS IP address
   - TTL: 3600

Wait 5-30 minutes for DNS propagation.

### Step 10: Set Up SSL (HTTPS)

Install Let's Encrypt SSL certificate:
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts, enter your email
# Choose option 2 to redirect HTTP to HTTPS
```

Your app is now live at `https://your-domain.com`! 🎉

---

## If You Have Hostinger Shared Hosting

Shared hosting doesn't support Flask, but you have these options:

### Option 1: Upgrade to Hostinger VPS
- **VPS 1:** Starting at ~$4-6/month
- Full server control, run Python apps
- Follow the VPS instructions above

### Option 2: Use PythonAnywhere (Free Tier Available)
1. Keep your domain on Hostinger
2. Host the Flask app on PythonAnywhere
3. Point a subdomain to PythonAnywhere:
   - In Hostinger DNS: Add CNAME record
   - Name: `checkin` (or your subdomain)
   - Points to: `yourusername.pythonanywhere.com`

### Option 3: Use Hostinger for Frontend Only
- Create a simple HTML page on Hostinger
- Host the Flask app elsewhere (PythonAnywhere, Heroku)
- Link from your main site to the app

---

## Updating Your App

When you make changes:

```bash
# SSH into your server
ssh root@your-server-ip

# Navigate to app directory
cd /var/www/troop_checkin

# Pull latest changes (if using git)
git pull

# Or upload new files via SCP/File Manager

# Restart the app
supervisorctl restart troop_checkin
```

---

## Troubleshooting

### Check if app is running:
```bash
supervisorctl status troop_checkin
```

### View logs:
```bash
tail -f /var/log/troop_checkin.out.log
tail -f /var/log/troop_checkin.err.log
```

### Restart services:
```bash
supervisorctl restart troop_checkin
systemctl restart nginx
```

### Database permissions:
```bash
cd /var/www/troop_checkin
chmod 664 checkin.db
chown www-data:www-data checkin.db
```

### Test app locally:
```bash
cd /var/www/troop_checkin
source venv/bin/activate
python app.py
# Visit http://your-server-ip:5000
```

---

## Costs

**Hostinger VPS Pricing (2025):**
- VPS 1: ~$5-8/month (1 vCPU, 4GB RAM) - Perfect for this app
- VPS 2: ~$10-15/month (2 vCPU, 8GB RAM) - Overkill for most troops

**Includes:**
- Full root access
- Your choice of OS (Ubuntu recommended)
- 100 Mbps network
- Free SSL certificate
- Weekly backups (on some plans)

---

## Need Help?

- **Hostinger Support:** Live chat in hPanel (24/7)
- **Hostinger VPS Tutorials:** https://www.hostinger.com/tutorials/vps
- **Check your plan:** Login to hPanel → Check dashboard for "VPS" or "Shared Hosting"
