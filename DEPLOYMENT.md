# Deployment Guide for Troop Check-in App

## Prerequisites
- Python 3.8+ installed on your server
- Web server with domain/subdomain configured
- SSH access to your server

## Option 1: Deploy to PythonAnywhere (Easiest)

PythonAnywhere offers free hosting for Python web apps.

1. **Create a PythonAnywhere account** at https://www.pythonanywhere.com

2. **Upload your files:**
   - Go to Files tab
   - Create a new directory: `/home/yourusername/troop_checkin`
   - Upload all files from your local `troop_checkin/` folder

3. **Set up a virtual environment:**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 troop_checkin
   pip install flask icalendar pytz requests
   ```

4. **Configure the web app:**
   - Go to Web tab → Add a new web app
   - Choose "Manual configuration" → Python 3.10
   - Set source code directory: `/home/yourusername/troop_checkin`
   - Edit WSGI configuration file and replace contents with:
   ```python
   import sys
   path = '/home/yourusername/troop_checkin'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```

5. **Reload** your web app and visit your URL!

---

## Option 2: Deploy to Your Own Server (VPS/Dedicated)

### Step 1: Prepare Your Server

SSH into your server and install dependencies:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y
```

### Step 2: Upload Your Application

```bash
# On your local machine, from the troop_checkin directory:
scp -r * user@your-server-ip:/var/www/troop_checkin/
```

Or use git:
```bash
# On your server:
cd /var/www/
git clone <your-repo-url> troop_checkin
cd troop_checkin
```

### Step 3: Set Up Python Environment

```bash
cd /var/www/troop_checkin
python3 -m venv venv
source venv/bin/activate
pip install flask icalendar pytz requests gunicorn
```

### Step 4: Configure Gunicorn (Production WSGI Server)

Create `/var/www/troop_checkin/wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

Create systemd service `/etc/systemd/system/troop_checkin.service`:
```ini
[Unit]
Description=Troop Check-in Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/troop_checkin
Environment="PATH=/var/www/troop_checkin/venv/bin"
ExecStart=/var/www/troop_checkin/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start troop_checkin
sudo systemctl enable troop_checkin
```

### Step 5: Configure Nginx

Create `/etc/nginx/sites-available/troop_checkin`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/troop_checkin/static;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/troop_checkin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Set Up SSL (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Option 3: Deploy to Heroku

1. **Install Heroku CLI** and login:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   heroku login
   ```

2. **Prepare your app** - Create these files in your `troop_checkin/` directory:

   `Procfile`:
   ```
   web: gunicorn app:app
   ```

   `requirements.txt`:
   ```
   flask
   icalendar
   pytz
   requests
   gunicorn
   ```

   `runtime.txt`:
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   cd troop_checkin
   git init
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

---

## Option 4: Deploy to DigitalOcean App Platform

1. Push your code to GitHub
2. Connect DigitalOcean to your GitHub repo
3. Configure build:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn app:app`
4. Deploy!

---

## Important Security Notes

### Before Going Live:

1. **Change the secret key in app.py:**
   ```python
   app.secret_key = 'your-very-long-random-secret-key-here'
   ```
   Generate a secure key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Change the developer password:**
   In `app.py`, update:
   ```python
   DEVELOPER_PASSWORD = 'your-new-secure-developer-password'
   ```

3. **Change the default user password:**
   Once deployed, immediately go to Admin → Settings and change from `traillife2024`

4. **Set Flask to production mode:**
   ```python
   # In app.py, change:
   if __name__ == '__main__':
       app.run(debug=False, host='0.0.0.0', port=8000)
   ```

5. **Use HTTPS:** Always use SSL/TLS certificates (Let's Encrypt is free)

---

## Database Persistence

The SQLite database (`checkin.db`) stores all your data. Make sure to:

1. **Backup regularly:**
   ```bash
   cp checkin.db checkin_backup_$(date +%Y%m%d).db
   ```

2. **Set proper permissions:**
   ```bash
   chmod 664 checkin.db
   chown www-data:www-data checkin.db
   ```

3. **For production**, consider migrating to PostgreSQL or MySQL for better concurrent access

---

## Updating Your App

When you make changes:

1. **PythonAnywhere:** Upload new files and reload web app
2. **Your server:**
   ```bash
   cd /var/www/troop_checkin
   git pull  # or upload new files
   sudo systemctl restart troop_checkin
   ```
3. **Heroku:** `git push heroku main`

---

## Troubleshooting

### App won't start
- Check logs: `sudo journalctl -u troop_checkin -n 50`
- Verify Python packages: `pip list`
- Check file permissions

### Database errors
- Ensure checkin.db is writable: `chmod 664 checkin.db`
- Check ownership: `chown www-data:www-data checkin.db`

### iCal sync not working
- Verify iCal URL is accessible from your server
- Check firewall allows outbound HTTPS connections
- Review logs for sync errors

---

## Need Help?

- **Flask docs:** https://flask.palletsprojects.com/
- **Gunicorn docs:** https://gunicorn.org/
- **Nginx docs:** https://nginx.org/en/docs/
- **PythonAnywhere help:** https://help.pythonanywhere.com/
