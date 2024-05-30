import folium
import pandas as pd

# Load data
regenerated_48_hour_data = pd.read_pickle('regenerated_48_hour_data.pkl')
all_user_data = pd.read_pickle('all_user_data.pkl')
optimized_route_df = pd.read_pickle('optimized_route.pkl')
optimized_route_df = pd.DataFrame(optimized_route_df)  # Ensure it's a DataFrame
generalized_optimized_timetable = pd.read_pickle('generalized_optimized_timetable.pkl')

# Ensure waypoint columns are present in generalized_optimized_timetable
if 'waypoint_lat' not in generalized_optimized_timetable.columns or 'waypoint_lon' not in generalized_optimized_timetable.columns:
    generalized_optimized_timetable = pd.merge(generalized_optimized_timetable,
                                               optimized_route_df[['site_id', 'waypoint_lat', 'waypoint_lon']],
                                               on='site_id', how='left')


# Function to plot 48-hour data
def plot_48_hour_data(m, data):
    for user_id, user_data in data.groupby('user_id'):
        folium.PolyLine(user_data[['Latitude', 'Longitude']].values, color='purple', weight=2.5, opacity=0.8).add_to(m)
        for _, row in user_data.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                color='purple',
                fill=True,
                fill_color='purple',
                fill_opacity=0.6
            ).add_to(m)


# Function to plot all user data
def plot_all_user_data(m, data):
    for user_id, user_data in data.groupby('user_id'):
        folium.PolyLine(user_data[['Latitude', 'Longitude']].values, color='blue', weight=2.5, opacity=0.8).add_to(m)
        for _, row in user_data.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=3,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6
            ).add_to(m)


# Function to plot optimized route
def plot_optimized_route(m, data):
    if 'site_lat' not in data.columns or 'site_lon' not in data.columns:
        print("Optimized route data does not contain 'site_lat' or 'site_lon' columns.")
        return
    for _, row in data.iterrows():
        folium.Marker(
            location=[row['site_lat'], row['site_lon']],
            popup=f"Route: {row['line_id']}<br>Stop: {row['site_name']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        folium.PolyLine(
            locations=[[row['site_lat'], row['site_lon']], [row['waypoint_lat'], row['waypoint_lon']]],
            color='red', weight=2, opacity=0.7
        ).add_to(m)


# Function to plot generalized timetable
def plot_generalized_timetable(m, data):
    if 'site_lat_dest' not in data.columns or 'site_lon_dest' not in data.columns:
        print("Generalized optimized timetable data does not contain 'site_lat_dest' or 'site_lon_dest' columns.")
        return
    if 'waypoint_lat' not in data.columns or 'waypoint_lon' not in data.columns:
        print("Generalized optimized timetable data does not contain 'waypoint_lat' or 'waypoint_lon' columns.")
        return
    for _, row in data.iterrows():
        folium.Marker(
            location=[row['site_lat_dest'], row['site_lon_dest']],
            popup=f"Route: {row['line_id']}<br>Destination: {row['destination']}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        folium.PolyLine(
            locations=[[row['site_lat_dest'], row['site_lon_dest']], [row['waypoint_lat'], row['waypoint_lon']]],
            color='orange', weight=2, opacity=0.7, dash_array='5,10'
        ).add_to(m)


# Define map center
map_center = [all_user_data['Latitude'].mean(), all_user_data['Longitude'].mean()]

# Create the map
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

# Plot data
plot_48_hour_data(m, regenerated_48_hour_data)
plot_all_user_data(m, all_user_data)
plot_optimized_route(m, optimized_route_df)
plot_generalized_timetable(m, generalized_optimized_timetable)

# Save the map
m.save('simulated_trajectory_map.html')
