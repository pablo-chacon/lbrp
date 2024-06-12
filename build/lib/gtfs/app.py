import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import logging
from datetime import datetime

import gtfs.user_patterns as up
import gtfs.sl_rtd as sl
import gtfs.trajectory_map as tm
import gtfs.user_trajectories as ut
import gtfs.lbrp as lbrp

# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23

# Set up logging.
logging.basicConfig(level=logging.INFO)


# Run scripts, generate data.
def run_scripts():
    ut.user_trajectory()  # Generate user trajectories first
    lbrp.lbrp()  # Then generate the optimized route
    up.user_patterns()  # Generate user patterns
    sl.rtd()  # Load real-time data
    tm.create_trajectory_map()  # Create trajectory map


# Load data functions
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_pickle(file_path)
        if isinstance(data, list):  # Check if data is a list
            data = pd.DataFrame(data)
        return data
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None


# Calculate total transit time
def calculate_total_transit_time(data, time_column='waypoint_time'):
    if time_column in data.columns:
        start_time = pd.to_datetime(data[time_column].min())
        end_time = pd.to_datetime(data[time_column].max())
        total_time = end_time - start_time
        return total_time
    return None


# Create folium map from DataFrame.
def create_folium_map(data, title, color='blue'):
    if 'Latitude' in data.columns and 'Longitude' in data.columns:
        m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=15)
        for _, row in data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['user_id']}<br>Time: {row['Time']}",
                icon=folium.Icon(color=color)
            ).add_to(m)
    elif 'lat' in data.columns and 'lon' in data.columns:
        # Filter out rows with NaN values in 'lat' or 'lon'
        data = data.dropna(subset=['lat', 'lon'])
        m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=15)
        for _, row in data.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"{row['name']}<br>Note: {row['note']}",
                icon=folium.Icon(color=color)
            ).add_to(m)
    elif 'waypoint_lat' in data.columns and 'waypoint_lon' in data.columns:
        m = folium.Map(location=[data['waypoint_lat'].mean(), data['waypoint_lon'].mean()], zoom_start=15)
        for _, row in data.iterrows():
            folium.Marker(
                location=[row['waypoint_lat'], row['waypoint_lon']],
                popup=f"{row['site_name']}<br>Time: {row['waypoint_time']}",
                icon=folium.Icon(color=color)
            ).add_to(m)
    else:
        st.error(
            f"Data for {title} does not contain 'Latitude'/'Longitude', 'lat'/'lon', or 'waypoint_lat'/'waypoint_lon' columns."
        )
        return None
    folium.LayerControl().add_to(m)
    return m


# Display folium map from HTML.
def display_map(html_file_path):
    with open(html_file_path, 'r') as file:
        map_html = file.read()
    return st.components.v1.html(map_html, height=600)


# Generate data
run_scripts()

# Streamlit UI
st.title("User Trajectories and Optimization Visualization")

tab1, tab2, tab3, tab4 = st.tabs(["User Trajectories", "Real-Time Data", "Optimization Comparison", "User Patterns"])

with tab1:
    all_user_data = load_data("gtfs/all_user_data.pkl")
    st.header("User Trajectories")
    st.write(all_user_data.head())
    st.header("Trajectory Map")
    display_map("gtfs/user_trajectories_map.html")

with tab2:
    st.header("Real-Time Data")
    sites_data = load_data("gtfs/sites_data.pkl")
    deviations_data = load_data("gtfs/deviations.pkl")
    st.write(sites_data.head())
    st.write("Deviations Data", deviations_data.head())

with tab3:
    optimized_data = load_data("gtfs/optimized_route.pkl")
    if optimized_data is not None:
        original_data = load_data("gtfs/gdf.pkl")
        st.header("Optimization Comparison")

        # Before Optimization
        st.subheader("Before Optimization")
        total_time_before = calculate_total_transit_time(all_user_data, 'Time')
        st.write(f"Total time in transit (Before Optimization): {total_time_before}")
        folium_map_before = create_folium_map(all_user_data, "Before Optimization", color='blue')
        if folium_map_before:
            st_folium(folium_map_before, width=700, key="before_optimization")

        # After Optimization
        st.subheader("After Optimization")
        total_time_after = calculate_total_transit_time(optimized_data, 'waypoint_time')
        st.write(f"Total time in transit (After Optimization): {total_time_after}")
        folium_map_after = create_folium_map(optimized_data, "After Optimization", color='red')
        if folium_map_after:
            st_folium(folium_map_after, width=700, key="after_optimization")

with tab4:
    st.header("User Patterns")
    display_map("gtfs/user_patterns_map.html")
