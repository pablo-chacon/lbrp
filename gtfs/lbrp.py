import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
from dotenv import load_dotenv
import os
from geopy.distance import geodesic
import sl_rtd as sl
import logging
import pickle
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load .env vars
load_dotenv()

# Load stops data
def load_stops_data():
    return sl.load_stops_data()

# Find the three closest stops within 1 km
def find_nearby_stops(lat, lon, stops_data, radius=1000, n=3):
    user_location = (lat, lon)
    stops_data['distance'] = stops_data.apply(lambda row: geodesic(user_location, (row['lat'], row['lon'])).meters, axis=1)
    nearby_stops = stops_data[stops_data['distance'] <= radius]
    closest_stops = nearby_stops.nsmallest(n, 'distance')
    return closest_stops

# Fetch real-time departure information
def fetch_departures(stop_id, destination_coords, time_window=60, transport_mode='BUS'):
    try:
        departures = sl.fetch_departures(stop_id, time_window, transport_mode)
        if departures and 'departures' in departures:
            logging.info(f"Fetched departures for stop ID {stop_id}: {departures['departures']}")
            print(f"Destination Coordinates: {destination_coords}")
            filtered_departures = []
            for dep in departures['departures']:
                stop_area = dep.get('stop_area', {})
                dep_coords = (stop_area.get('lat'), stop_area.get('lon'))
                print(f"Checking departure: {dep}")
                if dep_coords in destination_coords:
                    filtered_departures.append(dep)
            logging.info(f"Filtered departures for stop ID {stop_id}: {filtered_departures}")
            return filtered_departures
    except Exception as e:
        logging.error(f"Error fetching departures for stop ID {stop_id}: {e}")
    return []

# Estimate travel time for walking, biking, or driving
def estimate_travel_time(distance, transport_mode):
    if transport_mode == 'walk':
        speed_kmh = 5  # Average walking speed
    elif transport_mode == 'bike':
        speed_kmh = 15  # Average biking speed
    elif transport_mode == 'car':
        speed_kmh = 50  # Average city driving speed
    else:
        return "N/A"
    travel_time_hours = distance / 1000 / speed_kmh
    travel_time_minutes = travel_time_hours * 60
    return timedelta(minutes=travel_time_minutes)

# Optimize route
def optimize_route(gdf, stops_data, destination_coords, step=15):
    route = []
    for i in range(0, len(gdf), step):
        waypoint = gdf.iloc[i]
        closest_stops = find_nearby_stops(waypoint['Latitude'], waypoint['Longitude'], stops_data)
        logging.info(f"Closest stops for waypoint {i} ({waypoint['Latitude']}, {waypoint['Longitude']}): {closest_stops}")
        if not closest_stops.empty:
            for _, stop in closest_stops.iterrows():
                departures = fetch_departures(stop['id'], destination_coords)
                if departures:  # Only add entries with departures
                    logging.info(f"Found departures for stop ID {stop['id']} at waypoint {i}")
                    for dep in departures:
                        route.append({
                            "waypoint_lat": waypoint['Latitude'],
                            "waypoint_lon": waypoint['Longitude'],
                            "waypoint_time": waypoint['Time'],
                            "stop_id": stop['id'],
                            "stop_name": stop['name'],
                            "stop_lat": stop['lat'],
                            "stop_lon": stop['lon'],
                            "destination": dep['destination'],
                            "direction": dep['direction'],
                            "state": dep['state'],
                            "scheduled": dep['scheduled'],
                            "expected": dep['expected'],
                            "line_id": dep['line']['id'],
                            "line_designation": dep['line']['designation'],
                            "transport_mode": dep['line']['transport_mode']
                        })
        else:
            # Handle case with no nearby stops
            logging.info(f"No nearby stops found for waypoint {i} ({waypoint['Latitude']}, {waypoint['Longitude']})")
            for dest_lat, dest_lon in destination_coords:
                distance = geodesic((waypoint['Latitude'], waypoint['Longitude']), (dest_lat, dest_lon)).meters
                for mode in ['walk', 'bike', 'car']:
                    eta = estimate_travel_time(distance, mode)
                    route.append({
                        "waypoint_lat": waypoint['Latitude'],
                        "waypoint_lon": waypoint['Longitude'],
                        "waypoint_time": waypoint['Time'],
                        "stop_id": "N/A",
                        "stop_name": "N/A",
                        "stop_lat": dest_lat,
                        "stop_lon": dest_lon,
                        "destination": f"{mode.capitalize()} to destination",
                        "direction": "N/A",
                        "state": "N/A",
                        "scheduled": "N/A",
                        "expected": (datetime.strptime(waypoint['Time'], "%Y-%m-%d %H:%M:%S") + eta).strftime("%Y-%m-%d %H:%M:%S") if eta != "N/A" else "N/A",
                        "line_id": "N/A",
                        "line_designation": mode.capitalize(),
                        "transport_mode": mode
                    })
    logging.info(f"Route generated with {len(route)} entries.")
    return route

# Main function to integrate all steps
def main():
    logging.info("Loading user trajectory data")
    gdf = pd.read_pickle('gdf.pkl')
    dest = pd.read_pickle('dest.pkl')

    logging.info("Extracting destination coordinates from dest.pkl")
    destination_coords = [(row['Latitude'], row['Longitude']) for _, row in dest.iterrows() if row['is_destination']]

    logging.info(f"Destination coordinates: {destination_coords}")

    logging.info("Loading stops data")
    stops_data = load_stops_data()

    logging.info("Optimizing route")
    optimized_route = optimize_route(gdf, stops_data, destination_coords)

    logging.info(f"Optimized route: {optimized_route}")

    logging.info("Pickling optimized route")
    with open('optimized_route.pkl', 'wb') as f:
        pickle.dump(optimized_route, f)

    logging.info("Displaying optimized route")
    for entry in optimized_route:
        print(f"Waypoint (Lat: {entry['waypoint_lat']}, Lon: {entry['waypoint_lon']}, Time: {entry['waypoint_time']})")
        print(f"Stop (ID: {entry['stop_id']}, Name: {entry['stop_name']}, Lat: {entry['stop_lat']}, Lon: {entry['stop_lon']})")
        print("Departures:")
        print(entry['destination'], entry['direction'], entry['state'], entry['scheduled'], entry['expected'])
        print("\n")

if __name__ == '__main__':
    main()
