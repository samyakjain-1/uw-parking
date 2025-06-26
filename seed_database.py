import os
import psycopg2
from data_manager import DatabaseManager

# --- Data provided by the user ---
GARAGE_DATA = [
    {
        "name": "020  UNIVERSITY AVE RAMP",
        "address": "1390 University Ave, Madison, WI 53706",
        "latitude": 43.0734493,
        "longitude": -89.4087136
    },
    {
        "name": "027  NANCY NICHOLAS HALL GARAGE",
        "address": "1314 Linden Dr, Madison, WI 53706",
        "latitude": 43.0752143,
        "longitude": -89.4111493
    },
    {
        "name": "036  OBSERVATORY DR RAMP",
        "address": "Steenbock Ramp, 1645 Observatory Dr, Madison, WI 53706",
        "latitude": 43.076516,
        "longitude": -89.4134245
    },
    {
        "name": "067  LINDEN DRIVE RAMP",
        "address": "2002 Linden Dr, Madison, WI 53706",
        "latitude": 43.0755893,
        "longitude": -89.4173042
    },
    {
        "name": "006L HC WHITE GARAGE LOWR",
        "address": "600 N Park St, Madison, WI 53706",
        "latitude": 43.0766852,
        "longitude": -89.4013127
    },
    {
        "name": "006U HC WHITE GARAGE UPPR",
        "address": "600 N Park St, Madison, WI 53706",
        "latitude": 43.0766852,
        "longitude": -89.4013127
    },
    {
        "name": "007  GRAINGER HALL GARAGE",
        "address": "325 N Brooks St, Madison, WI 53715",
        "latitude": 43.072856,
        "longitude": -89.4022902
    },
    {
        "name": "029  N PARK STREET RAMP",
        "address": "21 N Park St, Madison, WI 53715",
        "latitude": 43.068625,
        "longitude": -89.400834
    },
    {
        "name": "046  LAKE & JOHNSON RAMP",
        "address": "301 North Lake Street, Madison, WI 53715",
        "latitude": 43.072142,
        "longitude": -89.397361
    },
    {
        "name": "083  FLUNO CENTER GARAGE",
        "address": "314 N Frances St, Madison, WI 53715",
        "latitude": 43.0727,
        "longitude": -89.395955
    },
    {
        "name": "017 ENGINEERING DR RAMP",
        "address": "1525 Engineering Dr, Madison, WI 53706",
        "latitude": 43.0718182,
        "longitude": -89.4123866
    },
    {
        "name": "080  UNION SOUTH GARAGE",
        "address": "1308 W Dayton St, Madison, WI 53715",
        "latitude": 43.0711743,
        "longitude": -89.4089623
    },
    {
        "name": "063 CHILDRENS HOSP GARAGE",
        "address": "1585 Highland Ave, Madison, WI 53705",
        "latitude": 43.0788761,
        "longitude": -89.4321361
    },
    {
        "name": "076  UNIV BAY DRIVE RAMP",
        "address": "2501 University Bay Dr, Madison, WI 53705",
        "latitude": 43.0813698,
        "longitude": -89.428328
    }
]

def seed_data():
    """Inserts the garage data into the database, ignoring duplicates."""
    db_manager = DatabaseManager()
    db_manager.connect()
    
    print("--- Seeding Database ---")
    with db_manager.conn.cursor() as cursor:
        for garage in GARAGE_DATA:
            # Check if the garage already exists before inserting
            cursor.execute("SELECT name FROM garages WHERE name = %s", (garage['name'],))
            if cursor.fetchone():
                print(f"'{garage['name']}' already exists. Skipping.")
                continue

            try:
                cursor.execute('''
                    INSERT INTO garages (name, address, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                ''', (garage['name'], garage['address'], garage['latitude'], garage['longitude']))
                print(f"Added '{garage['name']}' to the database.")
            except psycopg2.Error as e:
                print(f"Error inserting {garage['name']}: {e}")
                db_manager.conn.rollback()

    db_manager.conn.commit()
    db_manager.close()
    print("\n--- Database Seeding Finished ---")

if __name__ == "__main__":
    # First, ensure the tables exist
    db_manager = DatabaseManager()
    db_manager.setup_tables()
    # Then, seed the data
    seed_data()
