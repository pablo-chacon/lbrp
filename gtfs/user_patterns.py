import pandas as pd
import geopandas as gpd
import folium
import pickle
from folium.plugins import PolyLineOffset
import logging

# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load data
with open('generalized_optimized_timetable.pkl', 'rb') as f:
    generalized_optimized_timetable = pickle.load(f)

with open('all_user_data.pkl', 'rb') as f:
    all_user_data = pickle.load(f)

with open('optimized_route.pkl', 'rb') as f:
    optimized_route = pickle.load(f)

# Ensure optimized_route is a DataFrame
optimized_route_df = pd.DataFrame(optimized_route)


def plot_all_user_data(map_obj, data):
    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=3,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=f"User: {row['user_id']}\nTime: {row['Time']}"
        ).add_to(map_obj)


def plot_optimized_route(map_obj, data):
    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['waypoint_lat'], row['waypoint_lon']],
            radius=3,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.6,
            popup=f"Route: {row['line_designation']}"
        ).add_to(map_obj)


def plot_generalized_timetable(map_obj, data):
    for _, row in data.iterrows():
        folium.PolyLine(
            locations=[[row['site_lat_dest'], row['site_lon_dest']], [row['site_lat_dest'], row['site_lon_dest']]],
            color='green',
            weight=2,
            opacity=0.6,
            popup=f"Route ID: {row['line_id']}\nSite: {row['site_id']}\nDestination: {row['destination']}"
        ).add_to(map_obj)


def main():
    logging.info("Generalized optimized timetable columns: %s", generalized_optimized_timetable.columns)
    logging.info("All user data columns: %s", all_user_data.columns)
    logging.info("Optimized route columns: %s", optimized_route_df.columns)

    if 'destination_lat' not in optimized_route_df.columns or 'destination_lon' not in optimized_route_df.columns:
        optimized_route_df['destination_lat'] = optimized_route_df['site_lat']
        optimized_route_df['destination_lon'] = optimized_route_df['site_lon']

    # Initialize the map centered around an average location
    map_center = [all_user_data['Latitude'].mean(), all_user_data['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=10)

    # Plot data
    plot_all_user_data(m, all_user_data)
    plot_optimized_route(m, optimized_route_df)
    plot_generalized_timetable(m, generalized_optimized_timetable)

    # Save the map
    map_file = 'user_patterns_map.html'
    m.save(map_file)
    logging.info("Map has been saved as %s", map_file)


if __name__ == '__main__':
    main()
