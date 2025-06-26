from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

# --- Configuration ---
DB_FILE = 'parking_data.db'

app = Flask(__name__)
# Enable CORS to allow requests from the React frontend
CORS(app)

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

@app.route('/api/garages', methods=['GET'])
def get_garages():
    """
    API endpoint to fetch all garage data, joined with the latest availability.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL query to get all garages and their most recent availability status
        cursor.execute('''
            SELECT
                g.id,
                g.name,
                g.address,
                g.latitude,
                g.longitude,
                a.vacant_stalls,
                a.timestamp
            FROM
                garages g
            LEFT JOIN
                availability a ON g.name = a.garage_name
        ''')
        
        garages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(garages)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Note: For development only. Use a proper WSGI server for production.
    app.run(debug=True, port=5001)
