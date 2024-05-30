import requests
import pandas as pd
from geopy.distance import geodesic
from dotenv import load_dotenv
import os

# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23

# Load .env vars.
load_dotenv()

# Real-Time Data URLs.
deviations_url = 'https://deviations.integration.sl.se/v1/messages?'
departures_url_template = 'https://transport.integration.sl.se/v1/sites/{site_id}/departures'
sites_url = 'https://transport.integration.sl.se/v1/sites'


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


# Fetch and save sites data.
def fetch_and_save_sites_data():
    sites_data = make_request(sites_url)
    if sites_data:
        sites_df = pd.json_normalize(sites_data)
        sites_df.to_pickle('sites_data.pkl')
        print("Sites data saved successfully.")
    else:
        print("Failed to fetch sites data.")


# Process deviations data.
def save_deviations():
    deviations_data = make_request(deviations_url)
    if deviations_data:
        deviations_df = pd.json_normalize(deviations_data)
        deviations_df.to_pickle('deviations.pkl')
        return deviations_df
    return pd.DataFrame()


# Load sites data.
def load_sites_data():
    try:
        sites_df = pd.read_pickle('sites_data.pkl')
        print("Sites data loaded successfully.")
        return sites_df
    except Exception as e:
        print(f"Failed to load sites data: {e}")
        return pd.DataFrame()


# Find sites near the user's location.
def find_nearby_sites(sites_df, user_lat, user_lon, max_distance_km=1.0):
    nearby_sites = []
    user_location = (user_lat, user_lon)

    # Filter out rows with missing or NaN coordinates
    sites_df = sites_df.dropna(subset=['lat', 'lon'])

    for _, site in sites_df.iterrows():
        site_location = (site['lat'], site['lon'])
        distance = geodesic(user_location, site_location).km
        if distance <= max_distance_km:
            nearby_sites.append(site)

    return nearby_sites


# Fetch departures for a site.
def fetch_departures(site_id, time_window=15, transport_mode=None, direction=None, line=None):
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
        print(f"Departures Data for site ID {site_id}: {departures_data}")  # Debugging statement
        return departures_data.get('departures', [])
    return []


# Test a known site ID for debugging.
def test_known_site():
    known_site_id = '1002'
    departures_data = fetch_departures(known_site_id, time_window=120, transport_mode="BUS")
    if departures_data:
        print(f"Departures for known site ID {known_site_id}: {departures_data}")


# Main function to execute the script.
def main():
    # Fetch and save sites data
    fetch_and_save_sites_data()

    # Load sites data
    sites_df = load_sites_data()
    print(sites_df.head())
    deviations_df = save_deviations()
    user_lat, user_lon = 59.328284, 18.016154  # Example coordinates (replace with user location)
    print(f"Latitude: {user_lat}, Longitude: {user_lon}")  # Debugging statement
    nearby_sites = find_nearby_sites(sites_df, user_lat, user_lon, max_distance_km=1.0)

    print(f"Nearby Sites: {nearby_sites}")  # Debugging statement

    all_departures = []
    for site in nearby_sites:
        site_id = site['id']
        print(f"Processing site ID: {site_id}")  # Debugging statement
        if site_id:
            departures_data = fetch_departures(site_id, time_window=120,
                                               transport_mode="BUS")  # Adjusted time window and transport mode
            if departures_data:
                all_departures.append({"site_id": site_id, "departures": departures_data})
                print(f"Departures for site ID {site_id}: {departures_data}")

    # Test known site ID.
    test_known_site()


if __name__ == '__main__':
    main()
