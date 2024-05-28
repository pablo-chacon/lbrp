import requests
import pandas as pd
from geopy.distance import geodesic
from dotenv import load_dotenv
import os


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-23

# Load .env vars.
load_dotenv()

# Real-Time Data URLs.
deviations_url = "https://deviations.integration.sl.se/v1/messages"
departures_url_template = "https://transport.integration.sl.se/v1/sites/{site_id}/departures"
stops_url = "https://transport.integration.sl.se/v1/stop-points"


# Make GET requests.
def make_request(url, params=None):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Request URL: {response.url}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}, Status Code: {response.status_code}, Message: {response.text}")
        return None


# Fetch and save stops data.
def fetch_and_save_stops_data():
    stops_data = make_request(stops_url)
    if stops_data:
        stops_df = pd.json_normalize(stops_data)
        stops_df.to_pickle('stops_data.pkl')
        print("Stops data saved successfully.")
    else:
        print("Failed to fetch stops data.")


# Process deviations data.
def save_deviations():
    deviations_data = make_request(deviations_url)
    if deviations_data:
        deviations_df = pd.json_normalize(deviations_data)
        deviations_df.to_pickle('deviations.pkl')
        return deviations_df
    return pd.DataFrame()


# Load stops data from pickle.
def load_stops_data():
    try:
        stops_df = pd.read_pickle('stops_data.pkl')
        print("Stops data loaded successfully.")
        return stops_df
    except Exception as e:
        print(f"Failed to load stops data: {e}")
        return pd.DataFrame()


# Find stops near the user's location.
def find_nearby_stops(stops_df, user_lat, user_lon, max_distance_km=1.0):
    nearby_stops = []
    user_location = (user_lat, user_lon)

    for _, stop in stops_df.iterrows():
        stop_location = (stop['lat'], stop['lon'])
        distance = geodesic(user_location, stop_location).km
        if distance <= max_distance_km:
            nearby_stops.append(stop)

    return nearby_stops


# Convert Stop ID.
def convert_stop_id(stop_id):
    stop_id_str = str(stop_id).zfill(7)
    converted_id = f"{stop_id_str[1]}{stop_id_str[0]}{stop_id_str[2:]}"
    print(f"Converted stop ID from {stop_id} to {converted_id}")  # Debugging statement
    return converted_id


# Fetch departures for a stop.
def fetch_departures(stop_id, time_window=120, transport_mode=None, direction=None, line=None):
    site_id = convert_stop_id(stop_id)
    url = departures_url_template.format(site_id=site_id)
    params = {"forecast": time_window}
    if transport_mode:
        params["transport"] = transport_mode
    if direction:
        params["direction"] = direction
    if line:
        params["line"] = line
    departures_data = make_request(url, params=params)
    if departures_data:
        print(
            f"Departures Data for stop ID {stop_id} (converted to {site_id}): {departures_data}")  # Debugging statement
        return departures_data
    return None


# Test a known stop ID for debugging.
def test_known_stop():
    known_stop_id = '41483'  # Replace with a known working stop ID if available
    departures_data = fetch_departures(known_stop_id, time_window=120, transport_mode="BUS")
    if departures_data:
        departures = departures_data.get('departures', [])
        stop_deviations = departures_data.get('stop_deviations', [])
        print(f"Departures for known stop ID {known_stop_id}: {departures}")
        print(f"Deviations for known stop ID {known_stop_id}: {stop_deviations}")


# Main function to execute the script.
def main():
    # Fetch and save stops data
    fetch_and_save_stops_data()

    # Load stops data
    stops_df = load_stops_data()

    deviations_df = save_deviations()
    user_lat, user_lon = 59.328284, 18.016154  # Example coordinates (replace with user location)
    print(f"Latitude: {user_lat}, Longitude: {user_lon}")  # Debugging statement
    nearby_stops = find_nearby_stops(stops_df, user_lat, user_lon, max_distance_km=1.0)

    print(f"Nearby Stops: {nearby_stops}")  # Debugging statement

    all_departures = []
    for stop in nearby_stops:
        stop_id = stop['id']
        print(f"Processing stop ID: {stop_id}")  # Debugging statement
        if stop_id:
            departures_data = fetch_departures(stop_id, time_window=120,
                                               transport_mode="BUS")  # Adjusted time window and transport mode
            if departures_data:
                departures = departures_data.get('departures', [])
                stop_deviations = departures_data.get('stop_deviations', [])
                all_departures.append(
                    {"stop_id": stop_id, "departures": departures, "stop_deviations": stop_deviations})
                print(f"Departures for stop ID {stop_id}: {departures}")
                print(f"Deviations for stop ID {stop_id}: {stop_deviations}")

    # Test a known stop ID
    test_known_stop()


if __name__ == '__main__':
    main()
