import sqlite3

# Kreiranje ili povezivanje sa bazom
conn = sqlite3.connect("vozilaDB.db")
cursor = conn.cursor()

# Kreiranje tabele za registarske oznake
cursor.execute('''
CREATE TABLE IF NOT EXISTS registered_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL
)
''')

# Unos primjera podataka (npr. "not_registered" za neregistrovana vozila)
vehicles = [
    ('123A456', 'not_registered'),
    ('MBC123', 'speed_violation'),
    ('NM1234A', 'red_light_cross'),
]

# Ubacivanje podataka
cursor.executemany('INSERT OR IGNORE INTO registered_vehicles (plate, status) VALUES (?, ?)', vehicles)
conn.commit()
conn.close()


