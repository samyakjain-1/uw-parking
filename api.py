from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import requests
from bs4 import BeautifulSoup
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration ---
STATIC_GARAGE_FILE = 'garages.json'
AVAILABILITY_FILE = 'availability.json'
HISTORICAL_LOG_FILE = 'historical_log.jsonl'
SCRAPE_URL = "https://transportation.wisc.edu/parking-lots/lot-occupancy-count/"

app = Flask(__name__)
CORS(app)

# --- Scraping Logic ---
def do_scrape():
    """
    Performs a scrape of the UW website and updates the data files.
    This function is now designed to be run by the scheduler.
    """
    print(f"[{datetime.datetime.now()}] Running scheduled scrape...")
    try:
        response = requests.get(SCRAPE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = next((t for t in soup.find_all('table') if "Garage/Ramp" in t.get_text()), None)
        if not table:
            print("Scrape failed: Could not find the parking availability table.")
            return

        rows = table.find('tbody').find_all('tr')
        latest_availability = {}
        timestamp = datetime.datetime.now().isoformat()

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                garage_name = cells[1].get_text(strip=True)
                availability = cells[2].get_text(strip=True)
                
                latest_availability[garage_name] = {"vacant_stalls": availability, "timestamp": timestamp}
                log_entry = {"garage_name": garage_name, "vacant_stalls": availability, "timestamp": timestamp}
                
                with open(HISTORICAL_LOG_FILE, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')

        with open(AVAILABILITY_FILE, 'w') as f:
            json.dump(latest_availability, f, indent=2)
            
        print(f"Scrape successful: Updated {len(latest_availability)} garages.")

    except requests.exceptions.RequestException as e:
        print(f"Scrape failed: Error retrieving URL: {e}")
    except Exception as e:
        print(f"Scrape failed: An unexpected error occurred: {e}")

# --- API Endpoints ---

@app.route('/api/garages', methods=['GET'])
def get_garages():
    """
    API endpoint to fetch garage data by combining the static and live JSON files.
    """
    try:
        if not os.path.exists(STATIC_GARAGE_FILE):
            return jsonify({"error": "Static garage data not found."}), 500
        with open(STATIC_GARAGE_FILE, 'r') as f:
            garages = json.load(f)

        if os.path.exists(AVAILABILITY_FILE):
            with open(AVAILABILITY_FILE, 'r') as f:
                availability = json.load(f)
        else:
            availability = {}

        for garage in garages:
            garage_availability = availability.get(garage['name'])
            garage['vacant_stalls'] = garage_availability.get('vacant_stalls', 'N/A') if garage_availability else 'N/A'
            garage['timestamp'] = garage_availability.get('timestamp', None) if garage_availability else None
        
        return jsonify(garages)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<string:garage_name>', methods=['GET'])
def get_history(garage_name):
    """
    API endpoint to fetch historical availability data from the JSONL file.
    """
    try:
        history = []
        if os.path.exists(HISTORICAL_LOG_FILE):
            with open(HISTORICAL_LOG_FILE, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('garage_name') == garage_name:
                        history.append(record)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Scheduler Setup ---
# This code now runs when Gunicorn imports the file, ensuring the job starts in production.
# Run a scrape immediately on startup
do_scrape() 
# Then schedule it to run every 60 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=do_scrape, trigger="interval", seconds=60)
scheduler.start()

# To shut down the scheduler when the app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # This block is now only for local development
    print("Flask server and background scraper are running for local development...")
    app.run(debug=True, port=5001)
