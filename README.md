# UW Madison Live Parking Map

This web application provides a live, interactive map to help users find available parking at the University of Wisconsin-Madison campus. It scrapes real-time parking data, allows users to search for a destination, and displays the nearest available parking garages, sorted by distance.

## Features

- **Live Data Scraping:** A Python script runs continuously to scrape the latest parking availability from the UW Transportation Services website.
- **Interactive Google Map:** Displays garage locations on a clean, easy-to-read map.
- **Destination Search:** Users can type in any destination, and the app will provide autocomplete suggestions using the Google Places API.
- **Smart Filtering & Sorting:** When a destination is selected, the map automatically filters out full garages and sorts the remaining options by proximity.
- **Color-Coded Markers:** Garage pins are color-coded for at-a-glance availability:
    - **Green:** 5+ spaces available
    - **Yellow:** 1-4 spaces available
    - **Red:** Full
- **Detailed Info Windows:** Clicking on a garage pin or list item reveals its name, address, exact availability, and distance from the destination.
- **Smooth UI:** The map pans and zooms smoothly to new locations for a polished user experience.
- **Modular Architecture:** The backend, scraper, and frontend are decoupled, making the application maintainable and scalable.

## Tech Stack

- **Frontend:** React, Google Maps JavaScript API (`@vis.gl/react-google-maps`)
- **Backend API:** Flask
- **Database:** SQLite
- **Web Scraping:** Python (`requests`, `BeautifulSoup`)

## Setup and Installation

Follow these steps to get the application running locally.

### 1. Clone the Repository

```bash
git clone https://github.com/samyakjain-1/uw-parking.git
cd uw-parking/
```

### 2. Set Up the Python Backend

First, install the required Python packages.

```bash
pip3 install -r requirements.txt
```

Next, create the database and populate it with the static garage location data by running the seed script **once**.

```bash
python3 seed_database.py
```

### 3. Set Up the React Frontend

Navigate to the `frontend` directory and install the necessary Node.js packages.

```bash
cd frontend
npm install
```

Next, you need to provide a Google Maps API key. Create a new file named `.env` in the `frontend` directory.

```bash
touch .env
```

Open the `.env` file and add your API key in the following format. **Remember to enable the "Maps JavaScript API" and the "Places API" in your Google Cloud project.**

```
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## Running the Application

To run the full application, you will need to open **three separate terminal windows**.

### Terminal 1: Start the Backend API

This server provides the garage data to the frontend.

```bash
python3 api.py
```

### Terminal 2: Start the Automated Scraper

This script will run in the background, continuously updating the database with live availability data every 60 seconds.

```bash
python3 scraper.py
```

### Terminal 3: Start the Frontend

This will launch the React development server and open the application in your web browser.

```bash
cd frontend
npm start
```

You can now access the live parking map at `http://localhost:3000`.
