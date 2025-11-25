import pytest
import sqlite3
from pathlib import Path
from app import app, get_db, init_db, DB_PATH

@pytest.fixture
def client():
    app.config['TESTING'] = True
    test_db = ':memory:'
    app.config['DATABASE'] = test_db
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    schema_path = Path(__file__).parent.parent / 'schema.sql'
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()
    with app.test_client() as client:
        yield client
    conn.close()

def test_index(client):
    rv = client.get('/')
    assert b'Check In' in rv.data

def test_checkin_last4(client):
    # Add a family
    conn = get_test_db()
    cur = conn.execute("INSERT INTO families (phone, troop) VALUES ('1234', 'Test')")
    family_id = cur.lastrowid
    conn.execute("INSERT INTO adults (family_id, name) VALUES (?, 'Test Adult')", (family_id,))
    conn.execute("INSERT INTO kids (family_id, name) VALUES (?, 'Test Kid')", (family_id,))
    conn.commit()
    conn.close()

    rv = client.post('/checkin_last4', data={'last4': '1234'})
    assert b'Test Adult' in rv.data
    assert b'Test Kid' in rv.data

def test_admin_families(client):
    rv = client.get('/admin/families')
    assert b'Families' in rv.data

def test_add_family(client):
    rv = client.post('/admin/families/add', data={
        'phone': '5678',
        'troop': 'Test',
        'adults': ['Adult1', 'Adult2'],
        'kids': ['Kid1']
    }, follow_redirects=True)
    assert b'Family added' in rv.data

    # Check DB
    conn = get_test_db()
    family = conn.execute("SELECT * FROM families WHERE phone = '5678'").fetchone()
    assert family['troop'] == 'Test'
    adults = conn.execute("SELECT name FROM adults WHERE family_id = ?", (family['id'],)).fetchall()
    assert len(adults) == 2
    kids = conn.execute("SELECT name FROM kids WHERE family_id = ?", (family['id'],)).fetchall()
    assert len(kids) == 1
    conn.close()

def test_edit_family(client):
    # Add a family first
    conn = get_test_db()
    cur = conn.execute("INSERT INTO families (phone, troop) VALUES ('9999', 'Old')")
    family_id = cur.lastrowid
    conn.execute("INSERT INTO adults (family_id, name) VALUES (?, 'Old Adult')", (family_id,))
    conn.execute("INSERT INTO kids (family_id, name) VALUES (?, 'Old Kid')", (family_id,))
    conn.commit()
    conn.close()

    # Edit it
    rv = client.post(f'/admin/families/edit/{family_id}', data={
        'phone': '9999',
        'troop': 'New',
        'adults': ['New Adult'],
        'kids': ['New Kid1', 'New Kid2']
    }, follow_redirects=True)
    assert b'Family updated' in rv.data

    # Check DB
    conn = get_test_db()
    family = conn.execute("SELECT * FROM families WHERE id = ?", (family_id,)).fetchone()
    assert family['troop'] == 'New'
    adults = conn.execute("SELECT name FROM adults WHERE family_id = ?", (family_id,)).fetchall()
    assert len(adults) == 1
    assert adults[0]['name'] == 'New Adult'
    kids = conn.execute("SELECT name FROM kids WHERE family_id = ?", (family_id,)).fetchall()
    assert len(kids) == 2
    conn.close()