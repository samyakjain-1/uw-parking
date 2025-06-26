import json

# --- Configuration ---
OUTPUT_FILE = 'garages.json'

# --- Data provided by the user ---
GARAGE_DATA = [
    {
        "name": "020  UNIVERSITY AVE RAMP", "lot_number": 20,
        "address": "1390 University Ave, Madison, WI 53706", "latitude": 43.0734493, "longitude": -89.4087136
    },
    {
        "name": "027  NANCY NICHOLAS HALL GARAGE", "lot_number": 27,
        "address": "1314 Linden Dr, Madison, WI 53706", "latitude": 43.0752143, "longitude": -89.4111493
    },
    {
        "name": "036  OBSERVATORY DR RAMP", "lot_number": 36,
        "address": "Steenbock Ramp, 1645 Observatory Dr, Madison, WI 53706", "latitude": 43.076516, "longitude": -89.4134245
    },
    {
        "name": "067  LINDEN DRIVE RAMP", "lot_number": 67,
        "address": "2002 Linden Dr, Madison, WI 53706", "latitude": 43.0755893, "longitude": -89.4173042
    },
    {
        "name": "006L HC WHITE GARAGE LOWR", "lot_number": 6,
        "address": "600 N Park St, Madison, WI 53706", "latitude": 43.0766852, "longitude": -89.4013127
    },
    {
        "name": "006U HC WHITE GARAGE UPPR", "lot_number": 6,
        "address": "600 N Park St, Madison, WI 53706", "latitude": 43.0766852, "longitude": -89.4013127
    },
    {
        "name": "007  GRAINGER HALL GARAGE", "lot_number": 7,
        "address": "325 N Brooks St, Madison, WI 53715", "latitude": 43.072856, "longitude": -89.4022902
    },
    {
        "name": "029  N PARK STREET RAMP", "lot_number": 29,
        "address": "21 N Park St, Madison, WI 53715", "latitude": 43.068625, "longitude": -89.400834
    },
    {
        "name": "046  LAKE & JOHNSON RAMP", "lot_number": 46,
        "address": "301 North Lake Street, Madison, WI 53715", "latitude": 43.072142, "longitude": -89.397361
    },
    {
        "name": "083  FLUNO CENTER GARAGE", "lot_number": 83,
        "address": "314 N Frances St, Madison, WI 53715", "latitude": 43.0727, "longitude": -89.395955
    },
    {
        "name": "017 ENGINEERING DR RAMP", "lot_number": 17,
        "address": "1525 Engineering Dr, Madison, WI 53706", "latitude": 43.0718182, "longitude": -89.4123866
    },
    {
        "name": "080  UNION SOUTH GARAGE", "lot_number": 80,
        "address": "1308 W Dayton St, Madison, WI 53715", "latitude": 43.0711743, "longitude": -89.4089623
    },
    {
        "name": "063 CHILDRENS HOSP GARAGE", "lot_number": 63,
        "address": "1585 Highland Ave, Madison, WI 53705", "latitude": 43.0788761, "longitude": -89.4321361
    },
    {
        "name": "076  UNIV BAY DRIVE RAMP", "lot_number": 76,
        "address": "2501 University Bay Dr, Madison, WI 53705", "latitude": 43.0813698, "longitude": -89.428328
    }
]

RATE_SCHEDULES = {
    "group1": {
        "lots": [17, 20, 36, 76],
        "daytime_rate": "Daytime (Mon–Fri, 7am–4:30pm): $1/30min (first 3 hrs), then $1/hr. $15 max.",
        "evening_rate": "Evening (Mon–Fri, 4:30pm–12am): $1/hr. $5 max.",
        "notes": "Free 12am-7am Mon-Fri & all day Sat/Sun."
    },
    "group2": {
        "lots": [7],
        "daytime_rate": "Daytime (Mon–Sat, 7am–4:30pm): $1/30min (first 3 hrs), then $1/hr. $15 max.",
        "evening_rate": "Evening (Mon–Sat, 4:30pm–12am): $1/hr. $5 max.",
        "notes": "Free 12am-7am Mon-Sat & all day Sun."
    },
    "group3": {
        "lots": [6, 27, 29, 46, 67, 80, 83],
        "daytime_rate": "Daytime (7am–4:30pm): $1/30min (first 3 hrs), then $1/hr. $15 max.",
        "evening_rate": "Evening (4:30pm–12am): $1/hr. $5 max.",
        "notes": "Free 12am-7am daily."
    },
    "group4": {
        "lots": [63, 75],
        "daytime_rate": "Daytime (7am–12am): $1/30min (first 3 hrs), then $1/hr. $15 max.",
        "evening_rate": "Overnight (12am–7am): $1/hr. $5 max.",
        "notes": "Enforced at all times."
    }
}

def generate_static_data():
    """Generates a single JSON file with all static garage data."""
    
    print("--- Generating static garages.json file ---")
    
    processed_garages = {}
    
    for garage in GARAGE_DATA:
        # Avoid duplicating entries for lots like 006L and 006U
        if garage['name'] in processed_garages:
            continue

        schedule = next((s for s in RATE_SCHEDULES.values() if garage["lot_number"] in s["lots"]), None)
        
        if not schedule:
            print(f"Warning: No rate schedule found for lot {garage['lot_number']} ({garage['name']}).")
            continue

        processed_garages[garage['name']] = {
            "id": garage['lot_number'], # Use lot number as a unique ID
            "name": garage['name'],
            "address": garage['address'],
            "latitude": garage['latitude'],
            "longitude": garage['longitude'],
            "daytime_rate": schedule['daytime_rate'],
            "evening_rate": schedule['evening_rate'],
            "notes": schedule['notes']
        }

    # Convert the dictionary to a list for the final JSON array
    final_garage_list = list(processed_garages.values())

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_garage_list, f, indent=2)
        
    print(f"Successfully created {OUTPUT_FILE} with {len(final_garage_list)} garages.")

if __name__ == "__main__":
    generate_static_data()
