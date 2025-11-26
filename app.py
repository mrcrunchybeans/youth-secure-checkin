from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests

# Application version
APP_VERSION = "1.0.1"
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
import urllib3
from icalendar import Calendar
import pytz
import csv
import io
import json
import re
import threading
import time
import secrets
import qrcode
from io import BytesIO
import base64
import os
import tempfile
import urllib.parse
import ipaddress
import socket
import zipfile
import shutil
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backup_manager import BackupManager
from tlc_client import TrailLifeConnectClient

# Disable SSL warnings for whitelisted calendar domains
# We disable SSL verification only for pre-approved domains in ALLOWED_ICAL_DOMAINS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# Allowed domains for iCal imports (SSRF protection)
# Add trusted calendar providers here
ALLOWED_ICAL_DOMAINS = [
    # Google Calendar
    'calendar.google.com',
    
    # Microsoft Outlook/Office 365
    'outlook.office365.com',
    'outlook.live.com',
    
    # Apple iCloud
    'calendars.icloud.com',
    'ical.mac.com',
    'p01-caldav.icloud.com',
    'p02-caldav.icloud.com',
    'p03-caldav.icloud.com',
    'p04-caldav.icloud.com',
    'p05-caldav.icloud.com',
    'p06-caldav.icloud.com',
    'p07-caldav.icloud.com',
    'p08-caldav.icloud.com',
    
    # Trail Life USA
    'traillifeconnect.com',
    'www.traillifeconnect.com',
    
    # Church Management Systems
    'planningcenteronline.com',
    'api.planningcenteronline.com',
    'churchcenter.com',
    'breezechms.com',
    'secure.breezechms.com',
    'elvanto.com',
    'elvanto.net',
    'subsplash.com',
    'pushpay.com',
    
    # Other Calendar Services
    'calendar.yahoo.com',
    'zimbra.free-av.de',
    'calendar.zoho.com',
    'fastmail.com',
    'protonmail.com',
    'tutanota.com',
]

# Optional label printing support
try:
    from label_printer import generate_unique_code, print_checkout_label
    LABEL_PRINTING_AVAILABLE = True
except ImportError:
    LABEL_PRINTING_AVAILABLE = False
    print("Warning: Label printing libraries not available. Install Pillow to enable this feature.")

def normalize_address(address):
    if not address:
        return ''
    # Lower case
    addr = address.lower()
    # Remove punctuation
    addr = re.sub(r'[^\w\s]', '', addr)
    # Replace abbreviations
    addr = re.sub(r'\bst\b', 'street', addr)
    addr = re.sub(r'\bsr\b', 'street', addr)
    addr = re.sub(r'\bave\b', 'avenue', addr)
    addr = re.sub(r'\brd\b', 'road', addr)
    addr = re.sub(r'\bdr\b', 'drive', addr)
    # Replace directional abbreviations
    addr = re.sub(r'\bn\b', 'north', addr)
    addr = re.sub(r'\bs\b', 'south', addr)
    addr = re.sub(r'\be\b', 'east', addr)
    addr = re.sub(r'\bw\b', 'west', addr)
    # Replace multiple spaces with one
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr

# Database path - use DATABASE_PATH env var if set (for demo), otherwise default location
if os.getenv('DATABASE_PATH'):
    DB_PATH = Path(os.getenv('DATABASE_PATH'))
else:
    # Use /app/data for Docker containers, otherwise use local directory
    DATA_DIR = Path(__file__).parent / 'data'
    if DATA_DIR.exists() and DATA_DIR.is_dir():
        # Running in Docker or with data directory
        DB_PATH = DATA_DIR / 'checkin.db'
    else:
        # Running locally without data directory
        DB_PATH = Path(__file__).parent / 'checkin.db'

def get_db():
    db_path = app.config.get('DATABASE', DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(app.config.get('DATABASE', DB_PATH))
    conn.row_factory = sqlite3.Row
    schema_path = Path(__file__).parent / 'schema.sql'
    if schema_path.exists():
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-for-local')  # override in prod with env var

# Trust proxy headers for HTTPS detection behind reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# File upload configuration
UPLOAD_FOLDER = Path(__file__).parent / 'static' / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Make version, current year, and footer settings available to all templates
@app.context_processor
def inject_version():
    try:
        conn = get_db()
        
        # Get footer settings
        footer_enabled_row = conn.execute("SELECT value FROM settings WHERE key = 'footer_enabled'").fetchone()
        footer_enabled = footer_enabled_row[0] == 'True' if footer_enabled_row else True
        
        footer_text_row = conn.execute("SELECT value FROM settings WHERE key = 'footer_text'").fetchone()
        footer_text = footer_text_row[0] if footer_text_row else ''
        
        footer_show_github_row = conn.execute("SELECT value FROM settings WHERE key = 'footer_show_github'").fetchone()
        footer_show_github = footer_show_github_row[0] == 'True' if footer_show_github_row else True
        
        footer_show_version_row = conn.execute("SELECT value FROM settings WHERE key = 'footer_show_version'").fetchone()
        footer_show_version = footer_show_version_row[0] == 'True' if footer_show_version_row else True
        
        footer_show_admin_link_row = conn.execute("SELECT value FROM settings WHERE key = 'footer_show_admin_link'").fetchone()
        footer_show_admin_link = footer_show_admin_link_row[0] == 'True' if footer_show_admin_link_row else True
        
        conn.close()
        
        return {
            'app_version': APP_VERSION,
            'current_year': datetime.now().year,
            'footer_enabled': footer_enabled,
            'footer_text': footer_text,
            'footer_show_github': footer_show_github,
            'footer_show_version': footer_show_version,
            'footer_show_admin_link': footer_show_admin_link
        }
    except:
        # Fallback if database isn't available yet
        return {
            'app_version': APP_VERSION,
            'current_year': datetime.now().year,
            'footer_enabled': True,
            'footer_text': '',
            'footer_show_github': True,
            'footer_show_version': True,
            'footer_show_admin_link': True
        }

# Get timezone from database, default to America/Chicago
def get_timezone():
    try:
        conn = get_db()
        row = conn.execute("SELECT value FROM settings WHERE key = 'timezone'").fetchone()
        conn.close()
        if row:
            return pytz.timezone(row[0])
    except:
        pass
    return pytz.timezone('America/Chicago')

local_tz = get_timezone()

# Developer password from environment variable for security
# Falls back to None if not set (disables developer override features)
DEVELOPER_PASSWORD = os.getenv('DEVELOPER_PASSWORD', None)

# Initialize scheduled backup
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.start()
except ImportError:
    scheduler = None
    app.logger.warning("APScheduler not installed. Scheduled backups disabled.")

# Initialize Backup Manager
backup_manager = BackupManager(
    db_path=str(Path(__file__).parent / 'checkin.db'),
    backup_dir=str(Path(__file__).parent / 'data' / 'backups'),
    uploads_dir=str(Path(__file__).parent / 'uploads'),
    static_uploads_dir=str(Path(__file__).parent / 'static' / 'uploads')
)

@app.context_processor
def inject_branding():
    """Make branding settings available to all templates"""
    demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
    demo_banner = None
    if demo_mode:
        conn = get_db()
        cur = conn.execute("SELECT value FROM settings WHERE key = 'demo_banner'")
        row = cur.fetchone()
        demo_banner = row['value'] if row else 'This is a demonstration instance. Data resets periodically.'
        conn.close()
    
    return {
        'branding': get_branding_settings(),
        'demo_mode': demo_mode,
        'demo_banner': demo_banner
    }

@app.before_request
def check_setup():
    """Check if initial setup is needed and redirect if necessary"""
    # Skip check for static files and setup route itself
    if request.endpoint and (request.endpoint == 'static' or request.endpoint == 'setup'):
        return
    
    # Skip setup check in demo mode - database is pre-configured
    if os.getenv('DEMO_MODE', 'false').lower() == 'true':
        return
    
    # Check if setup is complete
    try:
        conn = get_db()
        cur = conn.execute("SELECT value FROM settings WHERE key = 'is_setup_complete'")
        row = cur.fetchone()
        conn.close()
        
        is_complete = row['value'] if row else 'false'
        
        # Redirect to setup if not complete
        if is_complete != 'true':
            return redirect(url_for('setup'))
    except:
        # If database doesn't exist or there's an error, allow access to continue
        pass

def ensure_db():
    # kept for manual invocation; do not run at import time so tests can control DB_PATH
    if not DB_PATH.exists():
        init_db()

def get_app_password():
    """Get the app password from settings, or return default"""
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'app_password'")
    row = cur.fetchone()
    conn.close()
    return row['value'] if row else 'changeme'

def set_app_password(password):
    """Set the app password in settings"""
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('app_password', ?)", (password,))
    conn.commit()
    conn.close()

def get_override_password():
    """Get the admin override checkout password from settings, or return app password as default"""
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'admin_override_password'")
    row = cur.fetchone()
    conn.close()
    # If no override password set, fall back to app password for backward compatibility
    return row['value'] if row else get_app_password()

def set_override_password(password):
    """Set the admin override checkout password in settings"""
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('admin_override_password', ?)", (password,))
    conn.commit()
    conn.close()

def check_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_logo_filename():
    """Get the current logo filename from settings"""
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'logo_filename'")
    row = cur.fetchone()
    conn.close()
    return row['value'] if row else None

def set_logo_filename(filename):
    """Set the logo filename in settings"""
    conn = get_db()
    if filename:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('logo_filename', ?)", (filename,))
    else:
        conn.execute("DELETE FROM settings WHERE key = 'logo_filename'")
    conn.commit()
    conn.close()

def get_favicon_filename():
    """Get the current favicon filename from settings"""
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'favicon_filename'")
    row = cur.fetchone()
    conn.close()
    return row['value'] if row else None

def set_favicon_filename(filename):
    """Set the favicon filename in settings"""
    conn = get_db()
    if filename:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('favicon_filename', ?)", (filename,))
    else:
        conn.execute("DELETE FROM settings WHERE key = 'favicon_filename'")
    conn.commit()
    conn.close()

def get_branding_settings():
    """Get all branding/customization settings for templates"""
    conn = get_db()
    settings = {}
    defaults = {
        'organization_name': 'Check-In System',
        'organization_type': 'other',
        'primary_color': '#79060d',
        'secondary_color': '#003b59',
        'accent_color': '#4a582d',
        'group_term': 'Group',
        'group_term_lower': 'group',
        'favicon_filename': None,
    }
    
    for key, default in defaults.items():
        cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        settings[key] = row['value'] if row else default
    
    conn.close()
    return settings

def set_branding_setting(key, value):
    """Update a branding setting"""
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_smtp_settings():
    """Get all SMTP settings from database"""
    conn = get_db()
    settings = {}
    keys = ['smtp_server', 'smtp_port', 'smtp_from', 'smtp_username', 'smtp_password', 'smtp_use_tls']
    
    for key in keys:
        cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        settings[key] = row['value'] if row else None
    
    conn.close()
    return settings

def set_smtp_settings(smtp_dict):
    """Save SMTP settings to database"""
    conn = get_db()
    for key, value in smtp_dict.items():
        if key.startswith('smtp_') and value is not None:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def send_email(to_address, subject, html_body, plain_text_body=None):
    """Send an email using configured SMTP settings.
    
    Args:
        to_address: Recipient email address
        subject: Email subject line
        html_body: HTML content of email
        plain_text_body: Plain text fallback (optional)
    
    Returns:
        Tuple of (success, message)
    """
    try:
        smtp_settings = get_smtp_settings()
        
        # Validate SMTP settings are configured
        if not all([smtp_settings.get('smtp_server'), 
                    smtp_settings.get('smtp_port'),
                    smtp_settings.get('smtp_from'),
                    smtp_settings.get('smtp_username'),
                    smtp_settings.get('smtp_password')]):
            return False, "SMTP settings not configured. Please configure SMTP in admin settings."
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_settings['smtp_from']
        msg['To'] = to_address
        
        # Attach plain text and HTML versions
        if plain_text_body:
            msg.attach(MIMEText(plain_text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Connect to SMTP server
        use_tls = smtp_settings.get('smtp_use_tls', 'false') == 'true'
        port = int(smtp_settings.get('smtp_port', 587))
        
        if use_tls:
            server = smtplib.SMTP(smtp_settings['smtp_server'], port, timeout=10)
            server.starttls()
        else:
            # For SSL, use SMTP_SSL
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_settings['smtp_server'], port, timeout=10)
            else:
                server = smtplib.SMTP(smtp_settings['smtp_server'], port, timeout=10)
        
        # Login and send
        server.login(smtp_settings['smtp_username'], smtp_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True, f"Email sent successfully to {to_address}"
    
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP Authentication failed. Check username and password."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def get_event_date_range_months():
    """Get the number of months (past and future) to show events for. Default is 1 month."""
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'event_date_range_months'")
    row = cur.fetchone()
    conn.close()
    
    if row and row['value']:
        try:
            return int(row['value'])
        except (ValueError, TypeError):
            return 1
    return 1

def parse_concat_list(concat_str, separator=':'):
    """Parse GROUP_CONCAT result into a list of dicts.
    
    Args:
        concat_str: String from GROUP_CONCAT like "1:name:notes,2:name2:notes2"
        separator: Field separator within each item (default ':')
    
    Returns:
        List of tuples with parsed values
    """
    if not concat_str:
        return []
    
    items = []
    for item_str in concat_str.split(','):
        parts = item_str.split(separator)
        items.append(parts)
    return items

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_authenticated():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def generate_share_token():
    """Generate a secure random token for sharing checkout codes.
    Using 6 bytes results in an 8-character URL-safe string.
    This is short enough for simple QR codes without needing an external shortener,
    while still providing sufficient entropy for temporary tokens.
    """
    return secrets.token_urlsafe(6)

def create_qr_code(url):
    """Generate a QR code image as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

def cleanup_expired_tokens():
    """Remove expired share tokens from database"""
    conn = get_db()
    now = datetime.utcnow().isoformat()
    conn.execute("DELETE FROM share_tokens WHERE expires_at < ? OR used = 1", (now,))
    conn.commit()
    conn.close()

def safe_http_get(url, timeout=10, max_size=10*1024*1024):
    """
    Perform a safe HTTP GET request with SSRF protection.
    Validates that the domain is in ALLOWED_ICAL_DOMAINS.
    """
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    
    # Basic SSRF protection: only allow whitelisted domains
    allowed = False
    for allowed_domain in ALLOWED_ICAL_DOMAINS:
        if domain == allowed_domain or domain.endswith('.' + allowed_domain):
            allowed = True
            break
            
    if not allowed:
        # Also allow localhost for testing if needed, or just fail
        # For now, strict whitelist
        raise ValueError(f"Domain {domain} is not in the allowed list")
        
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()
    
    content = b''
    for chunk in response.iter_content(chunk_size=8192):
        content += chunk
        if len(content) > max_size:
            raise ValueError("Response too large")
            
    return content

def sync_ical_events():
    """Sync events from iCal URL - can be called manually or automatically"""
    try:
        with app.app_context():
            conn = get_db()
            cur = conn.execute("SELECT value FROM settings WHERE key = 'ical_url'")
            ical_row = cur.fetchone()
            if not ical_row or not ical_row['value']:
                conn.close()
                return False, "No iCal URL set"
            ical_url = ical_row['value']
            conn.close()

            # Use safe HTTP request with SSRF protection
            content = safe_http_get(ical_url, timeout=10, max_size=10*1024*1024)
            cal = Calendar.from_ical(content.decode('utf-8'))

            conn = get_db()
            # Track events from calendar to identify which ones to keep
            calendar_events = []
            event_count = 0
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    name = str(component.get('summary', 'Event'))
                    start_dt = component.get('dtstart')
                    end_dt = component.get('dtend')
                    start_time = None
                    end_time = None
                    if start_dt:
                        dt = start_dt.dt
                        if hasattr(dt, 'tzinfo') and dt.tzinfo:
                            dt = dt.astimezone(local_tz)
                        else:
                            dt = local_tz.localize(dt)
                        start_time = dt.isoformat()
                    if end_dt:
                        dt = end_dt.dt
                        if hasattr(dt, 'tzinfo') and dt.tzinfo:
                            dt = dt.astimezone(local_tz)
                        else:
                            dt = local_tz.localize(dt)
                        end_time = dt.isoformat()
                    description = str(component.get('description', ''))
                    
                    # Check if event already exists (match by name and start_time)
                    existing = conn.execute(
                        "SELECT id FROM events WHERE name = ? AND start_time = ?",
                        (name, start_time)
                    ).fetchone()
                    
                    if existing:
                        # Update existing event
                        conn.execute(
                            "UPDATE events SET end_time = ?, description = ? WHERE id = ?",
                            (end_time, description, existing['id'])
                        )
                        calendar_events.append(existing['id'])
                    else:
                        # Insert new event
                        cursor = conn.execute(
                            "INSERT INTO events (name, start_time, end_time, description) VALUES (?, ?, ?, ?)",
                            (name, start_time, end_time, description)
                        )
                        calendar_events.append(cursor.lastrowid)
                    event_count += 1
            
            # Delete events that are no longer in the calendar (but only old ones with no active check-ins)
            if calendar_events:
                placeholders = ','.join('?' * len(calendar_events))
                conn.execute(f"""
                    DELETE FROM events 
                    WHERE id NOT IN ({placeholders})
                    AND start_time < datetime('now', '-7 days')
                    AND id NOT IN (SELECT DISTINCT event_id FROM checkins WHERE checkout_time IS NULL)
                """, calendar_events)
            
            conn.commit()

            # Update last sync time
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_ical_sync', ?)",
                        (datetime.utcnow().isoformat(),))
            conn.commit()
            conn.close()
            return True, f"Synced {event_count} events"
    except Exception as e:
        return False, f"Error syncing: {str(e)}"

def auto_sync_ical():
    """Background thread to automatically sync iCal every hour"""
    while True:
        time.sleep(3600)  # Wait 1 hour
        try:
            sync_ical_events()
        except:
            pass  # Silently fail, will try again next hour

# Start background sync thread
sync_thread = threading.Thread(target=auto_sync_ical, daemon=True)
sync_thread.start()

@app.route('/health')
def health():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({'status': 'ok'}), 200

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """First-time setup wizard"""
    # Check if setup is already complete
    conn = get_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = 'is_setup_complete'")
    row = cur.fetchone()
    is_complete = row['value'] if row else 'false'
    
    if is_complete == 'true':
        # Setup already done, redirect to login
        conn.close()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Validate required fields
        org_name = request.form.get('organization_name', '').strip()
        org_type = request.form.get('organization_type', 'other')
        group_term = request.form.get('group_term', 'Group').strip()
        event_date_range_months = request.form.get('event_date_range_months', '1')
        primary_color = request.form.get('primary_color', '#667eea')
        secondary_color = request.form.get('secondary_color', '#764ba2')
        accent_color = request.form.get('accent_color', '#48bb78')
        admin_password = request.form.get('admin_password', '').strip()
        admin_password_confirm = request.form.get('admin_password_confirm', '').strip()
        
        # Validate
        errors = []
        if not org_name:
            errors.append('Organization name is required')
        if len(admin_password) < 4:
            errors.append('Admin password must be at least 4 characters')
        if admin_password != admin_password_confirm:
            errors.append('Admin passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            conn.close()
            return render_template('setup.html')
        
        # Save organization settings
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('organization_name', ?)", (org_name,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('organization_type', ?)", (org_type,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('group_term', ?)", (group_term,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('group_term_lower', ?)", (group_term.lower(),))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('event_date_range_months', ?)", (event_date_range_months,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('primary_color', ?)", (primary_color,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('secondary_color', ?)", (secondary_color,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('accent_color', ?)", (accent_color,))
        
        # Handle favicon upload if provided
        if 'favicon' in request.files:
            file = request.files['favicon']
            if file and file.filename and allowed_file(file.filename, allowed_extensions={'png', 'jpg', 'jpeg', 'ico'}):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                filename = f"favicon_{int(time.time())}{ext}"
                filepath = app.config['UPLOAD_FOLDER'] / filename
                file.save(str(filepath))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('favicon_filename', ?)", (filename,))
        
        # Handle logo upload if provided
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                filename = f"logo_{int(time.time())}{ext}"
                filepath = app.config['UPLOAD_FOLDER'] / filename
                file.save(str(filepath))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('logo_filename', ?)", (filename,))
        
        # Set admin password (store as plain text for now, matching existing pattern)
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('app_password', ?)", (admin_password,))
        
        # Mark setup as complete
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('is_setup_complete', ?)", ('true',))
        conn.commit()
        conn.close()
        
        flash('Setup completed successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    conn.close()
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        app_password = get_app_password()

        # Check against app password or developer password
        if password == app_password or password == DEVELOPER_PASSWORD:
            session['authenticated'] = True
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('index'))
        else:
            flash('Incorrect password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def index():
    event_id = request.args.get('event_id')
    if not event_id:
        # Redirect to select event
        conn = get_db()
        months = get_event_date_range_months()
        cur = conn.execute(f"""
            SELECT id, name FROM events
            WHERE start_time >= datetime('now', '-{months} month') AND start_time <= datetime('now', '+{months} month')
            ORDER BY ABS(strftime('%s', start_time) - strftime('%s', 'now')) ASC
            LIMIT 1
        """)
        default_event = cur.fetchone()
        conn.close()
        if default_event:
            return redirect(url_for('index', event_id=default_event['id']))
        else:
            flash('No events available. Please add events in admin.', 'warning')
            return redirect(url_for('admin_index'))

    conn = get_db()
    cur = conn.execute("""
        SELECT c.id, k.id as kid_id, c.checkin_time, c.checkout_time, k.name as kid_name, k.notes as kid_notes,
               f.authorized_adults, f.phone, f.troop, a.name as adult_name
        FROM checkins c
        JOIN kids k ON c.kid_id = k.id
        JOIN families f ON k.family_id = f.id
        JOIN adults a ON c.adult_id = a.id
        WHERE c.checkout_time IS NULL AND c.event_id = ?
        ORDER BY c.checkin_time DESC
    """, (event_id,))
    checked_in = cur.fetchall()

    # Convert to dicts and format times
    checked_in = [dict(r) for r in checked_in]
    for checkin in checked_in:
        dt = datetime.fromisoformat(checkin['checkin_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
        checkin['formatted_time'] = dt.strftime('%b %d %I:%M %p')

    months = get_event_date_range_months()
    cur2 = conn.execute(f"SELECT id, name, start_time FROM events WHERE start_time >= datetime('now', '-{months} month') AND start_time <= datetime('now', '+{months} month') ORDER BY start_time DESC")
    events = cur2.fetchall()
    
    # Get require_codes setting
    setting = conn.execute("SELECT value FROM settings WHERE key = 'require_checkout_code'").fetchone()
    require_codes = setting and setting[0] == 'true'
    
    conn.close()

    # Check if TLC is configured (for UI button)
    tlc_configured = 'tlc_email' in session and 'tlc_password' in session

    return render_template('index.html', checked_in=checked_in, events=events, current_event_id=int(event_id), require_codes=require_codes, tlc_configured=tlc_configured)

@app.route('/checkin_last4', methods=['POST'])
@require_auth
def checkin_last4():
    phone_digits = request.form.get('last4', '').strip()
    event_id = request.form.get('event_id')
    if not phone_digits or not phone_digits.isdigit():
        return jsonify({'error': 'Invalid phone number'}), 400
    conn = get_db()
    
    # Search for phone that contains or ends with the provided digits
    # Phone may be stored with formatting (dashes, spaces, parens), so we need to strip and compare
    # Using REPLACE to remove common phone formatting characters
    cur = conn.execute("""
        SELECT f.id, f.phone, f.troop, f.default_adult_id,
               (SELECT GROUP_CONCAT(a.id || ':' || a.name)
                FROM adults a WHERE a.family_id = f.id) as adults,
               (SELECT GROUP_CONCAT(k.id || ':' || k.name || ':' || COALESCE(k.notes, ''))
                FROM kids k WHERE k.family_id = f.id) as kids
        FROM families f
        WHERE REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(f.phone, '-', ''), ' ', ''), '(', ''), ')', ''), '.', '') LIKE ?
           OR REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(f.phone, '-', ''), ' ', ''), '(', ''), ')', ''), '.', '') = ?
    """, ('%' + phone_digits + '%', phone_digits))
    families = cur.fetchall()
    
    if not families:
        conn.close()
        return jsonify({'error': 'No family found with that phone number'}), 404
    
    # Helper function to parse family data
    def parse_family_data(family):
        # Parse concatenated adult and kid data
        adults_list = parse_concat_list(family['adults'], ':') if family['adults'] else []
        adults = []
        for adult_parts in adults_list:
            if len(adult_parts) >= 2:
                adults.append({'id': int(adult_parts[0]), 'name': adult_parts[1]})
        
        kids_list = parse_concat_list(family['kids'], ':') if family['kids'] else []
        kids = []
        for kid_parts in kids_list:
            if len(kid_parts) >= 2:
                kid_id = int(kid_parts[0]) if kid_parts[0].isdigit() else None
                if kid_id:
                    kids.append({
                        'id': kid_id, 
                        'name': kid_parts[1], 
                        'notes': kid_parts[2] if len(kid_parts) > 2 else ''
                    })
        
        # Check which kids are already checked in to this event (if provided)
        if event_id and kids:
            kid_ids = [k['id'] for k in kids]
            placeholders = ','.join('?' * len(kid_ids))
            checked_in_cur = conn.execute(f"""
                SELECT kid_id FROM checkins 
                WHERE kid_id IN ({placeholders}) AND event_id = ? AND checkout_time IS NULL
            """, kid_ids + [event_id])
            checked_in_kids = {row[0] for row in checked_in_cur.fetchall()}
            
            # Mark kids as already checked in
            for kid in kids:
                kid['already_checked_in'] = kid['id'] in checked_in_kids
        
        return {
            'family_id': family['id'],
            'phone': family['phone'],
            'troop': family['troop'],
            'default_adult_id': family['default_adult_id'],
            'adults': adults,
            'kids': kids
        }
    
    # If multiple matches, return all of them (like search_name does)
    if len(families) > 1:
        families_data = [parse_family_data(f) for f in families]
        conn.close()
        return jsonify({'families': families_data})
    
    # Single match - return family data directly
    family_data = parse_family_data(families[0])
    conn.close()
    
    return jsonify(family_data)


@app.route('/search_name', methods=['POST'])
@require_auth
def search_name():
    """Search families by kid or adult name (partial match). Returns similar structure to checkin_last4 for the first match or an array of families."""
    name = request.form.get('name', '').strip()
    event_id = request.form.get('event_id')
    if not name:
        return jsonify({'error': 'Name required'}), 400

    likeparam = f"%{name}%"
    conn = get_db()
    cur = conn.execute("""
        SELECT f.id, f.phone, f.troop, f.default_adult_id,
               (SELECT GROUP_CONCAT(a.id || ':' || a.name)
                FROM adults a WHERE a.family_id = f.id) as adults,
               (SELECT GROUP_CONCAT(k.id || ':' || k.name || ':' || COALESCE(k.notes, ''))
                FROM kids k WHERE k.family_id = f.id) as kids
        FROM families f
        WHERE EXISTS (SELECT 1 FROM kids k WHERE k.family_id = f.id AND k.name LIKE ? COLLATE NOCASE)
           OR EXISTS (SELECT 1 FROM adults a WHERE a.family_id = f.id AND a.name LIKE ? COLLATE NOCASE)
        LIMIT 20
    """, (likeparam, likeparam))
    families = cur.fetchall()

    if not families:
        conn.close()
        return jsonify({'families': []})

    # Get all family IDs first
    family_ids = [family['id'] for family in families]
    
    # Get all checked-in kids for this event in a single query (if provided)
    checked_in_kids = set()
    if event_id and family_ids:
        placeholders = ','.join('?' * len(family_ids))
        checked_in_cur = conn.execute(f"""
            SELECT DISTINCT c.kid_id
            FROM checkins c
            JOIN kids k ON c.kid_id = k.id
            WHERE k.family_id IN ({placeholders})
            AND c.event_id = ? AND c.checkout_time IS NULL
        """, family_ids + [event_id])
        checked_in_kids = {row[0] for row in checked_in_cur.fetchall()}

    # Build a list of family objects similar to checkin_last4
    results = []
    for family in families:
        # Parse concatenated adult and kid data
        adults_list = parse_concat_list(family['adults'], ':') if family['adults'] else []
        adults = []
        for adult_parts in adults_list:
            if len(adult_parts) >= 2:
                adults.append({'id': int(adult_parts[0]), 'name': adult_parts[1]})
        
        kids_list = parse_concat_list(family['kids'], ':') if family['kids'] else []
        kids = []
        for kid_parts in kids_list:
            if len(kid_parts) >= 2:
                kid_id = int(kid_parts[0]) if kid_parts[0].isdigit() else None
                if kid_id:
                    kids.append({
                        'id': kid_id, 
                        'name': kid_parts[1], 
                        'notes': kid_parts[2] if len(kid_parts) > 2 else ''
                    })

        # Mark kids as already checked in
        if event_id:
            for kid in kids:
                kid['already_checked_in'] = kid['id'] in checked_in_kids

        results.append({
            'family_id': family['id'],
            'phone': family['phone'],
            'troop': family['troop'],
            'default_adult_id': family['default_adult_id'],
            'adults': adults,
            'kids': kids
        })

    conn.close()
    # Return array of matches; client will handle single vs multiple
    return jsonify({'families': results})


@app.route('/admin/backup_db')
@require_auth
def admin_backup_db():
    """Create and return a zip containing the database and uploads/data directories (if present)."""
    # Use in-memory zip if small, otherwise temporary file
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    tmpdir = tempfile.mkdtemp(prefix='youth_checkin_backup_')
    zip_path = Path(tmpdir) / f'youth-secure-checkin-backup-{timestamp}.zip'

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add the main SQLite DB
            try:
                if DB_PATH.exists():
                    zf.write(str(DB_PATH), arcname='checkin.db')
            except Exception:
                pass

            # Add data directory contents (if any)
            data_dir = Path(__file__).parent / 'data'
            if data_dir.exists():
                for root, dirs, files in os.walk(data_dir):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, start=Path(__file__).parent)
                        zf.write(full, arcname=arc)

            # Add uploads if present
            uploads_dir = Path(__file__).parent / 'uploads'
            if uploads_dir.exists():
                for root, dirs, files in os.walk(uploads_dir):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, start=Path(__file__).parent)
                        zf.write(full, arcname=arc)

        # Schedule cleanup of tempdir after short delay
        def _cleanup(path):
            time.sleep(60)
            try:
                shutil.rmtree(path)
            except Exception:
                pass
        threading.Thread(target=_cleanup, args=(tmpdir,), daemon=True).start()

        return send_file(str(zip_path), as_attachment=True, download_name=f'youth-secure-checkin-backup-{timestamp}.zip')
    except Exception as e:
        # cleanup on error
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
        return jsonify({'error': 'Backup failed', 'details': str(e)}), 500

@app.route('/admin/restore_db', methods=['POST'])
@require_auth
def admin_restore_db():
    """Restore database from uploaded backup zip file."""
    if 'backup_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('admin_utilities'))
    
    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin_utilities'))
    
    if not backup_file.filename.endswith('.zip'):
        flash('File must be a .zip backup file', 'error')
        return redirect(url_for('admin_utilities'))
    
    tmpdir = tempfile.mkdtemp(prefix='youth_checkin_restore_')
    try:
        # Save uploaded file
        zip_path = Path(tmpdir) / 'backup.zip'
        backup_file.save(str(zip_path))
        
        # Extract and validate
        extract_dir = Path(tmpdir) / 'extracted'
        extract_dir.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(str(extract_dir))
        
        # Check for checkin.db in extracted files
        db_file = extract_dir / 'checkin.db'
        if not db_file.exists():
            flash('Invalid backup file: checkin.db not found', 'error')
            shutil.rmtree(tmpdir)
            return redirect(url_for('admin_utilities'))
        
        # Backup current database before replacing
        app_root = Path(__file__).parent
        current_backup_name = f'checkin-before-restore-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.db'
        if DB_PATH.exists():
            shutil.copy2(str(DB_PATH), str(app_root / current_backup_name))
        
        # Replace database
        shutil.copy2(str(db_file), str(DB_PATH))
        
        # Restore data directory if present in backup
        data_backup = extract_dir / 'data'
        if data_backup.exists():
            data_dir = app_root / 'data'
            # Clear existing data dir contents (except the DB we just restored)
            if data_dir.exists():
                for item in data_dir.iterdir():
                    if item.name != 'checkin.db':
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
            else:
                data_dir.mkdir(exist_ok=True)
            
            # Copy restored data
            for item in data_backup.iterdir():
                if item.name != 'checkin.db':  # Skip DB, already restored
                    dest = data_dir / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
        
        # Restore uploads directory if present in backup
        uploads_backup = extract_dir / 'uploads'
        if uploads_backup.exists():
            uploads_dir = app_root / 'uploads'
            if uploads_dir.exists():
                shutil.rmtree(uploads_dir)
            shutil.copytree(uploads_backup, uploads_dir)
        
        # Cleanup temp directory
        shutil.rmtree(tmpdir)
        
        flash(f'Database restored successfully! Previous database saved as {current_backup_name}', 'success')
        return redirect(url_for('admin_utilities'))
        
    except Exception as e:
        # Cleanup on error
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
        flash(f'Restore failed: {str(e)}', 'error')
        return redirect(url_for('admin_utilities'))

@app.route('/checkin_selected', methods=['POST'])
@require_auth
def checkin_selected():
    family_id = request.form.get('family_id')
    adult_id = request.form.get('adult_id')
    kid_ids = request.form.getlist('kid_ids')
    event_id = request.form.get('event_id')
    if not family_id or not adult_id or not kid_ids or not event_id:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
    conn = get_db()
    now = datetime.utcnow().isoformat()
    
    # Check if checkout codes are enabled and get method
    require_codes_setting = conn.execute("SELECT value FROM settings WHERE key = 'require_checkout_code'").fetchone()
    require_codes = require_codes_setting and require_codes_setting[0] == 'true'
    
    checkout_method_setting = conn.execute("SELECT value FROM settings WHERE key = 'checkout_code_method'").fetchone()
    checkout_method = checkout_method_setting[0] if checkout_method_setting else 'qr'  # Default to QR
    
    # Get label printer settings if printing is needed
    label_size = '30336'  # Default
    if require_codes and checkout_method in ['label', 'both'] and LABEL_PRINTING_AVAILABLE:
        printer_type = conn.execute("SELECT value FROM settings WHERE key = 'label_printer_type'").fetchone()
        label_size_setting = conn.execute("SELECT value FROM settings WHERE key = 'label_size'").fetchone()
        printer_type = printer_type[0] if printer_type else 'dymo'
        label_size = label_size_setting[0] if label_size_setting else '30336'
        
        # Get event info for label
        event_row = conn.execute("SELECT name, start_time FROM events WHERE id = ?", (event_id,)).fetchone()
        event_name = event_row[0] if event_row else "Event"
        event_date = event_row[1][:10] if event_row else datetime.now().strftime('%Y-%m-%d')
    
    checked_in_count = 0
    labels_to_print = []  # Collect label data for client-side printing
    checked_in_data = []  # Collect check-in data for UI update
    kid_names_for_label = []  # Collect names for combined label
    
    # Get family info for the response
    family_row = conn.execute("""
        SELECT f.phone, f.troop, f.authorized_adults,
               a.name as adult_name
        FROM families f
        JOIN adults a ON a.id = ?
        WHERE f.id = ?
    """, (adult_id, family_id)).fetchone()
    
    adult_name = family_row['adult_name'] if family_row else 'Unknown'
    phone = family_row['phone'] if family_row else ''
    authorized_adults = family_row['authorized_adults'] if family_row else ''
    
    # Check if this family already has a checkout code for this event from previous check-ins
    family_checkout_code = None
    if require_codes:
        # Look for existing checkout code for this family/event combination
        existing_code = conn.execute("""
            SELECT DISTINCT c.checkout_code 
            FROM checkins c
            JOIN kids k ON k.id = c.kid_id
            WHERE k.family_id = ? AND c.event_id = ? AND c.checkout_time IS NULL AND c.checkout_code IS NOT NULL
            LIMIT 1
        """, (family_id, event_id)).fetchone()
        
        if existing_code and existing_code[0]:
            # Reuse existing code for siblings checked in separately
            family_checkout_code = existing_code[0]
        else:
            # Generate new code if none exists
            try:
                family_checkout_code = generate_unique_code(int(event_id), str(DB_PATH))
            except Exception as e:
                print(f"Error generating checkout code: {e}")
                family_checkout_code = None
    
    for kid_id in kid_ids:
        # Check if already checked in to this event
        cur = conn.execute("SELECT id FROM checkins WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL", (kid_id, event_id))
        if cur.fetchone():
            continue
        
        # Insert check-in with the SAME family code for all kids
        cursor = conn.execute("INSERT INTO checkins (kid_id, adult_id, event_id, checkin_time, checkout_code) VALUES (?, ?, ?, ?, ?)", 
                    (kid_id, adult_id, event_id, now, family_checkout_code))
        checkin_id = cursor.lastrowid
        checked_in_count += 1
        
        # Get kid data for response
        kid_row = conn.execute("SELECT name, notes FROM kids WHERE id = ?", (kid_id,)).fetchone()
        kid_name = kid_row['name'] if kid_row else "Unknown"
        kid_notes = kid_row['notes'] if kid_row else ''
        
        # Convert UTC to CST for display
        utc_time = datetime.fromisoformat(now).replace(tzinfo=pytz.UTC)
        cst_time = utc_time.astimezone(pytz.timezone('America/Chicago'))
        checkin_time = cst_time.strftime('%I:%M %p')
        formatted_time = cst_time.strftime('%b %d %I:%M %p')
        
        # Add to checked-in data for UI update
        checked_in_data.append({
            'id': checkin_id,
            'kid_id': int(kid_id),
            'kid_name': kid_name,
            'kid_notes': kid_notes,
            'adult_name': adult_name,
            'phone': phone,
            'authorized_adults': authorized_adults,
            'formatted_time': formatted_time
        })
        
        # Collect kid names for combined label
        kid_names_for_label.append(kid_name)
    
    # Create a single combined label if multiple kids checked in together
    if family_checkout_code and checkout_method in ['label', 'both'] and len(kid_names_for_label) > 0:
        try:
            # Combine all kid names for the label (comma separated)
            combined_names = ', '.join(kid_names_for_label)
            
            # Convert UTC to CST for display
            utc_time = datetime.fromisoformat(now).replace(tzinfo=pytz.UTC)
            cst_time = utc_time.astimezone(pytz.timezone('America/Chicago'))
            checkin_time = cst_time.strftime('%I:%M %p')
            
            # Add single label with all names
            labels_to_print.append({
                'kid_name': combined_names,
                'event_name': event_name,
                'event_date': event_date,
                'checkin_time': checkin_time,
                'checkout_code': family_checkout_code
            })
        except Exception as e:
            print(f"Error preparing label data: {e}")
    
    conn.commit()
    
    # Generate share token and QR code ONLY if codes are required and method includes QR
    share_token = None
    qr_code_data = None
    short_url = None
    if require_codes and checkout_method in ['qr', 'both'] and checked_in_data and len(checked_in_data) > 0 and any(c['id'] for c in checked_in_data):
        share_token = generate_share_token()
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        checkin_ids = ','.join([str(c['id']) for c in checked_in_data])
        
        conn.execute("""
            INSERT INTO share_tokens (token, family_id, event_id, checkin_ids, created_at, expires_at, used)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (share_token, family_id, event_id, checkin_ids, now, expires_at))
        conn.commit()
        
        # Generate QR code URL
        share_url = url_for('share_codes', token=share_token, _external=True)
        qr_code_data = create_qr_code(share_url)
    
    conn.close()
    
    # Return response with label data for client-side printing and check-in data for UI
    return jsonify({
        'success': True, 
        'message': f'Checked in {checked_in_count} kid(s)',
        'labels': labels_to_print,
        'label_size': label_size,
        'checkins': checked_in_data,
        'share_token': share_token,
        'qr_code': qr_code_data,
        'short_url': short_url,
        'checkout_code': family_checkout_code
    })

@app.route('/checkout/<int:kid_id>', methods=['POST'])
@require_auth
def checkout(kid_id):
    event_id = request.form.get('event_id')
    checkout_code = request.form.get('checkout_code', '').strip()
    additional_kid_ids = request.form.getlist('additional_kid_ids')  # Get additional kids to checkout
    
    if not event_id:
        return jsonify({'success': False, 'message': 'Missing event_id'}), 400
    
    # Combine primary kid with additional kids
    all_kid_ids = [kid_id] + [int(kid) for kid in additional_kid_ids if kid]
    
    conn = get_db()
    
    # Check if codes are required
    setting = conn.execute("SELECT value FROM settings WHERE key = 'require_checkout_code'").fetchone()
    require_codes = setting and setting[0] == 'true'
    
    # If codes are required, verify the code or admin override password
    if require_codes:
        if not checkout_code:
            conn.close()
            return jsonify({'success': False, 'message': 'Checkout code required', 'code_required': True}), 400
        
        # Check if it's the admin override password
        override_password = get_override_password()
        is_admin_password = (checkout_code == override_password or checkout_code == DEVELOPER_PASSWORD)
        
        if not is_admin_password:
            # Verify the checkout code matches for the primary kid
            checkin = conn.execute("""
                SELECT checkout_code FROM checkins 
                WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL
            """, (kid_id, event_id)).fetchone()
            
            if not checkin:
                conn.close()
                return jsonify({'success': False, 'message': 'Check-in not found'}), 404
            
            if checkin[0] != checkout_code:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid checkout code', 'code_required': True}), 403
    
    # Perform checkout for all selected kids
    now = datetime.utcnow().isoformat()
    checked_out_count = 0
    checkin_ids = []
    
    for current_kid_id in all_kid_ids:
        # Get the checkin_id
        checkin_row = conn.execute("""
            SELECT id FROM checkins 
            WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL
        """, (current_kid_id, event_id)).fetchone()
        
        if checkin_row:
            checkin_ids.append(checkin_row['id'])
            conn.execute("UPDATE checkins SET checkout_time = ? WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL", 
                        (now, current_kid_id, event_id))
            checked_out_count += 1
    
    # Mark share token as used if all kids are checked out
    if checkin_ids:
        # Find tokens containing any of these checkins
        tokens = conn.execute("""
            SELECT id, checkin_ids FROM share_tokens 
            WHERE used = 0
        """).fetchall()
        
        for token in tokens:
            token_checkin_ids = token['checkin_ids'].split(',')
            # Check if any of our checked out kids are in this token
            has_overlap = any(str(cid) in token_checkin_ids for cid in checkin_ids)
            if has_overlap:
                # Check if all checkins in this token are now checked out
                all_checked_out = True
                for cid in token_checkin_ids:
                    check = conn.execute("""
                        SELECT checkout_time FROM checkins WHERE id = ?
                    """, (cid,)).fetchone()
                    if check and not check['checkout_time']:
                        all_checked_out = False
                        break
                
                # Mark token as used if all kids are checked out
                if all_checked_out:
                    conn.execute("UPDATE share_tokens SET used = 1 WHERE id = ?", (token['id'],))
    
    conn.commit()
    conn.close()
    
    # Return JSON if it's an AJAX request, otherwise redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': f'Checked out {checked_out_count} kid(s) successfully'})
    return redirect(request.referrer or url_for('kiosk'))

@app.route('/get_siblings/<int:kid_id>', methods=['POST'])
@require_auth
def get_siblings(kid_id):
    """Get checked-in siblings for a kid to allow group checkout"""
    event_id = request.form.get('event_id')
    
    if not event_id:
        return jsonify({'success': False, 'message': 'Missing event_id'}), 400
    
    conn = get_db()
    
    # Get the family_id for this kid
    kid_row = conn.execute("SELECT family_id, name FROM kids WHERE id = ?", (kid_id,)).fetchone()
    
    if not kid_row:
        conn.close()
        return jsonify({'success': False, 'message': 'Kid not found'}), 404
    
    family_id = kid_row['family_id']
    kid_name = kid_row['name']
    
    # Get all siblings checked in to this event (excluding the current kid)
    siblings = conn.execute("""
        SELECT k.id, k.name
        FROM kids k
        JOIN checkins c ON c.kid_id = k.id
        WHERE k.family_id = ? AND k.id != ? AND c.event_id = ? AND c.checkout_time IS NULL
        ORDER BY k.name
    """, (family_id, kid_id, event_id)).fetchall()
    
    conn.close()
    
    sibling_list = [{'kid_id': s['id'], 'name': s['name']} for s in siblings]
    
    return jsonify({
        'success': True,
        'kid_name': kid_name,
        'siblings': sibling_list
    })

@app.route('/share/<token>')
def share_codes(token):
    """Display checkout codes for a family's check-ins with Web Share API support"""
    cleanup_expired_tokens()  # Clean up old tokens first
    
    conn = get_db()
    
    # Get token data
    token_data = conn.execute("""
        SELECT st.*, e.name as event_name, e.start_time
        FROM share_tokens st
        JOIN events e ON e.id = st.event_id
        WHERE st.token = ? AND st.used = 0 AND st.expires_at > ?
    """, (token, datetime.utcnow().isoformat())).fetchone()
    
    if not token_data:
        conn.close()
        return render_template('share_expired.html'), 404
    
    # Get checkin details - all kids share the same code
    checkin_ids = token_data['checkin_ids'].split(',')
    kids = []
    family_code = None
    checkin_time = None
    all_checked_out = True
    
    for checkin_id in checkin_ids:
        checkin = conn.execute("""
            SELECT c.checkout_code, c.checkin_time, c.checkout_time,
                   k.name as kid_name
            FROM checkins c
            JOIN kids k ON k.id = c.kid_id
            WHERE c.id = ?
        """, (checkin_id,)).fetchone()
        
        if checkin:
            # Get the family code from the first checkin (they're all the same)
            if not family_code:
                family_code = checkin['checkout_code']
                # Convert UTC to local time
                utc_time = datetime.fromisoformat(checkin['checkin_time']).replace(tzinfo=pytz.UTC)
                checkin_time = utc_time.astimezone(local_tz).strftime('%I:%M %p')
            
            kids.append({
                'name': checkin['kid_name'],
                'checked_out': checkin['checkout_time'] is not None
            })
            
            if not checkin['checkout_time']:
                all_checked_out = False
    
    conn.close()
    
    if not kids or not family_code:
        return render_template('share_expired.html'), 404
    
    # Format event time
    event_time = datetime.fromisoformat(token_data['start_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
    
    logo_filename = get_logo_filename()
    
    return render_template('share_codes.html',
                         event_name=token_data['event_name'],
                         event_date=event_time.strftime('%B %d, %Y'),
                         checkout_code=family_code,
                         checkin_time=checkin_time,
                         kids=kids,
                         all_checked_out=all_checked_out,
                         logo_filename=logo_filename)

@app.route('/kiosk')
@require_auth
def kiosk():
    event_id = request.args.get('event_id')
    if not event_id:
        # Redirect to select event
        conn = get_db()
        months = get_event_date_range_months()
        cur = conn.execute(f"""
            SELECT id, name FROM events
            WHERE start_time >= datetime('now', '-{months} month') AND start_time <= datetime('now', '+{months} month')
            ORDER BY ABS(strftime('%s', start_time) - strftime('%s', 'now')) ASC
            LIMIT 1
        """)
        default_event = cur.fetchone()
        conn.close()
        if default_event:
            return redirect(url_for('kiosk', event_id=default_event['id']))
        else:
            return "No events available", 404

    conn = get_db()
    cur = conn.execute("""
        SELECT c.id, k.id as kid_id, c.checkin_time, c.checkout_time, k.name as kid_name, k.notes as kid_notes,
               f.authorized_adults, f.phone, f.troop, a.name as adult_name
        FROM checkins c
        JOIN kids k ON c.kid_id = k.id
        JOIN families f ON k.family_id = f.id
        JOIN adults a ON c.adult_id = a.id
        WHERE c.checkout_time IS NULL AND c.event_id = ?
        ORDER BY c.checkin_time DESC
    """, (event_id,))
    checked_in = cur.fetchall()

    months = get_event_date_range_months()
    cur2 = conn.execute(f"SELECT id, name, start_time FROM events WHERE start_time >= datetime('now', '-{months} month') AND start_time <= datetime('now', '+{months} month') ORDER BY start_time DESC")
    events = cur2.fetchall()
    current_event = next((e for e in events if e['id'] == int(event_id)), None)
    if current_event:
        dt = datetime.fromisoformat(current_event['start_time']).astimezone(local_tz)
        current_event_name = current_event['name']
        current_event_date = dt.strftime('%b %d, %Y')
    else:
        current_event_name = 'Event'
        current_event_date = ''

    # Convert to dicts for mutability
    checked_in = [dict(c) for c in checked_in]
    events = [dict(e) for e in events]

    # Format times for display
    for c in checked_in:
        dt = datetime.fromisoformat(c['checkin_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
        c['formatted_time'] = dt.strftime('%b %d %I:%M %p')
    for e in events:
        dt = datetime.fromisoformat(e['start_time']).astimezone(local_tz)
        e['formatted_start'] = dt.strftime('%b %d, %Y %I:%M %p')

    logo_filename = get_logo_filename()
    
    conn.close()

    return render_template('kiosk.html', checked_in=checked_in, events=events, current_event_id=int(event_id), current_event_name=current_event_name, current_event_date=current_event_date, logo_filename=logo_filename)

@app.route('/history')
@require_auth
def history():
    event_id = request.args.get('event_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db()

    # Get all events for the filter dropdown
    events_cur = conn.execute("SELECT id, name, start_time FROM events ORDER BY start_time DESC")
    events = events_cur.fetchall()

    # Build the query with filters
    query = """
        SELECT c.id, c.checkin_time, c.checkout_time, k.name as kid_name, f.phone, f.troop, e.name as event_name, a.name as adult_name
        FROM checkins c
        JOIN kids k ON c.kid_id = k.id
        JOIN families f ON k.family_id = f.id
        JOIN adults a ON c.adult_id = a.id
        JOIN events e ON c.event_id = e.id
        WHERE 1=1
    """
    params = []

    if event_id:
        query += " AND c.event_id = ?"
        params.append(event_id)

    if start_date:
        query += " AND date(c.checkin_time) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date(c.checkin_time) <= ?"
        params.append(end_date)

    query += " ORDER BY c.checkin_time DESC LIMIT 200"

    cur = conn.execute(query, params)
    rows = cur.fetchall()

    # Convert to dicts and format times
    rows = [dict(r) for r in rows]
    for r in rows:
        dt = datetime.fromisoformat(r['checkin_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
        r['formatted_checkin'] = dt.strftime('%b %d, %Y %I:%M %p')
        if r['checkout_time']:
            dt = datetime.fromisoformat(r['checkout_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
            r['formatted_checkout'] = dt.strftime('%b %d, %Y %I:%M %p')
        else:
            r['formatted_checkout'] = ''
    conn.close()

    return render_template('history.html', rows=rows, events=events, event_id=event_id, start_date=start_date, end_date=end_date)

@app.route('/admin/history/email', methods=['POST'])
@require_auth
def email_history():
    """Generate and email the check-in/check-out history report"""
    email_address = request.form.get('email_address', '').strip()
    email_subject = request.form.get('email_subject', 'Check-in Report').strip()
    event_id = request.form.get('event_id', '').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    
    if not email_address:
        flash('Email address is required', 'danger')
        return redirect(url_for('history', event_id=event_id, start_date=start_date, end_date=end_date))
    
    try:
        conn = get_db()
        
        # Build the query with filters (same as history page)
        query = """
            SELECT c.id, c.checkin_time, c.checkout_time, k.name as kid_name, f.phone, f.troop, e.name as event_name, a.name as adult_name
            FROM checkins c
            JOIN kids k ON c.kid_id = k.id
            JOIN families f ON k.family_id = f.id
            JOIN adults a ON c.adult_id = a.id
            JOIN events e ON c.event_id = e.id
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND c.event_id = ?"
            params.append(event_id)
        
        if start_date:
            query += " AND date(c.checkin_time) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date(c.checkin_time) <= ?"
            params.append(end_date)
        
        query += " ORDER BY c.checkin_time DESC"
        
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        rows = [dict(r) for r in rows]
        
        # Format times and build HTML table
        html_rows = []
        for r in rows:
            dt = datetime.fromisoformat(r['checkin_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
            checkin_time = dt.strftime('%b %d, %Y %I:%M %p')
            
            checkout_time = ''
            if r['checkout_time']:
                dt = datetime.fromisoformat(r['checkout_time']).replace(tzinfo=pytz.UTC).astimezone(local_tz)
                checkout_time = dt.strftime('%b %d, %Y %I:%M %p')
            
            html_rows.append({
                'kid_name': r['kid_name'],
                'adult_name': r['adult_name'],
                'phone': r['phone'],
                'event_name': r['event_name'],
                'checkin_time': checkin_time,
                'checkout_time': checkout_time or '-'
            })
        
        conn.close()
        
        # Build HTML table
        html_table = """
        <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; font-size: 12px;">
            <thead>
                <tr style="background-color: #f0f0f0; border-bottom: 2px solid #333;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Youth Name</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Adult</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Phone</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Event</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Check-in Time</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #999;">Check-out Time</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for row in html_rows:
            html_table += f"""
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['kid_name']}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['adult_name']}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['phone']}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['event_name']}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['checkin_time']}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">{row['checkout_time']}</td>
                </tr>
            """
        
        html_table += """
            </tbody>
        </table>
        """
        
        # Build HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 900px; margin: 0 auto;">
                    <h2 style="color: #0dcaf0; border-bottom: 2px solid #0dcaf0; padding-bottom: 10px;">Check-in Report</h2>
                    
                    <div style="background-color: #f9f9f9; padding: 10px; margin: 15px 0; border-left: 4px solid #0dcaf0;">
                        <p><strong>Report Generated:</strong> {datetime.now().strftime('%b %d, %Y %I:%M %p')}</p>
                        <p><strong>Total Records:</strong> {len(html_rows)}</p>
                    </div>
                    
                    {html_table}
                    
                    <div style="margin-top: 20px; font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 10px;">
                        <p>This is an automated report. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Send email
        success, message = send_email(email_address, email_subject, html_body)
        
        if success:
            flash(f'Report sent successfully to {email_address}', 'success')
        else:
            flash(f'Failed to send report: {message}', 'danger')
        
        return redirect(url_for('history', event_id=event_id, start_date=start_date, end_date=end_date))
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('history', event_id=event_id, start_date=start_date, end_date=end_date))

# Admin routes
@app.route('/admin')
@require_auth
def admin_index():
    return render_template('admin/index.html')

@app.route('/admin/backup/export')
@require_auth
def export_configuration():
    """Export all configuration settings as JSON backup"""
    conn = get_db()
    
    # Collect all settings
    settings = {}
    
    # Branding settings
    branding_keys = ['organization_name', 'organization_type', 'group_term', 'group_term_lower',
                     'primary_color', 'secondary_color', 'accent_color', 
                     'logo_filename', 'favicon_filename']
    for key in branding_keys:
        val = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if val:
            settings[key] = val['value']
    
    # Security/access settings (exclude developer_password as it's env-only)
    security_keys = ['app_password', 'admin_override_password', 'checkout_code']
    for key in security_keys:
        val = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if val:
            settings[key] = val['value']
    
    # Other settings
    other_keys = ['event_date_range_months', 'label_line_1', 'label_line_2', 'label_line_3']
    for key in other_keys:
        val = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if val:
            settings[key] = val['value']
    
    conn.close()
    
    # Add metadata
    backup = {
        'export_date': datetime.now().isoformat(),
        'app_version': '1.0',
        'settings': settings
    }
    
    # Generate JSON
    output = json.dumps(backup, indent=2)
    
    response = app.response_class(
        response=output,
        status=200,
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = f'attachment; filename=configuration_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    return response

@app.route('/admin/backup/import', methods=['POST'])
@require_auth
def import_configuration():
    """Import/restore configuration settings from JSON backup"""
    if 'backup_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('admin_index'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin_index'))
    
    if not file.filename.endswith('.json'):
        flash('Invalid file type. Please upload a JSON backup file.', 'danger')
        return redirect(url_for('admin_index'))
    
    try:
        # Read and parse JSON
        content = file.read().decode('utf-8')
        backup = json.loads(content)
        
        # Validate backup structure
        if 'settings' not in backup:
            flash('Invalid backup file format', 'danger')
            return redirect(url_for('admin_index'))
        
        settings = backup['settings']
        conn = get_db()
        imported_count = 0
        
        # Import all settings
        for key, value in settings.items():
            # Skip empty values
            if value is None or value == '':
                continue
            
            # Insert or update setting
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            imported_count += 1
        
        conn.commit()
        conn.close()
        
        flash(f'Configuration restored successfully! {imported_count} settings imported.', 'success')
        flash('Please review your settings and restart the application if needed.', 'info')
        
    except json.JSONDecodeError:
        flash('Invalid JSON file. Please upload a valid backup file.', 'danger')
    except Exception as e:
        flash(f'Error importing configuration: {str(e)}', 'danger')
    
    return redirect(url_for('admin_index'))

@app.route('/admin/unlock_override', methods=['POST'])
@require_auth
def unlock_override():
    """Unlock the override password section with developer password"""
    dev_password = request.form.get('dev_password', '').strip()
    
    if DEVELOPER_PASSWORD is None:
        flash('Developer password not configured in .env file!', 'danger')
    elif dev_password == DEVELOPER_PASSWORD:
        session['override_unlocked'] = True
        flash('Override settings unlocked!', 'success')
    else:
        flash('Invalid developer password!', 'danger')
    
    return redirect(url_for('admin_security'))

@app.route('/admin/lock_override', methods=['POST'])
@require_auth
def lock_override():
    """Lock the override password section"""
    session.pop('override_unlocked', None)
    flash('Override settings locked!', 'info')
    return redirect(url_for('admin_security'))

@app.route('/admin/unlock_smtp', methods=['POST'])
@require_auth
def unlock_smtp():
    """Unlock the SMTP settings section with developer password"""
    dev_password = request.form.get('dev_password', '').strip()
    
    if DEVELOPER_PASSWORD is None:
        flash('Developer password not configured in .env file!', 'danger')
    elif dev_password == DEVELOPER_PASSWORD:
        session['smtp_unlocked'] = True
        flash('SMTP settings unlocked!', 'success')
    else:
        flash('Invalid developer password!', 'danger')
    
    return redirect(url_for('email_settings'))

@app.route('/admin/lock_smtp', methods=['POST'])
@require_auth
def lock_smtp():
    """Lock the SMTP settings section"""
    session.pop('smtp_unlocked', None)
    flash('SMTP settings locked!', 'info')
    return redirect(url_for('email_settings'))

@app.route('/admin/email', methods=['GET', 'POST'])
@require_auth
def email_settings():
    """Email settings page - separate page for SMTP configuration"""
    conn = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        # Handle SMTP settings save
        if action == 'save_smtp':
            # Only allow saving if SMTP is unlocked
            if session.get('smtp_unlocked', False):
                smtp_settings = {
                    'smtp_server': request.form.get('smtp_server', '').strip(),
                    'smtp_port': request.form.get('smtp_port', '').strip(),
                    'smtp_from': request.form.get('smtp_from', '').strip(),
                    'smtp_username': request.form.get('smtp_username', '').strip(),
                    'smtp_use_tls': 'true' if request.form.get('smtp_use_tls') == 'on' else 'false'
                }
                
                # Only update password if provided (non-empty)
                new_password = request.form.get('smtp_password', '').strip()
                if new_password:
                    smtp_settings['smtp_password'] = new_password
                
                set_smtp_settings(smtp_settings)
                flash('SMTP settings saved successfully!', 'success')
            else:
                flash('SMTP settings are locked. Unlock them first with developer password.', 'warning')
        
        conn.close()
        return redirect(url_for('email_settings'))
    
    # GET request - fetch current settings
    smtp_unlocked = session.get('smtp_unlocked', False)
    smtp_settings = get_smtp_settings()
    
    conn.close()
    return render_template('admin/email_settings.html',
                         smtp_unlocked=smtp_unlocked,
                         smtp_settings=smtp_settings,
                         dev_password_set=bool(DEVELOPER_PASSWORD))

@app.route('/admin/email/test', methods=['POST'])
@require_auth
def test_email():
    """Send a test email to verify SMTP configuration"""
    test_email_address = request.form.get('test_email', '').strip()
    
    if not test_email_address:
        flash('Email address is required', 'danger')
        return redirect(url_for('email_settings'))
    
    try:
        subject = "SMTP Test Email - Check-in System"
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0dcaf0;">✓ SMTP Configuration Working!</h2>
                    
                    <p>This is a test email to verify your SMTP settings are configured correctly.</p>
                    
                    <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #0dcaf0; margin: 20px 0;">
                        <p><strong>System:</strong> Youth Check-In System</p>
                        <p><strong>Test Sent:</strong> {}</p>
                        <p><strong>Status:</strong> ✓ Success</p>
                    </div>
                    
                    <p>You can now use the <strong>Email Report</strong> feature on the History page to send check-in reports via email.</p>
                    
                    <div style="margin-top: 20px; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 10px;">
                        <p>This is an automated test email. Please do not reply.</p>
                    </div>
                </div>
            </body>
        </html>
        """.format(datetime.now().strftime('%b %d, %Y %I:%M %p'))
        
        success, message = send_email(test_email_address, subject, html_body)
        
        if success:
            flash(f'✓ Test email sent successfully to {test_email_address}', 'success')
        else:
            flash(f'✗ Failed to send test email: {message}', 'danger')
    
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'danger')
    
    return redirect(url_for('email_settings'))

@app.route('/admin/backups')
@require_auth
def backup_list():
    """Display list of backups"""
    try:
        backups = backup_manager.list_backups()
        summary = backup_manager.get_backup_summary()
        
        # Get backup schedule settings
        conn = get_db()
        backup_frequency = conn.execute("SELECT value FROM settings WHERE key = 'backup_frequency'").fetchone()
        backup_frequency = backup_frequency[0] if backup_frequency else 'daily'
        
        backup_hour = conn.execute("SELECT value FROM settings WHERE key = 'backup_hour'").fetchone()
        backup_hour = int(backup_hour[0]) if backup_hour else 2
        
        # Get email backup settings
        backup_email_enabled = conn.execute("SELECT value FROM settings WHERE key = 'backup_email_enabled'").fetchone()
        backup_email_enabled = backup_email_enabled[0] if backup_email_enabled else 'false'
        
        backup_email_recipients = conn.execute("SELECT value FROM settings WHERE key = 'backup_email_recipients'").fetchone()
        backup_email_recipients = backup_email_recipients[0] if backup_email_recipients else ''
        
        conn.close()
        
        return render_template('admin/backups.html',
                             backups=backups,
                             summary=summary,
                             backup_frequency=backup_frequency,
                             backup_hour=backup_hour,
                             backup_email_enabled=backup_email_enabled,
                             backup_email_recipients=backup_email_recipients)
    except Exception as e:
        flash(f'Error loading backups: {str(e)}', 'danger')
        return redirect(url_for('admin_index'))

@app.route('/admin/backups/create', methods=['POST'])
@require_auth
def backup_create():
    """Create a new backup"""
    try:
        description = request.form.get('description', '').strip()
        if not description:
            description = f'Manual backup at {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        backup_filename = backup_manager.create_backup(description)
        
        # Rotate old backups according to retention policy
        removed = backup_manager.rotate_backups()
        
        flash(f'✓ Backup created successfully: {backup_filename}', 'success')
        if removed:
            flash(f'Rotated {removed} old backup(s) according to retention policy', 'info')
    
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

@app.route('/admin/backups/download/<filename>')
@require_auth
def backup_download(filename):
    """Download a backup file"""
    try:
        backup_path = Path(backup_manager.backup_dir) / filename
        if not backup_path.exists():
            flash('Backup file not found', 'danger')
            return redirect(url_for('backup_list'))
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f'Error downloading backup: {str(e)}', 'danger')
        return redirect(url_for('backup_list'))

@app.route('/admin/backups/restore/<filename>', methods=['POST'])
@require_auth
def backup_restore(filename):
    """Restore from a backup"""
    try:
        # Confirmation required
        confirm = request.form.get('confirm', '').lower()
        if confirm != 'restore':
            flash('Restoration cancelled: confirmation not provided', 'warning')
            return redirect(url_for('backup_list'))
        
        backup_manager.restore_backup(filename)
        flash(f'✓ Database restored successfully from {filename}', 'success')
        flash('NOTE: You may need to restart the application for all changes to take effect', 'info')
    
    except Exception as e:
        flash(f'Error restoring backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

@app.route('/admin/backups/delete/<filename>', methods=['POST'])
@require_auth
def backup_delete(filename):
    """Delete a backup"""
    try:
        backup_manager.delete_backup(filename)
        flash(f'✓ Backup deleted: {filename}', 'success')
    
    except Exception as e:
        flash(f'Error deleting backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

@app.route('/admin/backups/rotate', methods=['POST'])
@require_auth
def backup_rotate():
    """Manually trigger backup rotation"""
    try:
        removed = backup_manager.rotate_backups()
        if removed > 0:
            flash(f'✓ Rotated {removed} old backup(s)', 'success')
        else:
            flash('No backups needed to be rotated', 'info')
    
    except Exception as e:
        flash(f'Error rotating backups: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

@app.route('/admin/backups/schedule', methods=['POST'])
@require_auth
def backup_schedule():
    """Update backup schedule settings"""
    try:
        frequency = request.form.get('backup_frequency', 'daily').strip()
        hour = int(request.form.get('backup_hour', '2').strip())
        
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('backup_frequency', ?)", (frequency,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('backup_hour', ?)", (str(hour),))
        conn.commit()
        conn.close()
        
        # Update scheduler if available
        if scheduler:
            # Remove existing backup job if present
            if scheduler.get_job('local_backup_job'):
                scheduler.remove_job('local_backup_job')
            
            # Add new scheduled job
            try:
                if frequency == 'hourly':
                    scheduler.add_job(perform_scheduled_local_backup, 'cron', minute=0, id='local_backup_job', replace_existing=True)
                elif frequency == 'daily':
                    scheduler.add_job(perform_scheduled_local_backup, 'cron', hour=hour, minute=0, id='local_backup_job', replace_existing=True)
                elif frequency == 'weekly':
                    scheduler.add_job(perform_scheduled_local_backup, 'cron', day_of_week='6', hour=hour, minute=0, id='local_backup_job', replace_existing=True)
                elif frequency == 'monthly':
                    scheduler.add_job(perform_scheduled_local_backup, 'cron', day=1, hour=hour, minute=0, id='local_backup_job', replace_existing=True)
                
                app.logger.info(f"Scheduled backup job updated: {frequency} at {hour:02d}:00")
                flash(f'✓ Backup schedule updated: {frequency} at {hour:02d}:00', 'success')
            except Exception as e:
                app.logger.warning(f"Failed to update scheduled backup: {e}")
                flash(f'Settings saved but scheduler update failed: {str(e)}', 'warning')
        else:
            flash('✓ Backup schedule saved (scheduler not available)', 'warning')
    
    except Exception as e:
        flash(f'Error updating backup schedule: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

@app.route('/admin/backups/email-config', methods=['POST'])
@require_auth
def backup_email_config():
    """Update email backup configuration"""
    try:
        email_enabled = 'true' if request.form.get('backup_email_enabled') == 'on' else 'false'
        email_recipients = request.form.get('backup_email_recipients', '').strip()
        
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('backup_email_enabled', ?)", (email_enabled,))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('backup_email_recipients', ?)", (email_recipients,))
        conn.commit()
        conn.close()
        
        flash('✓ Email backup settings updated successfully!', 'success')
    
    except Exception as e:
        flash(f'Error updating email backup settings: {str(e)}', 'danger')
    
    return redirect(url_for('backup_list'))

def perform_scheduled_local_backup():
    """Perform a scheduled local backup (called by APScheduler)"""
    try:
        description = f'Scheduled backup at {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        backup_filename = backup_manager.create_backup(description)
        
        # Rotate old backups
        removed = backup_manager.rotate_backups()
        
        app.logger.info(f"Scheduled backup completed: {backup_filename} (rotated {removed} old backups)")
    except Exception as e:
        app.logger.error(f"Error performing scheduled backup: {str(e)}")

@app.route('/admin/security', methods=['GET', 'POST'])
@require_auth
def admin_security():
    """Security settings page - access codes and checkout settings"""
    conn = get_db()
    
    if request.method == 'POST':
        # Handle password changes
        if request.form.get('new_password') or request.form.get('new_override_password'):
            # Update login access code
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                set_app_password(new_password)
                flash('Login access code updated successfully!', 'success')
            
            # Update admin override checkout code
            new_override = request.form.get('new_override_password', '').strip()
            if new_override:
                set_override_password(new_override)
                flash('Admin override checkout code updated successfully!', 'success')
        
        # Handle label printing settings
        elif 'require_checkout_code' in request.form or 'checkout_code_method' in request.form:
            require_codes = 'true' if request.form.get('require_checkout_code') else 'false'
            checkout_code_method = request.form.get('checkout_code_method', 'qr')
            printer_type = request.form.get('label_printer_type', 'dymo')
            label_size = request.form.get('label_size', '30336')
            
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('require_checkout_code', ?)", (require_codes,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('checkout_code_method', ?)", (checkout_code_method,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_printer_type', ?)", (printer_type,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_size', ?)", (label_size,))
            conn.commit()
            flash('Checkout code settings updated successfully!', 'success')
        
        conn.close()
        return redirect(url_for('admin_security'))
    
    # GET request - fetch current settings
    current_password = get_app_password()
    current_override_password = get_override_password()
    
    # Check if override section is unlocked (persists during session)
    override_unlocked = session.get('override_unlocked', False)
    
    # Fetch label printing settings
    label_settings = {}
    for key in ['require_checkout_code', 'checkout_code_method', 'label_printer_type', 'label_size']:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        label_settings[key] = row[0] if row else None
    
    # Fetch YOURLS settings
    yourls_settings = {}
    for key in ['yourls_api_url', 'yourls_signature']:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        yourls_settings[key] = row[0] if row else None
    
    conn.close()
    
    return render_template('admin/security.html', 
                         branding=get_branding_settings(),
                         admin_password_set=bool(current_password),
                         require_login=override_unlocked)

# Trail Life Connect Integration Routes
@app.route('/admin/tlc', methods=['GET'])
@require_auth
def admin_tlc():
    branding = get_branding_settings()
    
    # Check if we have credentials in session
    if 'tlc_email' not in session or 'tlc_password' not in session:
        return render_template('admin/tlc_sync.html', step='login', branding=branding)
    
    # Try to fetch events
    try:
        client = TrailLifeConnectClient(session['tlc_email'], session['tlc_password'])
        if not client.login():
            flash('Login failed. Please check your credentials.', 'error')
            session.pop('tlc_email', None)
            session.pop('tlc_password', None)
            return render_template('admin/tlc_sync.html', step='login', branding=branding)
            
        events = client.get_upcoming_events()
        return render_template('admin/tlc_sync.html', step='events', events=events, branding=branding)
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('admin/tlc_sync.html', step='login', branding=branding)

@app.route('/admin/tlc/login', methods=['POST'])
@require_auth
def admin_tlc_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email and password:
        session['tlc_email'] = email
        session['tlc_password'] = password
        return redirect(url_for('admin_tlc'))
    
    flash('Please provide both email and password.', 'error')
    return redirect(url_for('admin_tlc'))

@app.route('/admin/tlc/sync/<event_id>', methods=['GET'])
@require_auth
def admin_tlc_sync_confirm(event_id):
    branding = get_branding_settings()
    
    if 'tlc_email' not in session:
        return redirect(url_for('admin_tlc'))
        
    client = TrailLifeConnectClient(session['tlc_email'], session['tlc_password'])
    if not client.login():
        return redirect(url_for('admin_tlc'))
        
    # 1. Get TLC Roster
    tlc_roster = client.get_event_roster(event_id) # Dict: Name -> ID
    
    # 2. Get Local Check-ins for today (or recent)
    # For now, we'll just get ALL kids currently checked in, or checked in today.
    # Let's assume the event is "today".
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    # Get all checkins for today
    checkins = conn.execute('''
        SELECT k.id, k.name, k.tlc_id, c.checkin_time 
        FROM checkins c
        JOIN kids k ON c.kid_id = k.id
        WHERE date(c.checkin_time) = ?
    ''', (today_str,)).fetchall()
    conn.close()
    
    matches = []
    
    # Helper for name normalization
    def normalize(n):
        return n.lower().replace(',', '').replace('.', '').strip()
    
    # 3. Match
    for checkin in checkins:
        local_name = checkin['name']
        local_tlc_id = checkin['tlc_id']
        local_norm = normalize(local_name)
        
        match_found = None
        
        # 1. Try ID match first
        if local_tlc_id:
            for tlc_name, tlc_id in tlc_roster.items():
                if tlc_id == local_tlc_id:
                    match_found = {'name': tlc_name, 'id': tlc_id}
                    break
        
        # 2. If no ID match, try name match
        if not match_found:
            # Try exact match first
            for tlc_name, tlc_id in tlc_roster.items():
                tlc_norm = normalize(tlc_name)
                
                # Check exact
                if local_norm == tlc_norm:
                    match_found = {'name': tlc_name, 'id': tlc_id}
                    break
                
                # Check "Last First" vs "First Last"
                parts = tlc_norm.split()
                if len(parts) >= 2:
                    # Swap first two parts
                    swapped = f"{parts[1]} {parts[0]}"
                    if local_norm == swapped:
                        match_found = {'name': tlc_name, 'id': tlc_id}
                        break
                    
        status = 'matched' if match_found else 'unmatched'
        
        matches.append({
            'local_id': checkin['id'],
            'local_name': local_name,
            'tlc_name': match_found['name'] if match_found else None,
            'tlc_id': match_found['id'] if match_found else None,
            'status': status
        })
        
    return render_template('admin/tlc_sync.html', 
                         step='confirm', 
                         event_id=event_id, 
                         matches=matches, 
                         branding=branding)

@app.route('/admin/tlc/sync/<event_id>/execute', methods=['POST'])
@require_auth
def admin_tlc_sync_execute(event_id):
    if 'tlc_email' not in session:
        return redirect(url_for('admin_tlc'))
        
    client = TrailLifeConnectClient(session['tlc_email'], session['tlc_password'])
    if not client.login():
        return redirect(url_for('admin_tlc'))
        
    count = 0
    errors = 0
    
    # Iterate through form data
    # Look for sync_{local_id} checkboxes
    for key, value in request.form.items():
        if key.startswith('sync_') and value == 'on':
            local_id = key.replace('sync_', '')
            # Get the mapped TLC ID
            tlc_id = request.form.get(f'mapping_{local_id}')
            
            if tlc_id:
                # SAFE SYNC: We only mark attendance as Present (True).
                # We do NOT mark anyone as Absent (False).
                # This ensures that if someone is marked Present on TLC but not checked in locally,
                # their status on TLC is preserved (not overwritten).
                if client.mark_attendance(event_id, tlc_id, present=True):
                    count += 1
                else:
                    errors += 1
                    
    if errors > 0:
        flash(f'Synced {count} records, but {errors} failed.', 'warning')
    else:
        flash(f'Successfully synced {count} records to Trail Life Connect!', 'success')
        
    return redirect(url_for('admin_tlc'))

@app.route('/admin/tlc/roster', methods=['GET'])
@require_auth
def admin_tlc_roster():
    branding = get_branding_settings()
    if 'tlc_email' not in session:
        return redirect(url_for('admin_tlc'))
    
    client = TrailLifeConnectClient(session['tlc_email'], session['tlc_password'])
    if not client.login():
        return redirect(url_for('admin_tlc'))

    # We need an event to get the roster. 
    # If provided in args, use it. Otherwise try to find one.
    event_id = request.args.get('event_id')
    
    if not event_id:
        # Try to get the first upcoming event
        events = client.get_upcoming_events()
        if events:
            event_id = events[0]['id']
        else:
            flash("No upcoming events found to fetch roster from. Please ensure there is at least one event in TLC.", "warning")
            return redirect(url_for('admin_tlc'))
            
    tlc_roster = client.get_event_roster(event_id) # Dict: Name -> ID
    
    conn = get_db()
    kids = conn.execute("SELECT id, name, tlc_id FROM kids ORDER BY name").fetchall()
    conn.close()
    
    # Prepare options for dropdown
    tlc_options = [{'id': uid, 'name': name} for name, uid in tlc_roster.items()]
    tlc_options.sort(key=lambda x: x['name'])
    
    # Helper for name normalization
    def normalize(n):
        return n.lower().replace(',', '').replace('.', '').strip()

    roster_rows = []
    for kid in kids:
        current_tlc_id = kid['tlc_id']
        match_status = 'unlinked'
        suggested_id = current_tlc_id
        
        # If not linked, try to auto-match
        if not current_tlc_id:
            local_norm = normalize(kid['name'])
            for tlc_name, tlc_id in tlc_roster.items():
                tlc_norm = normalize(tlc_name)
                if local_norm == tlc_norm:
                    suggested_id = tlc_id
                    match_status = 'auto-match'
                    break
                # Check swapped
                parts = tlc_norm.split()
                if len(parts) >= 2:
                    swapped = f"{parts[1]} {parts[0]}"
                    if local_norm == swapped:
                        suggested_id = tlc_id
                        match_status = 'auto-match'
                        break
        else:
            match_status = 'linked'
            
        roster_rows.append({
            'id': kid['id'],
            'name': kid['name'],
            'current_tlc_id': current_tlc_id,
            'suggested_id': suggested_id,
            'status': match_status
        })
        
    return render_template('admin/tlc_sync.html', 
                         step='roster', 
                         roster_rows=roster_rows, 
                         tlc_options=tlc_options, 
                         branding=branding)

@app.route('/admin/tlc/roster/save', methods=['POST'])
@require_auth
def admin_tlc_roster_save():
    conn = get_db()
    count = 0
    
    for key, value in request.form.items():
        if key.startswith('tlc_id_'):
            kid_id = key.replace('tlc_id_', '')
            tlc_id = value if value else None
            
            conn.execute("UPDATE kids SET tlc_id = ? WHERE id = ?", (tlc_id, kid_id))
            count += 1
            
    conn.commit()
    conn.close()
    
    flash(f"Updated roster links for {count} records.", "success")
    return redirect(url_for('admin_tlc'))



