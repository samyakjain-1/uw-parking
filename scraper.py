import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

# --- Configuration ---
STATIC_GARAGE_FILE = 'garages.json'
AVAILABILITY_FILE = 'availability.json'
HISTORICAL_LOG_FILE = 'historical_log.jsonl'
UW_URL = "https://transportation.wisc.edu/parking-lots/lot-occupancy-count/"
CITY_URL = "https://www.cityofmadison.com/parking/data/ramp-availability.json"
SCRAPE_INTERVAL = 60 # seconds

# --- Helper to load static garage data ---
def load_static_garages():
    with open(STATIC_GARAGE_FILE, 'r') as f:
        return json.load(f)

# --- City of Madison Scraping Logic ---
def scrape_city_garages(static_garages):
    """Scrapes City of Madison garage availability from their JSON feed."""
    print("--- Scraping City of Madison Garages ---")
    try:
        response = requests.get(CITY_URL)
        response.raise_for_status()
        data = response.json()
        
        city_availability = {}
        
        # Correctly parse the custom timestamp from the City's JSON feed
        modified_str = data['modified']
        # The format is like "June 29, 2025 – 2:42pm"
        dt_object = datetime.datetime.strptime(modified_str, '%B %d, %Y – %I:%M%p')
        timestamp = dt_object.isoformat()

        # Create a mapping from lot_number to garage name
        city_garage_map = {int(g['id'].split('-')[0]): g['name'] for g in static_garages if g.get('source') == 'City'}

        for lot_id, vacant_stalls in data['vacancies'].items():
            garage_name = city_garage_map.get(int(lot_id))
            if garage_name:
                city_availability[garage_name] = {
                    "vacant_stalls": str(vacant_stalls),
                    "timestamp": timestamp
                }
                print(f"Logged City availability for '{garage_name}': {vacant_stalls}")
            else:
                print(f"Warning: No matching garage found for city lot ID {lot_id}")
        
        return city_availability
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving City of Madison URL: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while scraping City garages: {e}")
        return {}

# --- UW Scraping Logic ---
def scrape_uw_garages():
    """Scrapes UW garage availability."""
    print("--- Scraping UW Garages ---")
    try:
        response = requests.get(UW_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = next((t for t in soup.find_all('table') if "Garage/Ramp" in t.get_text()), None)
        
        if not table:
            print("Error: Could not find the UW parking availability table.")
            return {}

        rows = table.find('tbody').find_all('tr')
        uw_availability = {}
        timestamp = datetime.datetime.now().isoformat()

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                garage_name = cells[1].get_text(strip=True)
                availability = cells[2].get_text(strip=True)
                uw_availability[garage_name] = {
                    "vacant_stalls": availability,
                    "timestamp": timestamp
                }
                print(f"Logged UW availability for '{garage_name}': {availability}")
        
        return uw_availability

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving UW URL: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while scraping UW garages: {e}")
        return {}

# --- Main Scraping Logic ---
def scrape_and_update():
    """
    Scrapes parking availability from all sources and updates the JSON data files.
    """
    static_garages = load_static_garages()
    
    print("\n--- Scraping and Updating Availability ---")
    uw_data = scrape_uw_garages()
    city_data = scrape_city_garages(static_garages)

    # Merge data, giving preference to UW data in case of name conflicts
    latest_availability = {**city_data, **uw_data}

    # Write historical log
    with open(HISTORICAL_LOG_FILE, 'a') as f:
        for garage_name, data in latest_availability.items():
            log_entry = {
                "garage_name": garage_name,
                "vacant_stalls": data["vacant_stalls"],
                "timestamp": data["timestamp"]
            }
            f.write(json.dumps(log_entry) + '\n')

    # Overwrite the latest availability file with fresh data
    with open(AVAILABILITY_FILE, 'w') as f:
        json.dump(latest_availability, f, indent=2)
    
    print(f"Successfully updated {AVAILABILITY_FILE} with data from all sources.")

if __name__ == "__main__":
    # Ensure the static garage file exists before starting
    if not os.path.exists(STATIC_GARAGE_FILE):
        print(f"Error: {STATIC_GARAGE_FILE} not found.")
        print("Please run `python3 seed_database.py` first to generate it.")
        exit(1)

    print("Starting the scraper... It will run every 60 seconds.")
    print("Press Ctrl+C to stop.")
    
    while True:
        print(f"\n[{datetime.datetime.now()}] Running scraper...")
        scrape_and_update()
        print(f"Scraping complete. Waiting for {SCRAPE_INTERVAL} seconds...")
        time.sleep(SCRAPE_INTERVAL)
