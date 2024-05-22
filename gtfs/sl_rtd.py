import requests
import pandas as pd
from dotenv import load_dotenv
import os
import json


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-11

"""Fetch Real-Time Data from SL API. 
    Endpoints: Timetable, Deviations, Nearby Stops.
    Save data to local files.
"""

# Load .env vars.
load_dotenv()

# Retrieve API Key.
API_KEY = os.getenv('SL_API_KEY')

# Real-Time Data URLs.
timetable_url = "https://transport.integration.sl.se/v1/lines"
deviations_url = "https://deviations.integration.sl.se/v1/messages"
nearby_stops_url = "https://journeyplanner.integration.sl.se/v1/nearbystopsv2.json"


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


# Process timetable data.
def process_data(data):
    # List for extracted data.
    extracted_info = []
    # Iterate transport mode.
    for transport_mode, lines in data.items():
        if not isinstance(lines, list):
            print(f"Unexpected data type for lines: {type(lines)}")
            continue
        # Iterate lines in transport mode.
        for line in lines:
            # Extract relevant data.
            info = {
                "transport_mode": transport_mode,
                "line_id": line["id"],
                "line_name": line["name"],
                "designation": line["designation"],
                "group_of_lines": line.get("group_of_lines"),
                "transport_authority_id": line["transport_authority"]["id"],
                "transport_authority_name": line["transport_authority"]["name"],
                "contractor_id": line.get("contractor", {}).get("id"),
                "contractor_name": line.get("contractor", {}).get("name"),
                "valid_from": line["valid"].get("from"),
                "valid_to": line["valid"].get("to")
            }
            # Append data.
            extracted_info.append(info)
    # Create DataFrame.
    df = pd.DataFrame(extracted_info)
    return df


def current_timetable(timetable_df, deviations_df):
    # Explode deviations_df separate rows lines.
    deviations_exploded = deviations_df.explode('scope.lines')
    deviations_exploded = deviations_exploded.reset_index(drop=True)
    deviations_exploded['line_id'] = deviations_exploded['scope.lines'].apply(lambda x: x['id'])

    # Merge dataframes.
    merged_data = pd.merge(timetable_df, deviations_exploded, on='line_id', suffixes=('_timetable', '_deviation'))

    return merged_data


def extract_stop_locations(nearby_stops_data):
    nearby_stops_info = []
    for item in nearby_stops_data['stopLocationOrCoordLocation']:
        stop_location = item['StopLocation']
        nearby_stops_info.append(stop_location)
    nearby_stops_df = pd.DataFrame(nearby_stops_info)
    return nearby_stops_df


def save_timetable():
    timetable_data = make_request(timetable_url, params={"transport_authority_id": 1})
    if timetable_data:
        timetable_df = process_data(timetable_data)
        timetable_df.to_pickle('timetable.pkl')
        print(timetable_df.head())
        return timetable_df
    return pd.DataFrame()


def save_deviations():
    deviations_data = make_request(deviations_url)
    if deviations_data:
        deviations_df = pd.json_normalize(deviations_data)
        deviations_df.to_pickle('deviations.pkl')
        print(deviations_df.head())
        return deviations_df
    return pd.DataFrame()


def save_nearby_stops():
    nearby_stops_data = make_request(nearby_stops_url, params={
        "originCoordLat": 59.328284,
        "originCoordLong": 18.016154,
        "maxNo": 5,
        "r": 200,
        "key": API_KEY
    })
    if nearby_stops_data:
        nearby_stops_df = extract_stop_locations(nearby_stops_data)
        nearby_stops_df.to_pickle('nearby_stops.pkl')
        print(nearby_stops_df.head())
        return nearby_stops_df
    return pd.DataFrame()


def save_all_data():
    timetable_df = save_timetable()
    deviations_df = save_deviations()
    nearby_stops_df = save_nearby_stops()
    return timetable_df, deviations_df, nearby_stops_df


if __name__ == '__main__':
    save_all_data()
