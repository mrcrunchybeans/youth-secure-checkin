# YOURLS URL Shortener Setup

YOURLS (Your Own URL Shortener) creates short, branded URLs for checkout QR codes, making them easier to scan and type manually.

## 🐳 Docker Setup (Recommended)

### Quick Start with Docker Compose

YOURLS is included in the docker-compose setup and starts automatically:

```bash
# Production with YOURLS
docker-compose --profile production up -d

# Demo mode with YOURLS (already included)
docker-compose -f docker-compose.demo.yml up -d
```

**Services started:**
- `youth-checkin` or `youth-checkin-demo` - Main application (port 5000)
- `yourls` - URL shortener (port 8080)
- `yourls-db` - MySQL database for YOURLS

### Initial YOURLS Configuration

1. **Access YOURLS admin panel:**
   - Production: http://localhost:8080/admin
   - Demo: http://localhost:8080/admin
   - Default credentials: `admin` / `admin` (change in `.env` file)

2. **Complete YOURLS installation:**
   - Visit http://localhost:8080/admin on first run
   - Click "Install YOURLS" button
   - YOURLS will create database tables automatically

3. **Get your API Signature Token:**
   - In YOURLS admin, go to **Tools → API**
   - Copy your signature token (looks like: `abc123def456`)

4. **Configure Youth Check-in:**
   - Login to Youth Check-in: http://localhost:5000
   - Go to **Admin → Security → URL Shortener (YOURLS)**
   - Enter:
     - **YOURLS API URL:** `http://yourls/yourls-api.php`
     - **API Signature Token:** (paste from step 3)
   - Click **Save YOURLS Settings**

5. **Test the integration:**
   - Check-in a family
   - QR code modal will show a short URL below the QR code
   - Example: `http://localhost:8080/1` instead of full URL

### Environment Variables (.env file)

Create/edit `.env` in project root:

```env
# YOURLS Configuration
YOURLS_DB_PASSWORD=yourlspass
YOURLS_DB_ROOT_PASSWORD=rootpass
YOURLS_USER=admin
YOURLS_PASSWORD=change_this_password

# Youth Check-in
SECRET_KEY=your-secret-key-here
DEVELOPER_PASSWORD=your-dev-password
```

### Docker Profiles

- `production` - Includes YOURLS by default
- `demo` - Includes YOURLS by default
- `with-yourls` - Standalone YOURLS profile

### Custom Domain Setup

To use your own domain (e.g., `yourl.ink`):

1. Update `docker-compose.yml`:
   ```yaml
   yourls:
     environment:
       - YOURLS_SITE=https://yourl.ink  # Your domain
   ```

2. Configure reverse proxy (Nginx/Traefik) to route domain to port 8080

3. Update Youth Check-in settings with your domain

---

## 💻 Bare Metal Setup

### Prerequisites

- Apache or Nginx web server
- MySQL 5.7+ or MariaDB 10.3+
- PHP 7.4+ with extensions: `curl`, `gd`, `mbstring`, `mysqli`, `pdo_mysql`

### Installation Steps

#### 1. Download YOURLS

```bash
cd /var/www
sudo wget https://github.com/YOURLS/YOURLS/archive/refs/heads/master.zip
sudo unzip master.zip
sudo mv YOURLS-master yourls
sudo chown -R www-data:www-data yourls
```

#### 2. Create MySQL Database

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE yourls;
CREATE USER 'yourls'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON yourls.* TO 'yourls'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Configure YOURLS

```bash
cd /var/www/yourls/user
sudo cp config-sample.php config.php
sudo nano config.php
```

Edit these settings:

```php
<?php
// MySQL settings
define('YOURLS_DB_USER', 'yourls');
define('YOURLS_DB_PASS', 'secure_password_here');
define('YOURLS_DB_NAME', 'yourls');
define('YOURLS_DB_HOST', 'localhost');
define('YOURLS_DB_PREFIX', 'yourls_');

// Site URL
define('YOURLS_SITE', 'http://yourl.ink'); // Your domain or http://localhost/yourls

// Timezone
define('YOURLS_TIMEZONE', 'America/Chicago');

// Username and password
$yourls_user_passwords = array(
    'admin' => 'strong_password_here',
);

// Cookie key (random string)
define('YOURLS_COOKIEKEY', 'random_string_here');
?>
```

#### 4. Apache Virtual Host

Create `/etc/apache2/sites-available/yourls.conf`:

```apache
<VirtualHost *:80>
    ServerName yourl.ink
    DocumentRoot /var/www/yourls

    <Directory /var/www/yourls>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/yourls-error.log
    CustomLog ${APACHE_LOG_DIR}/yourls-access.log combined
</VirtualHost>
```

Enable site:
```bash
sudo a2ensite yourls.conf
sudo a2enmod rewrite
sudo systemctl reload apache2
```

#### 5. Nginx Configuration (Alternative)

Create `/etc/nginx/sites-available/yourls`:

```nginx
server {
    listen 80;
    server_name yourl.ink;
    root /var/www/yourls;
    index index.php;

    location / {
        try_files $uri $uri/ /yourls-loader.php$is_args$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/yourls /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

#### 6. Install YOURLS

Visit http://yourl.ink/admin (or http://localhost/yourls/admin) and click **Install YOURLS**

#### 7. Get API Signature

1. Login to YOURLS admin panel
2. Go to **Tools → API**
3. Copy your signature token

#### 8. Configure Youth Check-in

In Youth Check-in app:
1. Go to **Admin → Security → URL Shortener (YOURLS)**
2. Enter:
   - **YOURLS API URL:** `http://yourl.ink/yourls-api.php` (or `http://localhost/yourls/yourls-api.php`)
   - **API Signature Token:** (paste from step 7)
3. Click **Save YOURLS Settings**

---

## 🔧 Troubleshooting

### YOURLS not accessible

**Docker:**
```bash
docker ps | grep yourls  # Check if containers are running
docker logs youth-checkin-yourls  # Check logs
```

**Bare metal:**
```bash
sudo systemctl status apache2  # or nginx
sudo tail -f /var/log/apache2/yourls-error.log
```

### Database connection errors

**Docker:**
- Wait 30 seconds after first start for MySQL initialization
- Check environment variables in docker-compose.yml

**Bare metal:**
- Verify MySQL credentials in config.php
- Test connection: `mysql -u yourls -p yourls`

### Short URLs not working

1. Check YOURLS API URL in Youth Check-in settings
2. Verify signature token is correct
3. Test YOURLS API manually:
   ```bash
   curl "http://localhost:8080/yourls-api.php?signature=YOUR_TOKEN&action=shorturl&url=https://google.com&format=json"
   ```

### URLs too long for QR codes

Short URLs should be much shorter. If still long:
- Use a shorter domain name
- Check YOURLS_SITE setting matches actual domain
- Verify YOURLS is creating short codes (check in admin panel)

---

## 📊 Monitoring & Maintenance

### View YOURLS Statistics

Access http://localhost:8080/admin to see:
- Total clicks
- Most popular links
- Recent short URLs
- Traffic sources

### Backup YOURLS Data

**Docker:**
```bash
# Backup database
docker exec youth-checkin-yourls-db mysqldump -u yourls -pyourlspass yourls > yourls-backup.sql

# Backup volumes
docker run --rm -v youth-secure-checkin_yourls-data:/data -v $(pwd):/backup alpine tar czf /backup/yourls-data.tar.gz /data
```

**Bare metal:**
```bash
# Backup database
mysqldump -u yourls -p yourls > yourls-backup.sql

# Backup files
tar czf yourls-backup.tar.gz /var/www/yourls
```

### Update YOURLS

**Docker:**
```bash
docker-compose pull yourls
docker-compose up -d yourls
```

**Bare metal:**
```bash
cd /var/www/yourls
sudo -u www-data git pull origin master
```

---

## 🌐 Production Deployment

### SSL/HTTPS Setup

**Docker with Traefik:**
See `DOCKER.md` for Traefik configuration with automatic SSL

**Bare metal with Certbot:**
```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d yourl.ink
```

### Security Hardening

1. **Change default credentials** in `.env` or `config.php`
2. **Restrict admin access** - Add IP whitelist in YOURLS config
3. **Enable private mode** in YOURLS settings (require login to create short URLs)
4. **Regular updates** - Keep YOURLS and dependencies updated
5. **Firewall rules** - Only allow necessary ports (80, 443)

### Performance Optimization

**Enable caching in YOURLS:**
1. Install cache plugin from YOURLS plugin directory
2. Configure Redis/Memcached if high traffic

**Database optimization:**
```sql
-- Run monthly
OPTIMIZE TABLE yourls_url;
OPTIMIZE TABLE yourls_options;
```

---

## 📚 Additional Resources

- **YOURLS Official:** https://yourls.org/
- **YOURLS Documentation:** https://docs.yourls.org/
- **YOURLS Plugins:** https://github.com/YOURLS/awesome-yourls
- **Docker Hub:** https://hub.docker.com/_/yourls

---

## ✅ Verification Checklist

- [ ] YOURLS accessible at http://localhost:8080/admin
- [ ] Can login to YOURLS admin panel
- [ ] API signature token obtained
- [ ] Youth Check-in YOURLS settings saved
- [ ] Test check-in shows short URL in QR modal
- [ ] Short URL redirects correctly when visited
- [ ] QR code scans successfully with short URL
