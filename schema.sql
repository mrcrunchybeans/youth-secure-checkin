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
    FOREIGN KEY (family_id) REFERENCES families(id)
);

CREATE TABLE IF NOT EXISTS kids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name TEXT NOT NULL,
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
    FOREIGN KEY (kid_id) REFERENCES kids(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
