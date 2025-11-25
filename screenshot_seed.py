#!/usr/bin/env python3
"""
Screenshot Data Seed Script for Youth Secure Check-in
Generates realistic pseudodata for marketing screenshots
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
import random
import json

# Screenshot configuration
TROOP_NAME = "Troop 101"
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/screenshots.db')

# Families with realistic names
FAMILIES = [
    {
        'phone': '555-0101',
        'troop': TROOP_NAME,
        'adults': ['Sarah Johnson', 'Mike Johnson'],
        'kids': [
            {'name': 'Emma Johnson', 'notes': 'Allergic to peanuts'},
            {'name': 'Noah Johnson', 'notes': ''}
        ]
    },
    {
        'phone': '555-0102',
        'troop': TROOP_NAME,
        'adults': ['Jennifer Smith'],
        'kids': [
            {'name': 'Olivia Smith', 'notes': 'Needs inhaler for asthma'},
        ]
    },
    {
        'phone': '555-0103',
        'troop': TROOP_NAME,
        'adults': ['David Williams', 'Lisa Williams'],
        'kids': [
            {'name': 'Liam Williams', 'notes': ''},
            {'name': 'Sophia Williams', 'notes': 'Vegetarian meals only'}
        ]
    },
    {
        'phone': '555-0104',
        'troop': TROOP_NAME,
        'adults': ['Robert Brown'],
        'kids': [
            {'name': 'Mason Brown', 'notes': ''},
        ]
    },
    {
        'phone': '555-0105',
        'troop': TROOP_NAME,
        'adults': ['Maria Garcia', 'Carlos Garcia'],
        'kids': [
            {'name': 'Isabella Garcia', 'notes': ''},
            {'name': 'Ethan Garcia', 'notes': 'Wears glasses'},
            {'name': 'Ava Garcia', 'notes': ''}
        ]
    },
    {
        'phone': '555-0106',
        'troop': TROOP_NAME,
        'adults': ['Amanda Martinez'],
        'kids': [
            {'name': 'Lucas Martinez', 'notes': ''},
        ]
    },
    {
        'phone': '555-0107',
        'troop': TROOP_NAME,
        'adults': ['James Anderson', 'Emily Anderson'],
        'kids': [
            {'name': 'Charlotte Anderson', 'notes': 'Lactose intolerant'},
            {'name': 'Benjamin Anderson', 'notes': ''}
        ]
    },
    {
        'phone': '555-0108',
        'troop': TROOP_NAME,
        'adults': ['Patricia Taylor'],
        'kids': [
            {'name': 'Amelia Taylor', 'notes': ''},
        ]
    },
]

# Events - dates are relative to current date
EVENTS = [
    {
        'name': 'Leadership Training',
        'start_offset_days': -28,
        'start_hour': 9,
        'duration_hours': 6,
        'description': 'Youth leadership development workshop'
    },
    {
        'name': 'Service Project - Park Cleanup',
        'start_offset_days': -21,
        'start_hour': 10,
        'duration_hours': 4,
        'description': 'Community service: cleaning up local park trails'
    },
    {
        'name': 'Weekend Camping Trip',
        'start_offset_days': -14,
        'start_hour': 9,
        'duration_hours': 48,
        'description': 'Two-day camping trip at Pine Ridge State Park'
    },
    {
        'name': 'Weekly Troop Meeting',
        'start_offset_days': -7,
        'start_hour': 18,
        'duration_hours': 2,
        'description': 'Regular weekly troop meeting with badge work and activities'
    },
    {
        'name': 'Weekly Troop Meeting',
        'start_offset_days': 0,
        'start_hour': 18,
        'duration_hours': 2,
        'description': 'Regular weekly troop meeting with badge work and activities'
    },
    {
        'name': 'Social Event',
        'start_offset_days': 7,
        'start_hour': 14,
        'duration_hours': 3,
        'description': 'Group celebration with games and activities'
    },
    {
        'name': 'Merit Badge Workshop',
        'start_offset_days': 14,
        'start_hour': 13,
        'duration_hours': 4,
        'description': 'Focused workshop for First Aid and Emergency Preparedness badges'
    },
    {
        'name': 'Family Campout',
        'start_offset_days': 21,
        'start_hour': 17,
        'duration_hours': 40,
        'description': 'Weekend family camping trip with outdoor activities'
    },
]

# Settings for screenshots - NO DEMO MODE
SETTINGS = {
    'troop_name': TROOP_NAME,
    'troop_number': '101',
    'council_name': 'National Council',
    'organization_name': 'Troop 101',
    'primary_color': '#0a3161',
    'secondary_color': '#ce1126',
    'logo_filename': '',
    'timezone': 'America/Chicago',
    'checkout_enabled': '1',
    'require_checkout_code': 'true',
    'checkout_code_method': 'qr',
    'demo_mode': 'false',  # Disabled for screenshots
    'demo_banner': '',
    'admin_password_hash': 'pbkdf2:sha256:260000$demo$5d8c8a8e8f9e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f',  # password: demo123
    'is_setup_complete': 'true',
    'app_password': 'demo123',
}


def init_database():
    """Initialize database with schema"""
    # Ensure data directory exists
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database if it exists
    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing database: {DATABASE_PATH}")
    
    # Create new database
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    # Load and execute schema
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path) as f:
        conn.executescript(f.read())
    
    conn.commit()
    print(f"Initialized database: {DATABASE_PATH}")
    return conn


def seed_families_and_kids(conn):
    """Seed families, adults, and kids"""
    family_ids = []
    adult_ids = {}
    kid_ids = {}
    
    for fam_data in FAMILIES:
        # Insert family
        cur = conn.execute(
            "INSERT INTO families (phone, troop) VALUES (?, ?)",
            (fam_data['phone'], fam_data['troop'])
        )
        family_id = cur.lastrowid
        family_ids.append(family_id)
        
        # Insert adults
        family_adult_ids = []
        for adult_name in fam_data['adults']:
            cur = conn.execute(
                "INSERT INTO adults (family_id, name) VALUES (?, ?)",
                (family_id, adult_name)
            )
            adult_id = cur.lastrowid
            family_adult_ids.append(adult_id)
        
        # Set default adult to first adult in list
        if family_adult_ids:
            conn.execute(
                "UPDATE families SET default_adult_id = ? WHERE id = ?",
                (family_adult_ids[0], family_id)
            )
            adult_ids[family_id] = family_adult_ids
        
        # Insert kids
        family_kid_ids = []
        for kid_data in fam_data['kids']:
            cur = conn.execute(
                "INSERT INTO kids (family_id, name, notes) VALUES (?, ?, ?)",
                (family_id, kid_data['name'], kid_data['notes'])
            )
            kid_id = cur.lastrowid
            family_kid_ids.append(kid_id)
        
        kid_ids[family_id] = family_kid_ids
    
    conn.commit()
    print(f"Seeded {len(family_ids)} families with adults and kids")
    return family_ids, adult_ids, kid_ids


def seed_events(conn):
    """Seed events"""
    event_ids = []
    now = datetime.now()
    
    for event_data in EVENTS:
        start_time = now + timedelta(days=event_data['start_offset_days'])
        start_time = start_time.replace(hour=event_data['start_hour'], minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=event_data['duration_hours'])
        
        cur = conn.execute(
            "INSERT INTO events (name, start_time, end_time, description) VALUES (?, ?, ?, ?)",
            (
                event_data['name'],
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                event_data['description']
            )
        )
        event_ids.append(cur.lastrowid)
    
    conn.commit()
    print(f"Seeded {len(event_ids)} events")
    return event_ids


def seed_checkins(conn, family_ids, adult_ids, kid_ids, event_ids):
    """Seed check-ins for past and current events"""
    checkin_count = 0
    now = datetime.now()
    
    # Get all events
    for event_id in event_ids:
        cur = conn.execute("SELECT start_time, end_time FROM events WHERE id = ?", (event_id,))
        event = cur.fetchone()
        event_start = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
        event_end = datetime.strptime(event['end_time'], '%Y-%m-%d %H:%M:%S')
        
        is_past = event_end < now
        is_current = event_start <= now <= event_end
        
        if not (is_past or is_current):
            continue
            
        # Randomly select 60-90% of families to attend
        attending_families = random.sample(family_ids, k=random.randint(int(len(family_ids) * 0.6), int(len(family_ids) * 0.9)))
        
        for family_id in attending_families:
            # Get all kids for this family
            family_kids = kid_ids.get(family_id, [])
            family_adults = adult_ids.get(family_id, [])
            
            if not family_kids or not family_adults:
                continue
            
            # Select random adult for drop-off
            adult_id = random.choice(family_adults)
            
            # Check in all kids in the family
            for kid_id in family_kids:
                # Check-in time: slightly randomized around event start
                checkin_offset = random.randint(-5, 15)  # -5 to +15 minutes
                checkin_time = event_start + timedelta(minutes=checkin_offset)
                
                # For past events, add checkout times
                if is_past:
                    # 80% of check-ins have checkout times
                    if random.random() < 0.8:
                        # Checkout time: slightly randomized around event end
                        checkout_offset = random.randint(-10, 5)
                        checkout_time = event_end + timedelta(minutes=checkout_offset)
                        checkout_code = f"{random.randint(1000, 9999)}"
                        
                        conn.execute(
                            "INSERT INTO checkins (kid_id, adult_id, event_id, checkin_time, checkout_time, checkout_code) VALUES (?, ?, ?, ?, ?, ?)",
                            (kid_id, adult_id, event_id, checkin_time.strftime('%Y-%m-%d %H:%M:%S'), 
                             checkout_time.strftime('%Y-%m-%d %H:%M:%S'), checkout_code)
                        )
                    else:
                        # Forgot to checkout
                        conn.execute(
                            "INSERT INTO checkins (kid_id, adult_id, event_id, checkin_time) VALUES (?, ?, ?, ?)",
                            (kid_id, adult_id, event_id, checkin_time.strftime('%Y-%m-%d %H:%M:%S'))
                        )
                elif is_current:
                    # For current event, just check in (no checkout yet)
                    conn.execute(
                        "INSERT INTO checkins (kid_id, adult_id, event_id, checkin_time) VALUES (?, ?, ?, ?)",
                        (kid_id, adult_id, event_id, checkin_time.strftime('%Y-%m-%d %H:%M:%S'))
                    )
                
                checkin_count += 1
    
    conn.commit()
    print(f"Seeded {checkin_count} check-ins")


def seed_settings(conn):
    """Seed application settings"""
    for key, value in SETTINGS.items():
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    conn.commit()
    print(f"Seeded {len(SETTINGS)} settings")


def main():
    """Main seeding function"""
    print("=" * 50)
    print("Youth Secure Check-in - Screenshot Data Seeder")
    print("=" * 50)
    
    # Initialize database
    conn = init_database()
    
    # Seed data
    family_ids, adult_ids, kid_ids = seed_families_and_kids(conn)
    event_ids = seed_events(conn)
    seed_checkins(conn, family_ids, adult_ids, kid_ids, event_ids)
    seed_settings(conn)
    
    conn.close()
    
    print("=" * 50)
    print("✓ Screenshot database seeded successfully!")
    print(f"Database location: {DATABASE_PATH}")
    print(f"Login credentials:")
    print(f"  Password: demo123")
    print("=" * 50)


if __name__ == '__main__':
    main()
