import requests
import pandas as pd


# __author__ = "pablo-chacon"
# __version__ = "1.0.0"
# __date__ = "2024-05-11"


# SL Real-Time Data URLs
timetable_url = "https://transport.integration.sl.se/v1/lines"
deviations_url = "https://deviations.integration.sl.se/v1/messages"
nearby_stops_url = "https://transport.integration.sl.se/v1/sites?"


# Make GET requests
def make_request(url):
    payload = {}
    params = {"transport_authority_id": 1}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, params=params, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}")
        return None


# Process real-time data
def process_real_time_data():
    # Get timetable data
    timetable_data = make_request(timetable_url)
    if timetable_data:
        timetable_df = pd.json_normalize(timetable_data)
        timetable_df.to_pickle('timetable.pkl')
        print("Timetable data processed and saved.")

    # Get deviations data
    deviations_data = make_request(deviations_url)
    if deviations_data:
        deviations_df = pd.json_normalize(deviations_data)
        deviations_df.to_pickle('deviations.pkl')
        print("Deviations data processed and saved.")

    # Get nearby stops data
    lat, lon = 59.3293, 18.0686  # Stockholm
    nearby_stops_data = make_request(f"{nearby_stops_url}&latitude={lat}&longitude={lon}")
    if nearby_stops_data:
        nearby_stops_df = pd.json_normalize(nearby_stops_data)
        nearby_stops_df.to_pickle('nearby_stops.pkl')
        print("Nearby stops data processed and saved.")


if __name__ == '__main__':
    process_real_time_data()
