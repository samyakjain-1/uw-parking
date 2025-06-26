import sqlite3

class DatabaseManager:
    """
    A modular class to handle all interactions with the SQLite database.
    This can be replaced by a different manager (e.g., for Redis) in the future.
    """
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """Establishes a connection to the database."""
        self.conn = sqlite3.connect(self.db_file)

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def setup_tables(self):
        """
        Sets up the necessary tables ('garages' and 'availability')
        if they don't already exist.
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        # Static garage information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS garages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        # Dynamic availability data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garage_name TEXT UNIQUE NOT NULL,
                vacant_stalls TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        print("Database tables are set up.")

    def update_availability(self, garage_name, vacant_stalls):
        """
        Inserts or replaces the availability data for a given garage.
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO availability (garage_name, vacant_stalls, timestamp)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (garage_name, vacant_stalls))
        self.conn.commit()
