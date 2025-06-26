# UW Madison Live Parking Map

This web application provides a live, interactive map to help users find available parking at the University of Wisconsin-Madison campus. It scrapes real-time parking data, allows users to search for a destination, and displays the nearest available parking garages, sorted by distance.

## Features

- **Live Data Scraping:** A Python script runs continuously to scrape the latest parking availability from the UW Transportation Services website.
- **Interactive Google Map:** Displays garage locations on a clean, easy-to-read map.
- **Destination Search:** Users can type in any destination, and the app will provide autocomplete suggestions using the Google Places API.
- **Smart Filtering & Sorting:** When a destination is selected, the map automatically filters out full garages and sorts the remaining options by proximity.
- **Color-Coded Markers:** Garage pins are color-coded for at-a-glance availability.
- **Smooth UI:** The map pans and zooms smoothly to new locations for a polished user experience.
- **Modular Architecture:** The backend, scraper, and frontend are decoupled, making the application maintainable and scalable.

## Tech Stack

- **Frontend:** React, Google Maps JavaScript API
- **Backend API:** Flask, Gunicorn
- **Database:** PostgreSQL
- **Web Scraping:** Python (`requests`, `BeautifulSoup`)
- **Deployment:** Heroku

---

## Local Development Setup

Follow these steps to get the application running on your local machine.

### 1. Prerequisites
- Python 3 and `pip`
- Node.js and `npm`
- A local PostgreSQL instance

### 2. Setup
1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2.  **Install Python Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```
3.  **Install Frontend Dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```
4.  **Configure Environment Variables:**
    - Create a `.env` file in the root directory.
    - Add your local PostgreSQL database URL and your Google Maps API key:
      ```
      DATABASE_URL=postgresql://user:password@localhost:5432/yourdbname
      REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
      ```
    - **Important:** Also create a `.env` file inside the `frontend` directory containing just the `REACT_APP_GOOGLE_MAPS_API_KEY` for the React build process to use.

### 3. Running Locally
1.  **Seed the Database (run once):**
    ```bash
    python3 seed_database.py
    ```
2.  **Start the Backend API (Terminal 1):**
    ```bash
    python3 api.py
    ```
3.  **Start the Scraper (Terminal 2):**
    ```bash
    python3 scraper.py
    ```
4.  **Start the Frontend (Terminal 3):**
    ```bash
    cd frontend
    npm start
    ```

---

## Heroku Deployment Instructions

Follow these steps to deploy the application to Heroku.

### 1. Prerequisites
- A free [Heroku account](https://signup.heroku.com/).
- The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed on your machine.
- The project pushed to a GitHub repository.

### 2. Deployment Steps

1.  **Log in to Heroku:**
    ```bash
    heroku login
    ```

2.  **Create a New Heroku App:**
    From your Heroku dashboard, click "New" -> "Create new app". Give it a unique name.

3.  **Connect to GitHub:**
    In the "Deploy" tab of your new Heroku app, connect to your GitHub account and link the correct repository.

4.  **Add Buildpacks:**
    In the "Settings" tab, scroll down to the "Buildpacks" section. You need to add two, **in this specific order**:
    1.  `heroku/python`
    2.  `heroku/nodejs`

5.  **Provision PostgreSQL Database:**
    In the "Resources" tab, search for the **"Heroku Postgres"** add-on and provision the free "Hobby Dev" plan. This will automatically create a `DATABASE_URL` config var.

6.  **Set Environment Variables:**
    In the "Settings" tab, click "Reveal Config Vars". Add your Google Maps API key:
    - **KEY:** `REACT_APP_GOOGLE_MAPS_API_KEY`
    - **VALUE:** `your_google_maps_api_key_here`

7.  **Deploy the Application:**
    Go to the "Deploy" tab and trigger a manual deployment of the `main` branch. Heroku will now build both the frontend and backend.

8.  **Seed the Production Database:**
    After the deployment is successful, you need to run the seed script on the Heroku server.
    - In your local terminal, run:
      ```bash
      heroku run python3 seed_database.py --app your-heroku-app-name
      ```
    - This command executes the script on a one-off dyno, populating your live database.

9.  **Scale Your Dynos:**
    By default, only the `web` process runs. You need to enable the `worker` process.
    - In the "Resources" tab, you should see your `web` and `worker` dynos listed (from the `Procfile`).
    - Click the "Edit" icon (pencil) for the `worker` dyno, toggle it on, and click "Confirm".

Your application is now live! You can open it using the "Open app" button in the top-right of your Heroku dashboard.
