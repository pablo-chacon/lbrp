import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
API_KEY = os.getenv('SL_API_KEY')

# SL Real-Time Data URLs
timetable_url = "https://transport.integration.sl.se/v1/lines"
deviations_url = "https://deviations.integration.sl.se/v1/messages"
nearby_stops_url = "https://journeyplanner.integration.sl.se/v1/nearbystopsv2.json?"

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
        return response.json()

def current_timetable(timetable_df, deviations_df):
    # Explode deviations_df separate rows lines.
    deviations_exploded = deviations_df.explode('scope.lines')
    deviations_exploded = deviations_exploded.reset_index(drop=True)
    deviations_exploded['line_id'] = deviations_exploded['scope.lines'].apply(lambda x: x['id'])

    # Merge dataframes.
    merged_data = pd.merge(timetable_df, deviations_exploded, on='line_id', suffixes=('_timetable', '_deviation'))

    return merged_data

# Process timetable data.
def process__data(data):
    # List extracted data.
    extracted_info = []
    # Iterate transport mode.
    for transport_mode, lines in data.items():
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

if __name__ == '__main__':
    # Get timetable.
    timetable_data = make_request(timetable_url)
    if timetable_data:
        timetable_df = process__data(timetable_data)
        timetable_df.to_pickle('timetable.pkl')
        print(timetable_df.head())

    # Get deviations.
    deviations_data = make_request(deviations_url)
    if deviations_data:
        deviations_df = pd.json_normalize(deviations_data)
        deviations_df.to_pickle('deviations.pkl')

    merged_timetable = current_timetable(timetable_df, deviations_df)
    print(merged_timetable.head())

    # Get nearby stops data
    lat, lon = 59.314722, 18.071944  # Medborgarplatsen coordinates.
    nearby_stops_data = make_request(f"{nearby_stops_url}&originCoordLong={lon}&originCoordLat={lat}&key={API_KEY}")
    if nearby_stops_data:
        nearby_stops_df = pd.json_normalize(nearby_stops_data)
        nearby_stops_df.to_pickle('nearby_stops.pkl')
        print(nearby_stops_df.head())
