import sqlite3
import datetime
import threading

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._local = threading.local()
        self.setup()

    @property
    def cursor(self):
        if not hasattr(self._local, 'cursor'):
            self._local.cursor = self.conn.cursor()
        return self._local.cursor

    def setup(self):
        # Create tables if they don't exist
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password TEXT,
                is_staff BOOLEAN DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT UNIQUE,
                origin TEXT,
                destination TEXT,
                departure_time DATETIME,
                arrival_time DATETIME,
                price REAL,
                seats_available INTEGER,
                category TEXT DEFAULT 'Domestic'
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                flight_id INTEGER,
                booking_date DATETIME,
                status TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(flight_id) REFERENCES flights(id)
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER,
                amount REAL,
                method TEXT,
                transaction_id TEXT UNIQUE,
                status TEXT,
                FOREIGN KEY(booking_id) REFERENCES bookings(id)
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                subject TEXT,
                message TEXT,
                created_at DATETIME
            );
        ''')
        self.conn.commit()

db = Database()
