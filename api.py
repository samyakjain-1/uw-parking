import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from data_manager import DatabaseManager

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
# Enable CORS to allow requests from the React frontend during development
CORS(app)

@app.route('/api/garages', methods=['GET'])
def get_garages():
    """
    API endpoint to fetch all garage data, joined with the latest availability.
    """
    db_manager = DatabaseManager()
    try:
        db_manager.connect()
        with db_manager.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
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
        return jsonify(garages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if db_manager.conn:
            db_manager.close()

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Use Gunicorn for production, but this is fine for local dev
    app.run(use_reloader=True, port=5001, threaded=True)
