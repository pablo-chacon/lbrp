import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SL_API_KEY')


def get_trip(origin_id, dest_id):
    url = f'https://api.resrobot.se/v2/trip?key={API_KEY}&originId={origin_id}&destId={dest_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def lookup_stop(query):
    url = f'https://api.resrobot.se/v2/location.name?key={API_KEY}&input={query}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_nearby_stops(lat, lon):
    url = f'https://api.resrobot.se/v2/location.nearbystops?key={API_KEY}&originCoordLat={lat}&originCoordLong={lon}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Example usage
stop_name = 'Medborgarplatsen'
stop_data = lookup_stop(stop_name)
print(stop_data)

lat, lon = 59.315196, 18.072867
nearby_stops = get_nearby_stops(lat, lon)
print(nearby_stops)

# Example usage
origin_id = 'origin_stop_id'
dest_id = 'destination_stop_id'
trip_data = get_trip(origin_id, dest_id)
print(trip_data)
