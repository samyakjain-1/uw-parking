import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """
    A modular class to handle all interactions with the PostgreSQL database.
    """
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("No DATABASE_URL set for the database connection.")
        self.conn = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.conn = psycopg2.connect(self.db_url)
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            raise

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
        
        with self.conn.cursor() as cursor:
            # Static garage information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS garages (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    address TEXT,
                    latitude REAL,
                    longitude REAL
                )
            ''')
            # Dynamic availability data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS availability (
                    id SERIAL PRIMARY KEY,
                    garage_name TEXT UNIQUE NOT NULL,
                    vacant_stalls TEXT,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
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
            
        with self.conn.cursor() as cursor:
            # Use ON CONFLICT to perform an "upsert"
            cursor.execute('''
                INSERT INTO availability (garage_name, vacant_stalls, timestamp)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (garage_name) DO UPDATE SET
                    vacant_stalls = EXCLUDED.vacant_stalls,
                    timestamp = CURRENT_TIMESTAMP;
            ''', (garage_name, vacant_stalls))
        self.conn.commit()
