import requests
import pandas as pd

# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-11


"""
SL Real-Time Data API interaction.
Retrieve timetable, deviations, and nearby stops data.
Build response to dataframe and pickle dataframes.
"""

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


def timetable_to_df(timetable):
    df = pd.json_normalize(timetable)
    df.to_pickle('timetable.pkl')
    return df


def get_deviations():
    response = requests.get(deviations_url)
    data = response.json()
    return data


def deviations_to_df(deviations):
    df = pd.json_normalize(deviations)
    df.to_pickle('deviations.pkl')
    return df


def get_nearby_stops(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
    }
    response = requests.get(nearby_stops_url, params=params)
    nearby_stops_data = response.json()
    return nearby_stops_data


def nearby_stops_to_df(nearby_stops_data):
    df = pd.json_normalize(nearby_stops_data)
    df.to_pickle('nearby_stops.pkl')
    return df


if __name__ == '__main__':
    timetable = get_timetable()  # Get timetable data
    timetable_df = timetable_to_df(timetable)  # Timetable to DataFrame.
    deviations = get_deviations()  # Get deviations data
    deviations_df = deviations_to_df(deviations)  # Deviations to DataFrame.
    nearby_stops = get_nearby_stops(59.3293, 18.0686)  # Get nearby stops data.

