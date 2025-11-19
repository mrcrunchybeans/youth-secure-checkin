#!/usr/bin/env python3
"""
Test script to verify demo setup works correctly
"""

import sqlite3
import sys
from pathlib import Path

def test_demo_database():
    """Test that demo database is properly seeded"""
    db_path = Path('data/demo.db')
    
    if not db_path.exists():
        print("❌ Demo database does not exist")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check families exist
    cur = conn.execute("SELECT COUNT(*) as count FROM families")
    family_count = cur.fetchone()['count']
    if family_count >= 8:
        print(f"✓ Families: {family_count} families found")
        tests_passed += 1
    else:
        print(f"✗ Families: Expected at least 8, found {family_count}")
        tests_failed += 1
    
    # Test 2: Check kids exist
    cur = conn.execute("SELECT COUNT(*) as count FROM kids")
    kid_count = cur.fetchone()['count']
    if kid_count >= 10:
        print(f"✓ Kids: {kid_count} kids found")
        tests_passed += 1
    else:
        print(f"✗ Kids: Expected at least 10, found {kid_count}")
        tests_failed += 1
    
    # Test 3: Check adults exist
    cur = conn.execute("SELECT COUNT(*) as count FROM adults")
    adult_count = cur.fetchone()['count']
    if adult_count >= 8:
        print(f"✓ Adults: {adult_count} adults found")
        tests_passed += 1
    else:
        print(f"✗ Adults: Expected at least 8, found {adult_count}")
        tests_failed += 1
    
    # Test 4: Check events exist
    cur = conn.execute("SELECT COUNT(*) as count FROM events")
    event_count = cur.fetchone()['count']
    if event_count >= 6:
        print(f"✓ Events: {event_count} events found")
        tests_passed += 1
    else:
        print(f"✗ Events: Expected at least 6, found {event_count}")
        tests_failed += 1
    
    # Test 5: Check check-ins exist
    cur = conn.execute("SELECT COUNT(*) as count FROM checkins")
    checkin_count = cur.fetchone()['count']
    if checkin_count > 0:
        print(f"✓ Check-ins: {checkin_count} check-ins found")
        tests_passed += 1
    else:
        print(f"✗ Check-ins: Expected > 0, found {checkin_count}")
        tests_failed += 1
    
    # Test 6: Check demo settings
    cur = conn.execute("SELECT value FROM settings WHERE key = 'troop_name'")
    troop = cur.fetchone()
    if troop and 'Demo' in troop['value']:
        print(f"✓ Settings: Demo troop configured ({troop['value']})")
        tests_passed += 1
    else:
        print(f"✗ Settings: Demo troop not found")
        tests_failed += 1
    
    # Test 7: Check specific test family
    cur = conn.execute("SELECT COUNT(*) as count FROM families WHERE phone = '555-0101'")
    test_family = cur.fetchone()['count']
    if test_family == 1:
        print(f"✓ Test Data: Johnson family (555-0101) exists")
        tests_passed += 1
    else:
        print(f"✗ Test Data: Johnson family not found")
        tests_failed += 1
    
    conn.close()
    
    print("\n" + "="*50)
    print(f"Tests Passed: {tests_passed}/{tests_passed + tests_failed}")
    print("="*50)
    
    return tests_failed == 0


if __name__ == '__main__':
    print("="*50)
    print("Testing Demo Database Setup")
    print("="*50 + "\n")
    
    success = test_demo_database()
    sys.exit(0 if success else 1)
