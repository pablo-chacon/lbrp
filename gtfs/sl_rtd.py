import requests
import time
import gtfs_kit as gk
import pandas as pd


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-11


timetable_url = "https://transport.integration.sl.se/v1/lines"
deviations_url = "https://deviations.integration.sl.se/v1/messages"
nearby_stops_url = "https://transport.integration.sl.se/v1/sites?"


def get_timetable():
    payload = {}
    params = {"transport_authority_id": 1}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", timetable_url, headers=headers, params=params, data=payload)
    return response.json()


def get_deviations():
    response = requests.get(deviations_url)
    data = response.json()
    return data


def get_nearby_stops(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
    }
    response = requests.get(nearby_stops_url, params=params)
    nearby_stops_data = response.json()
    return nearby_stops_data


# Sample JSON response for timetables
timetables_json = {
    'from': '2007-08-24T00:00:00'
    # Add more fields as needed
}

# Sample JSON response for deviations
deviations_json = {
    'id': 694,
    'gid': 9011001069400000,
    'name': '',
    # Add more fields as needed
}

if __name__ == "__main__":
    user_lat = 59.3284
    user_lon = 18.0675
    timetable_data = get_timetable()  # Request timetable
    pd.to_pickle(timetable_data, 'data/timetable_data.pkl')  # Save timetable data to file
    get_nearby_stops(user_lat, user_lon)  # Nearby stops

    deviations_data = get_deviations()  # Get deviasions

    # Implement dynamic routing decision
    # Based on user profile data, real-time location, timetable, and deviation information, adjust routing recommendations

    # Verify deviation information and present routing recommendations to the user

    # time.sleep(30)  # Sleep 30 to simulate real-time data
