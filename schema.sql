-- schema for troop check-in
CREATE TABLE IF NOT EXISTS families (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    troop TEXT,
    default_adult_id INTEGER,
    authorized_adults TEXT,
    FOREIGN KEY (default_adult_id) REFERENCES adults(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS adults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_hash TEXT,
    name_token_hashes TEXT,
    phone TEXT,
    FOREIGN KEY (family_id) REFERENCES families(id)
);

CREATE TABLE IF NOT EXISTS kids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_hash TEXT,
    name_token_hashes TEXT,
    notes TEXT,
    FOREIGN KEY (family_id) REFERENCES families(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kid_id INTEGER NOT NULL,
    adult_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    checkin_time TEXT NOT NULL,
    checkout_time TEXT,
    checkout_code TEXT,
    FOREIGN KEY (kid_id) REFERENCES kids(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS share_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    family_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    checkin_ids TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    attempt_time TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS login_lockout (
    ip_address TEXT PRIMARY KEY,
    locked_until TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_time ON login_attempts(ip_address, attempt_time);
CREATE INDEX IF NOT EXISTS idx_login_lockout_ip ON login_lockout(ip_address);
);
