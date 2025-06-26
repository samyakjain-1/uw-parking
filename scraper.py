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
URL = "https://transportation.wisc.edu/parking-lots/lot-occupancy-count/"
SCRAPE_INTERVAL = 60 # seconds

# --- Main Scraping Logic ---
def scrape_and_update():
    """
    Scrapes parking availability and updates the JSON data files.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = None
        for t in soup.find_all('table'):
            if "Garage/Ramp" in t.get_text():
                table = t
                break
        
        if not table:
            print("Error: Could not find the parking availability table.")
            return

        rows = table.find('tbody').find_all('tr')
        
        latest_availability = {}
        timestamp = datetime.datetime.now().isoformat()

        print("\n--- Scraping and Updating Availability ---")
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                garage_name = cells[1].get_text(strip=True)
                availability = cells[2].get_text(strip=True)

                # Prepare data for latest availability file
                latest_availability[garage_name] = {
                    "vacant_stalls": availability,
                    "timestamp": timestamp
                }

                # Prepare data for historical log
                log_entry = {
                    "garage_name": garage_name,
                    "vacant_stalls": availability,
                    "timestamp": timestamp
                }
                
                # Append to the historical log file
                with open(HISTORICAL_LOG_FILE, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')

                print(f"Logged availability for '{garage_name}': {availability}")

        # Overwrite the latest availability file with fresh data
        with open(AVAILABILITY_FILE, 'w') as f:
            json.dump(latest_availability, f, indent=2)
        
        print(f"Successfully updated {AVAILABILITY_FILE}.")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving URL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
