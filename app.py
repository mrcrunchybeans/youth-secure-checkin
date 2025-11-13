from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests
from icalendar import Calendar
import pytz
import csv
import io
import re
import threading
import time
import secrets
import qrcode
from io import BytesIO
import base64
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

DB_PATH = Path(__file__).parent / 'checkin.db'

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

# File upload configuration
UPLOAD_FOLDER = Path(__file__).parent / 'static' / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

local_tz = pytz.timezone('America/Chicago')  # Adjust to your local timezone

# Developer password from environment variable for security
# Falls back to None if not set (disables developer override features)
DEVELOPER_PASSWORD = os.getenv('DEVELOPER_PASSWORD', None)

@app.context_processor
def inject_branding():
    """Make branding settings available to all templates"""
    return {'branding': get_branding_settings()}

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
    return row['value'] if row else 'traillife2024'

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
    """Generate a secure random token for sharing checkout codes"""
    return secrets.token_urlsafe(32)

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

            response = requests.get(ical_url, timeout=10)
            response.raise_for_status()
            cal = Calendar.from_ical(response.text)

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
        cur = conn.execute("""
            SELECT id, name FROM events
            WHERE start_time >= datetime('now', '-1 month') AND start_time <= datetime('now', '+1 month')
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

    cur2 = conn.execute("SELECT id, name, start_time FROM events WHERE start_time >= datetime('now', '-1 month') AND start_time <= datetime('now', '+1 month') ORDER BY start_time DESC")
    events = cur2.fetchall()
    conn.close()

    return render_template('index.html', checked_in=checked_in, events=events, current_event_id=int(event_id))

@app.route('/checkin_last4', methods=['POST'])
@require_auth
def checkin_last4():
    last4 = request.form.get('last4', '').strip()
    event_id = request.form.get('event_id')
    if not last4 or len(last4) != 4 or not last4.isdigit():
        return jsonify({'error': 'Invalid last 4 digits'}), 400
    conn = get_db()
    cur = conn.execute("""
        SELECT f.id, f.phone, f.troop, f.default_adult_id,
               (SELECT GROUP_CONCAT(a.id || ':' || a.name)
                FROM adults a WHERE a.family_id = f.id) as adults,
               (SELECT GROUP_CONCAT(k.id || ':' || k.name || ':' || COALESCE(k.notes, ''))
                FROM kids k WHERE k.family_id = f.id) as kids
        FROM families f
        WHERE f.phone LIKE ?
    """, ('%' + last4,))
    families = cur.fetchall()
    
    if not families:
        conn.close()
        return jsonify({'error': 'No family found with that phone ending'}), 404
    
    # Assume first match; in real app, handle multiples
    family = families[0]
    adults = [adult.split(':', 1) for adult in family['adults'].split(',')] if family['adults'] else []
    adults = [{'id': int(a[0]), 'name': a[1]} for a in adults]
    kids = [kid.split(':', 2) for kid in family['kids'].split(',')] if family['kids'] else []
    kids = [{'id': int(k[0]), 'name': k[1], 'notes': k[2] if len(k) > 2 else ''} for k in kids]
    
    # Check which kids are already checked in to this event
    if event_id:
        checked_in_kids = set()
        for kid in kids:
            checkin = conn.execute("""
                SELECT id FROM checkins 
                WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL
            """, (kid['id'], event_id)).fetchone()
            if checkin:
                checked_in_kids.add(kid['id'])
        
        # Mark kids as already checked in
        for kid in kids:
            kid['already_checked_in'] = kid['id'] in checked_in_kids
    
    conn.close()
    
    return jsonify({
        'family_id': family['id'],
        'phone': family['phone'],
        'troop': family['troop'],
        'default_adult_id': family['default_adult_id'],
        'adults': adults,
        'kids': kids
    })

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
    
    # Generate share token and QR code if codes were generated and method includes QR
    share_token = None
    qr_code_data = None
    if checkout_method in ['qr', 'both'] and checked_in_data and len(checked_in_data) > 0 and any(c['id'] for c in checked_in_data):
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
        cur = conn.execute("""
            SELECT id, name FROM events
            WHERE start_time >= datetime('now', '-1 month') AND start_time <= datetime('now', '+1 month')
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

    cur2 = conn.execute("SELECT id, name, start_time FROM events WHERE start_time >= datetime('now', '-1 month') AND start_time <= datetime('now', '+1 month') ORDER BY start_time DESC")
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

# Admin routes
@app.route('/admin')
@require_auth
def admin_index():
    return render_template('admin/index.html')

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
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@require_auth
def admin_settings():
    conn = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        # Handle branding updates
        if action == 'update_branding':
            organization_name = request.form.get('organization_name', '').strip()
            organization_type = request.form.get('organization_type', 'other')
            group_term = request.form.get('group_term', 'Group').strip()
            primary_color = request.form.get('primary_color', '#79060d').strip()
            secondary_color = request.form.get('secondary_color', '#003b59').strip()
            accent_color = request.form.get('accent_color', '#4a582d').strip()
            
            if organization_name:
                set_branding_setting('organization_name', organization_name)
                set_branding_setting('organization_type', organization_type)
                set_branding_setting('group_term', group_term)
                set_branding_setting('group_term_lower', group_term.lower())
                set_branding_setting('primary_color', primary_color)
                set_branding_setting('secondary_color', secondary_color)
                set_branding_setting('accent_color', accent_color)
                flash('Organization branding updated successfully!', 'success')
            else:
                flash('Organization name is required', 'danger')
            
            return redirect(url_for('admin_settings'))
        
        # Handle logo upload
        elif action == 'upload_logo':
            if 'logo_file' not in request.files:
                flash('No file selected', 'danger')
            else:
                file = request.files['logo_file']
                if file.filename == '':
                    flash('No file selected', 'danger')
                elif not allowed_file(file.filename):
                    flash('Invalid file type. Please upload PNG, JPG, or SVG.', 'danger')
                else:
                    # Delete old logo if exists
                    old_logo = get_logo_filename()
                    if old_logo:
                        old_path = app.config['UPLOAD_FOLDER'] / old_logo
                        if old_path.exists():
                            old_path.unlink()
                    
                    # Save new logo
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid caching issues
                    name, ext = os.path.splitext(filename)
                    filename = f"logo_{int(time.time())}{ext}"
                    filepath = app.config['UPLOAD_FOLDER'] / filename
                    file.save(str(filepath))
                    
                    set_logo_filename(filename)
                    flash('Logo uploaded successfully!', 'success')
        
        # Handle logo removal
        elif action == 'remove_logo':
            old_logo = get_logo_filename()
            if old_logo:
                old_path = app.config['UPLOAD_FOLDER'] / old_logo
                if old_path.exists():
                    old_path.unlink()
                set_logo_filename(None)
                flash('Logo removed successfully!', 'success')
        
        # Handle favicon upload
        elif action == 'upload_favicon':
            if 'favicon_file' not in request.files:
                flash('No file selected', 'danger')
            else:
                file = request.files['favicon_file']
                if file.filename == '':
                    flash('No file selected', 'danger')
                elif not allowed_file(file.filename, allowed_extensions={'png', 'jpg', 'jpeg', 'ico'}):
                    flash('Invalid file type. Please upload ICO, PNG, or JPG.', 'danger')
                else:
                    # Delete old favicon if exists
                    old_favicon = get_favicon_filename()
                    if old_favicon:
                        old_path = app.config['UPLOAD_FOLDER'] / old_favicon
                        if old_path.exists():
                            old_path.unlink()
                    
                    # Save new favicon
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid caching issues
                    name, ext = os.path.splitext(filename)
                    filename = f"favicon_{int(time.time())}{ext}"
                    filepath = app.config['UPLOAD_FOLDER'] / filename
                    file.save(str(filepath))
                    
                    set_favicon_filename(filename)
                    flash('Favicon uploaded successfully!', 'success')
        
        # Handle favicon removal
        elif action == 'remove_favicon':
            old_favicon = get_favicon_filename()
            if old_favicon:
                old_path = app.config['UPLOAD_FOLDER'] / old_favicon
                if old_path.exists():
                    old_path.unlink()
                set_favicon_filename(None)
                flash('Favicon removed successfully!', 'success')
        
        # Handle password changes
        elif request.form.get('new_password') or request.form.get('new_override_password'):
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
        
        # Handle label printing settings (check if any label setting fields are present)
        elif 'label_printer_type' in request.form or 'label_size' in request.form or 'checkout_code_method' in request.form:
            # Checkbox only appears in form data if checked, so we check explicitly
            require_codes = 'true' if request.form.get('require_checkout_code') == 'on' else 'false'
            checkout_code_method = request.form.get('checkout_code_method', 'qr').strip()
            printer_type = request.form.get('label_printer_type', 'dymo').strip()
            label_size = request.form.get('label_size', '30336').strip()
            
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('require_checkout_code', ?)", (require_codes,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('checkout_code_method', ?)", (checkout_code_method,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_printer_type', ?)", (printer_type,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_size', ?)", (label_size,))
            conn.commit()
            flash('Checkout code settings updated successfully!', 'success')
        
        conn.close()
        return redirect(url_for('admin_settings'))
    
    # GET request - fetch current settings
    current_password = get_app_password()
    current_override_password = get_override_password()
    current_logo = get_logo_filename()
    current_favicon = get_favicon_filename()
    
    # Check if override section is unlocked (persists during session)
    override_unlocked = session.get('override_unlocked', False)
    
    # Fetch label printing settings
    label_settings = {}
    for key in ['require_checkout_code', 'checkout_code_method', 'label_printer_type', 'label_size']:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        label_settings[key] = row[0] if row else None
    
    conn.close()
    
    return render_template('admin/settings.html', 
                         current_password=current_password,
                         current_override_password=current_override_password,
                         override_unlocked=override_unlocked,
                         dev_password_set=bool(DEVELOPER_PASSWORD),
                         label_settings=label_settings,
                         current_logo=current_logo,
                         current_favicon=current_favicon)

@app.route('/admin/families')
@require_auth
def admin_families():
    conn = get_db()
    cur = conn.execute("""
        SELECT f.id, f.phone, f.troop,
               (SELECT GROUP_CONCAT(name, ', ') FROM adults WHERE family_id = f.id) as adults,
               (SELECT GROUP_CONCAT(name, ', ') FROM kids WHERE family_id = f.id) as kids
        FROM families f
        ORDER BY f.phone
    """)
    families = cur.fetchall()
    conn.close()
    return render_template('admin/families.html', families=families)

@app.route('/admin/families/add', methods=['GET', 'POST'])
@require_auth
def admin_add_family():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        troop = request.form.get('troop', '').strip()
        authorized_adults = request.form.get('authorized_adults', '').strip()
        adults = request.form.getlist('adults')
        kids = request.form.getlist('kids')
        kid_notes = request.form.getlist('kid_notes')
        default_adult_index = request.form.get('default_adult_index', '').strip()
        if not phone:
            flash('Phone required', 'danger')
            return redirect(request.url)
        conn = get_db()
        try:
            cur = conn.execute("INSERT INTO families (phone, troop, authorized_adults) VALUES (?, ?, ?)", 
                              (phone, troop, authorized_adults if authorized_adults else None))
            family_id = cur.lastrowid
            
            # Track adult IDs to set default
            adult_ids = []
            for adult in adults:
                if adult.strip():
                    cur = conn.execute("INSERT INTO adults (family_id, name) VALUES (?, ?)", (family_id, adult.strip()))
                    adult_ids.append(cur.lastrowid)
            
            # Insert kids with their notes
            for i, kid in enumerate(kids):
                if kid.strip():
                    note = kid_notes[i].strip() if i < len(kid_notes) else ''
                    conn.execute("INSERT INTO kids (family_id, name, notes) VALUES (?, ?, ?)", 
                                (family_id, kid.strip(), note if note else None))
            
            # Set default adult if specified
            if default_adult_index and default_adult_index.isdigit():
                idx = int(default_adult_index)
                if 0 <= idx < len(adult_ids):
                    conn.execute("UPDATE families SET default_adult_id = ? WHERE id = ?", (adult_ids[idx], family_id))
            
            conn.commit()
            flash('Family added', 'success')
            return redirect(url_for('admin_families'))
        except sqlite3.IntegrityError:
            flash('Phone already exists', 'danger')
        finally:
            conn.close()
    return render_template('admin/add_family.html')

@app.route('/admin/families/import', methods=['GET', 'POST'])
@require_auth
def admin_import_families():
    if request.method == 'POST':
        troop = request.form.get('troop', '').strip()
        file = request.files.get('file')
        if not troop or not file:
            flash('Troop and file required', 'danger')
            return redirect(request.url)
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
            reader = csv.DictReader(stream)
            families = {}
            for row in reader:
                last_name = row.get('Last Name', '').strip()
                first_name = row.get('First Name', '').strip()
                youth = row.get('Youth', '').strip().upper() == 'Y'
                mobile = row.get('Mobile Phone', '').strip()
                home = row.get('Home Phone', '').strip()
                work = row.get('Work Phone', '').strip()
                phone = mobile or home or work
                address = row.get('Address Line 1', '').strip()
                if not last_name or not first_name or not address:
                    continue
                norm_addr = normalize_address(address)
                key = (last_name, norm_addr)
                if key not in families:
                    families[key] = {'phones': [], 'troop': troop, 'adults': [], 'kids': []}
                name = f"{first_name} {last_name}"
                if youth:
                    families[key]['kids'].append(name)
                else:
                    families[key]['adults'].append(name)
                    if phone:
                        families[key]['phones'].append(phone)
            conn = get_db()
            imported = 0
            for fam_data in families.values():
                if not fam_data['phones']:
                    last4 = None
                else:
                    last4 = fam_data['phones'][0][-4:] if len(fam_data['phones'][0]) >= 4 else fam_data['phones'][0]
                try:
                    # Insert new family
                    cur = conn.execute("INSERT INTO families (phone, troop) VALUES (?, ?)", (last4, fam_data['troop']))
                    family_id = cur.lastrowid
                    for adult in fam_data['adults']:
                        conn.execute("INSERT INTO adults (family_id, name) VALUES (?, ?)", (family_id, adult))
                    for kid in fam_data['kids']:
                        conn.execute("INSERT INTO kids (family_id, name) VALUES (?, ?)", (family_id, kid))
                    imported += 1
                except Exception as e:
                    flash(f'Error importing family {fam_data["adults"][0] if fam_data["adults"] else "unknown"}: {e}', 'danger')
                    continue
            conn.commit()
            flash(f'Imported {imported} families', 'success')
        except Exception as e:
            flash(f'Error parsing CSV: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('admin_families'))
    return render_template('admin/import_families.html')

@app.route('/admin/families/edit/<int:family_id>', methods=['GET', 'POST'])
@require_auth
def admin_edit_family(family_id):
    conn = get_db()
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        troop = request.form.get('troop', '').strip()
        authorized_adults = request.form.get('authorized_adults', '').strip()
        adults = request.form.getlist('adults')
        adult_ids = request.form.getlist('adult_ids')
        kids = request.form.getlist('kids')
        kid_ids = request.form.getlist('kid_ids')
        kid_notes = request.form.getlist('kid_notes')
        default_adult_id = request.form.get('default_adult_id', '').strip()
        if not phone:
            phone = None
        try:
            # Update family including authorized_adults and default_adult_id
            final_default_id = int(default_adult_id) if default_adult_id and default_adult_id.isdigit() else None
            conn.execute("UPDATE families SET phone = ?, troop = ?, authorized_adults = ?, default_adult_id = ? WHERE id = ?", 
                        (phone, troop, authorized_adults if authorized_adults else None, final_default_id, family_id))
            
            # Update adults: UPDATE existing, INSERT new, DELETE removed
            existing_adult_ids = set()
            for i, adult_name in enumerate(adults):
                if adult_name.strip():
                    adult_id = adult_ids[i] if i < len(adult_ids) and adult_ids[i] else None
                    if adult_id:
                        # Update existing adult
                        conn.execute("UPDATE adults SET name = ? WHERE id = ? AND family_id = ?", 
                                    (adult_name.strip(), adult_id, family_id))
                        existing_adult_ids.add(int(adult_id))
                    else:
                        # Insert new adult
                        conn.execute("INSERT INTO adults (family_id, name) VALUES (?, ?)", 
                                    (family_id, adult_name.strip()))
            
            # Delete adults that were removed
            all_adults = conn.execute("SELECT id FROM adults WHERE family_id = ?", (family_id,)).fetchall()
            for adult in all_adults:
                if adult['id'] not in existing_adult_ids:
                    conn.execute("DELETE FROM adults WHERE id = ?", (adult['id'],))
            
            # Update kids: UPDATE existing, INSERT new, DELETE removed
            existing_kid_ids = set()
            for i, kid_name in enumerate(kids):
                if kid_name.strip():
                    kid_id = kid_ids[i] if i < len(kid_ids) and kid_ids[i] else None
                    note = kid_notes[i].strip() if i < len(kid_notes) else ''
                    if kid_id:
                        # Update existing kid
                        conn.execute("UPDATE kids SET name = ?, notes = ? WHERE id = ? AND family_id = ?", 
                                    (kid_name.strip(), note if note else None, kid_id, family_id))
                        existing_kid_ids.add(int(kid_id))
                    else:
                        # Insert new kid
                        conn.execute("INSERT INTO kids (family_id, name, notes) VALUES (?, ?, ?)", 
                                    (family_id, kid_name.strip(), note if note else None))
            
            # Delete kids that were removed
            all_kids = conn.execute("SELECT id FROM kids WHERE family_id = ?", (family_id,)).fetchall()
            for kid in all_kids:
                if kid['id'] not in existing_kid_ids:
                    conn.execute("DELETE FROM kids WHERE id = ?", (kid['id'],))
            conn.commit()
            flash('Family updated', 'success')
            return redirect(url_for('admin_families'))
        except sqlite3.IntegrityError:
            flash('Phone already exists', 'danger')
        finally:
            conn.close()
    else:
        # GET
        family = conn.execute("SELECT * FROM families WHERE id = ?", (family_id,)).fetchone()
        adults = conn.execute("SELECT * FROM adults WHERE family_id = ?", (family_id,)).fetchall()
        kids = conn.execute("SELECT * FROM kids WHERE family_id = ?", (family_id,)).fetchall()
        conn.close()
        if not family:
            flash('Family not found', 'danger')
            return redirect(url_for('admin_families'))
        return render_template('admin/edit_family.html', family=family, adults=adults, kids=kids)

@app.route('/admin/families/clear', methods=['POST'])
@require_auth
def admin_clear_families():
    conn = get_db()
    conn.execute("DELETE FROM kids")
    conn.execute("DELETE FROM adults")
    conn.execute("DELETE FROM families")
    conn.commit()
    conn.close()
    flash('All families cleared', 'success')
    return redirect(url_for('admin_families'))

@app.route('/admin/events')
@require_auth
def admin_events():
    conn = get_db()
    cur = conn.execute("SELECT * FROM events ORDER BY start_time DESC")
    events = cur.fetchall()
    cur2 = conn.execute("SELECT value FROM settings WHERE key = 'ical_url'")
    ical_row = cur2.fetchone()
    ical_url = ical_row['value'] if ical_row else None
    cur3 = conn.execute("SELECT value FROM settings WHERE key = 'last_ical_sync'")
    last_sync_row = cur3.fetchone()
    last_sync = last_sync_row['value'] if last_sync_row else None
    if last_sync:
        # Format the last sync time
        dt = datetime.fromisoformat(last_sync).replace(tzinfo=pytz.UTC).astimezone(local_tz)
        last_sync_formatted = dt.strftime('%b %d, %Y %I:%M %p')
    else:
        last_sync_formatted = 'Never'
    conn.close()
    return render_template('admin/events.html', events=events, ical_url=ical_url, last_sync=last_sync_formatted)

@app.route('/admin/events/set_ical', methods=['POST'])
@require_auth
def admin_set_ical():
    ical_url = request.form.get('ical_url', '').strip()
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('ical_url', ?)", (ical_url,))
    conn.commit()
    conn.close()
    flash('iCal URL saved', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/events/sync', methods=['POST'])
@require_auth
def admin_sync_ical():
    success, message = sync_ical_events()
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin_events'))

@app.route('/admin/events/import', methods=['GET', 'POST'])
@require_auth
def admin_import_events():
    if request.method == 'POST':
        ical_url = request.form.get('ical_url', '').strip()
        if not ical_url:
            flash('iCal URL required', 'danger')
            return redirect(request.url)
        try:
            response = requests.get(ical_url)
            response.raise_for_status()
            cal = Calendar.from_ical(response.text)
            conn = get_db()
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
                    if start_time:
                        conn.execute("INSERT OR IGNORE INTO events (name, start_time, end_time, description) VALUES (?, ?, ?, ?)",
                                     (name, start_time, end_time, description))
            conn.commit()
            conn.close()
            flash('Events imported successfully', 'success')
        except Exception as e:
            flash(f'Error importing: {str(e)}', 'danger')
        return redirect(url_for('admin_events'))
    return render_template('admin/import_events.html')

if __name__ == '__main__':
    # ensure DB exists when running the server directly
    ensure_db()
    
    # Clean up expired tokens on startup
    cleanup_expired_tokens()
    
    # Start background thread to clean up tokens periodically
    def periodic_cleanup():
        while True:
            time.sleep(3600)  # Run every hour
            cleanup_expired_tokens()
    
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
