import requests
import pandas as pd
from dotenv import load_dotenv
import os
import json

# Load .env vars.
load_dotenv()

# Retrieve API Key.
API_KEY = os.getenv('SL_API_KEY')

# Real-Time Data URLs
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


# Process timetable data.
def process_data(data):
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


def main():
    # Get timetable.
    timetable_data = make_request(timetable_url)
    if timetable_data:
        timetable_df = process_data(timetable_data)
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
    nearby_stops_data = {
        'stopLocationOrCoordLocation': [
            {'StopLocation': {
                'id': 'A=1@O=Medborgarplatsen@X=18072867@Y=59315196@u=74@U=74@L=400110130@',
                'extId': '400110130',
                'hasMainMast': True,
                'mainMastId': 'A=1@O=Medborgarplatsen (Stockholm)@X=18073433@Y=59314288@U=74@L=300109191@',
                'mainMastExtId': '300109191',
                'name': 'Medborgarplatsen',
                'lon': 18.072867,
                'lat': 59.315196,
                'weight': 1277,
                'dist': 74,
                'products': 8}},
            {'StopLocation': {
                'id': 'A=1@O=Björns trädgård@X=18072867@Y=59315214@u=76@U=74@L=400110410@',
                'extId': '400110410',
                'hasMainMast': True,
                'mainMastId': 'A=1@O=Björns trädgård (Stockholm)@X=18072912@Y=59315187@U=74@L=300101315@',
                'mainMastExtId': '300101315',
                'name': 'Björns trädgård',
                'lon': 18.072867, 'lat': 59.315214,
                'weight': 13109,
                'dist': 76,
                'products': 10}},
            # Add more stop locations as needed
        ],
        'serverVersion': '1.4',
        'dialectVersion': '1.23',
        'requestId': 'ce8fe1f8a84c75cf0c487b6356f751bb'
    }

    nearby_stops_df = extract_stop_locations(nearby_stops_data)
    # Extract rows where dist is less than 80
    relevant_data = nearby_stops_df[nearby_stops_df['dist'] < 80]
    print(relevant_data.values)
    nearby_stops_df.to_pickle('nearby_stops.pkl')
    print(nearby_stops_df.head())


if __name__ == '__main__':
    main()
