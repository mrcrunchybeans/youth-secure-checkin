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
app.secret_key = 'dev-key-for-local'  # override in prod with env var

local_tz = pytz.timezone('America/Chicago')  # Adjust to your local timezone

# Hard-coded developer password - CHANGE THIS!
DEVELOPER_PASSWORD = 'dev2024secure'

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

def check_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_authenticated():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

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
    if not last4 or len(last4) != 4 or not last4.isdigit():
        return jsonify({'error': 'Invalid last 4 digits'}), 400
    conn = get_db()
    cur = conn.execute("""
        SELECT f.id, f.phone, f.troop, f.default_adult_id,
               GROUP_CONCAT(DISTINCT a.id || ':' || a.name) as adults,
               GROUP_CONCAT(DISTINCT k.id || ':' || k.name) as kids
        FROM families f
        LEFT JOIN adults a ON a.family_id = f.id
        LEFT JOIN kids k ON k.family_id = f.id
        WHERE f.phone LIKE ?
        GROUP BY f.id
    """, ('%' + last4,))
    families = cur.fetchall()
    conn.close()
    if not families:
        return jsonify({'error': 'No family found with that phone ending'}), 404
    # Assume first match; in real app, handle multiples
    family = families[0]
    adults = [adult.split(':', 1) for adult in family['adults'].split(',')] if family['adults'] else []
    adults = [{'id': int(a[0]), 'name': a[1]} for a in adults]
    kids = [kid.split(':', 1) for kid in family['kids'].split(',')] if family['kids'] else []
    kids = [{'id': int(k[0]), 'name': k[1]} for k in kids]
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
    
    # Check if label printing is enabled
    setting = conn.execute("SELECT value FROM settings WHERE key = 'require_checkout_code'").fetchone()
    require_codes = setting and setting[0] == 'true' and LABEL_PRINTING_AVAILABLE
    
    # Get label printer settings if needed
    if require_codes:
        printer_type = conn.execute("SELECT value FROM settings WHERE key = 'label_printer_type'").fetchone()
        label_width = conn.execute("SELECT value FROM settings WHERE key = 'label_width'").fetchone()
        label_height = conn.execute("SELECT value FROM settings WHERE key = 'label_height'").fetchone()
        printer_type = printer_type[0] if printer_type else 'dymo'
        label_width = float(label_width[0]) if label_width else 2.0
        label_height = float(label_height[0]) if label_height else 1.0
        
        # Get event info for label
        event_row = conn.execute("SELECT name, start_time FROM events WHERE id = ?", (event_id,)).fetchone()
        event_name = event_row[0] if event_row else "Event"
        event_date = event_row[1][:10] if event_row else datetime.now().strftime('%Y-%m-%d')
    
    checked_in_count = 0
    for kid_id in kid_ids:
        # Check if already checked in to this event
        cur = conn.execute("SELECT id FROM checkins WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL", (kid_id, event_id))
        if cur.fetchone():
            continue
        
        # Generate unique code if required
        checkout_code = None
        if require_codes and LABEL_PRINTING_AVAILABLE:
            try:
                checkout_code = generate_unique_code(int(event_id), str(DB_PATH))
            except Exception as e:
                print(f"Error generating checkout code: {e}")
                checkout_code = None
        
        # Insert check-in with code
        conn.execute("INSERT INTO checkins (kid_id, adult_id, event_id, checkin_time, checkout_code) VALUES (?, ?, ?, ?, ?)", 
                    (kid_id, adult_id, event_id, now, checkout_code))
        checked_in_count += 1
        
        # Print label if code was generated
        if checkout_code:
            try:
                kid_row = conn.execute("SELECT name FROM kids WHERE id = ?", (kid_id,)).fetchone()
                kid_name = kid_row[0] if kid_row else "Unknown"
                
                # Convert UTC to CST for display
                utc_time = datetime.fromisoformat(now).replace(tzinfo=pytz.UTC)
                cst_time = utc_time.astimezone(pytz.timezone('America/Chicago'))
                checkin_time = cst_time.strftime('%I:%M %p')
                
                print_checkout_label(
                    kid_name=kid_name,
                    event_name=event_name,
                    event_date=event_date,
                    checkin_time=checkin_time,
                    checkout_code=checkout_code,
                    printer_type=printer_type,
                    width=label_width,
                    height=label_height
                )
            except Exception as e:
                print(f"Error printing label: {e}")
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Checked in {checked_in_count} kid(s)'})

@app.route('/checkout/<int:kid_id>', methods=['POST'])
@require_auth
def checkout(kid_id):
    event_id = request.form.get('event_id')
    checkout_code = request.form.get('checkout_code', '').strip()
    
    if not event_id:
        return jsonify({'success': False, 'message': 'Missing event_id'}), 400
    
    conn = get_db()
    
    # Check if codes are required
    setting = conn.execute("SELECT value FROM settings WHERE key = 'require_checkout_code'").fetchone()
    require_codes = setting and setting[0] == 'true'
    
    # If codes are required, verify the code or admin password
    if require_codes:
        if not checkout_code:
            conn.close()
            return jsonify({'success': False, 'message': 'Checkout code required', 'code_required': True}), 400
        
        # Check if it's the admin password (override)
        app_password = get_app_password()
        is_admin_password = (checkout_code == app_password or checkout_code == DEVELOPER_PASSWORD)
        
        if not is_admin_password:
            # Verify the checkout code matches
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
    
    # Perform checkout
    now = datetime.utcnow().isoformat()
    conn.execute("UPDATE checkins SET checkout_time = ? WHERE kid_id = ? AND event_id = ? AND checkout_time IS NULL", 
                (now, kid_id, event_id))
    conn.commit()
    conn.close()
    
    # Return JSON if it's an AJAX request, otherwise redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Checked out successfully'})
    return redirect(request.referrer or url_for('kiosk'))

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

    conn.close()

    return render_template('kiosk.html', checked_in=checked_in, events=events, current_event_id=int(event_id), current_event_name=current_event_name, current_event_date=current_event_date)

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

@app.route('/admin/settings', methods=['GET', 'POST'])
@require_auth
def admin_settings():
    conn = get_db()
    
    if request.method == 'POST':
        # Handle password change
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            set_app_password(new_password)
            flash('App password updated successfully!', 'success')
        
        # Handle label printing settings (check if any label setting fields are present)
        if 'label_printer_type' in request.form or 'label_width' in request.form:
            # Checkbox only appears in form data if checked, so we check explicitly
            require_codes = 'true' if request.form.get('require_checkout_code') == 'on' else 'false'
            printer_type = request.form.get('label_printer_type', 'dymo').strip()
            label_width = request.form.get('label_width', '2.0').strip()
            label_height = request.form.get('label_height', '1.0').strip()
            
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('require_checkout_code', ?)", (require_codes,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_printer_type', ?)", (printer_type,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_width', ?)", (label_width,))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('label_height', ?)", (label_height,))
            conn.commit()
            flash('Label printing settings updated successfully!', 'success')
        
        conn.close()
        return redirect(url_for('admin_settings'))
    
    # GET request - fetch current settings
    current_password = get_app_password()
    
    # Fetch label printing settings
    label_settings = {}
    for key in ['require_checkout_code', 'label_printer_type', 'label_width', 'label_height']:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        label_settings[key] = row[0] if row else None
    
    conn.close()
    
    return render_template('admin/settings.html', 
                         current_password=current_password, 
                         dev_password_set=bool(DEVELOPER_PASSWORD),
                         label_settings=label_settings)

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
    app.run(host='0.0.0.0', port=5000, debug=True)
