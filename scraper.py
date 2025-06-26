import requests
from bs4 import BeautifulSoup
from data_manager import DatabaseManager
import time
import datetime

# --- Configuration ---
DB_FILE = 'parking_data.db'
URL = "https://transportation.wisc.edu/parking-lots/lot-occupancy-count/"
SCRAPE_INTERVAL = 60 # seconds

# --- Main Scraping Logic ---
def scrape_and_update():
    """
    Scrapes parking availability and uses the DatabaseManager to update it.
    """
    db_manager = DatabaseManager(DB_FILE)
    db_manager.connect()

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
        print("\n--- Scraping and Updating Availability ---")

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                garage_name = cells[1].get_text(strip=True)
                availability = cells[2].get_text(strip=True)

                # Use the manager to update the database
                db_manager.update_availability(garage_name, availability)
                print(f"Updated availability for '{garage_name}': {availability}")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving URL: {e}")
    finally:
        db_manager.close()
        print("\n--- Script Finished ---")

if __name__ == "__main__":
    # The scraper will now run in a continuous loop.
    print("Starting the scraper... It will run every 60 seconds.")
    print("Press Ctrl+C to stop.")
    
    while True:
        print(f"\n[{datetime.datetime.now()}] Running scraper...")
        scrape_and_update()
        print(f"Scraping complete. Waiting for {SCRAPE_INTERVAL} seconds...")
        time.sleep(SCRAPE_INTERVAL)
