import requests
import time

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



user_lat = 59.3284
user_lon = 18.0675

while True:

    timetable_data = get_timetable()  # Request timetable
    print(timetable_data)
    get_nearby_stops(user_lat, user_lon)  # Nearby stops

    deviations_data = get_deviations()  # Get deviasions

    # Implement dynamic routing decision
    # Based on user profile data, real-time location, timetable, and deviation information, adjust routing recommendations


    # Verify deviation information and present routing recommendations to the user


    time.sleep(30)  # Sleep 30 to simulate real-time data
