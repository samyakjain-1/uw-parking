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
UW_URL = "https://transportation.wisc.edu/parking-lots/lot-occupancy-count/"
CITY_URL = "https://www.cityofmadison.com/parking/data/ramp-availability.json"

app = Flask(__name__)
CORS(app)

# --- Scraping Logic ---

def load_static_garages():
    with open(STATIC_GARAGE_FILE, 'r') as f:
        return json.load(f)

def scrape_city_garages(static_garages):
    try:
        response = requests.get(CITY_URL)
        response.raise_for_status()
        data = response.json()
        city_availability = {}
        dt_object = datetime.datetime.strptime(data['modified'], '%B %d, %Y – %I:%M%p')
        timestamp = dt_object.isoformat()
        city_garage_map = {int(g['id'].split('-')[0]): g['name'] for g in static_garages if g.get('source') == 'City'}
        for lot_id, vacant_stalls in data['vacancies'].items():
            garage_name = city_garage_map.get(int(lot_id))
            if garage_name:
                city_availability[garage_name] = {"vacant_stalls": str(vacant_stalls), "timestamp": timestamp}
        return city_availability
    except Exception as e:
        print(f"Error scraping City garages: {e}")
        return {}

def scrape_uw_garages():
    try:
        response = requests.get(UW_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = next((t for t in soup.find_all('table') if "Garage/Ramp" in t.get_text()), None)
        if not table: return {}
        rows = table.find('tbody').find_all('tr')
        uw_availability = {}
        timestamp = datetime.datetime.now().isoformat()
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                garage_name = cells[1].get_text(strip=True)
                availability = cells[2].get_text(strip=True)
                uw_availability[garage_name] = {"vacant_stalls": availability, "timestamp": timestamp}
        return uw_availability
    except Exception as e:
        print(f"Error scraping UW garages: {e}")
        return {}

def do_scrape():
    """Performs a scrape of all sources and updates the data files."""
    print(f"[{datetime.datetime.now()}] Running scheduled scrape...")
    static_garages = load_static_garages()
    uw_data = scrape_uw_garages()
    city_data = scrape_city_garages(static_garages)
    latest_availability = {**city_data, **uw_data}
    
    with open(HISTORICAL_LOG_FILE, 'a') as f:
        for garage_name, data in latest_availability.items():
            log_entry = {"garage_name": garage_name, "vacant_stalls": data["vacant_stalls"], "timestamp": data["timestamp"]}
            f.write(json.dumps(log_entry) + '\n')

    with open(AVAILABILITY_FILE, 'w') as f:
        json.dump(latest_availability, f, indent=2)
    print(f"Scrape successful: Updated {len(latest_availability)} garages.")

# --- API Endpoints ---

@app.route('/api/garages', methods=['GET'])
def get_garages():
    try:
        if not os.path.exists(STATIC_GARAGE_FILE): return jsonify({"error": "Static garage data not found."}), 500
        with open(STATIC_GARAGE_FILE, 'r') as f:
            garages = json.load(f)
        availability = {}
        if os.path.exists(AVAILABILITY_FILE):
            with open(AVAILABILITY_FILE, 'r') as f:
                availability = json.load(f)
        for garage in garages:
            garage_availability = availability.get(garage['name'])
            garage['vacant_stalls'] = garage_availability.get('vacant_stalls', 'N/A') if garage_availability else 'N/A'
            garage['timestamp'] = garage_availability.get('timestamp', None) if garage_availability else None
        return jsonify(garages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<string:garage_name>', methods=['GET'])
def get_history(garage_name):
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
do_scrape() 
scheduler = BackgroundScheduler()
scheduler.add_job(func=do_scrape, trigger="interval", seconds=60)
scheduler.start()
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    print("Flask server and background scraper are running for local development...")
    app.run(debug=True, port=5001)
