import streamlit as st
import subprocess
import pandas as pd
import folium
from streamlit_folium import st_folium
import logging


# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23


# Set up logging.
logging.basicConfig(level=logging.INFO)


# Run scripts, generate data.
def run_scripts():
    # Run user_trajectories.py
    subprocess.run(["python", "user_trajectories.py"])

    # Run lbrp.py
    subprocess.run(["python", "lbrp.py"])

    # Run user_patterns.py
    subprocess.run(["python", "user_patterns.py"])


# Load data functions
@st.cache_data
def load_data(file_path):
    return pd.read_pickle(file_path)


# Create folium map from DataFrame.
def create_folium_map(data, title):
    if 'Latitude' in data.columns and 'Longitude' in data.columns:
        m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=12)
        for _, row in data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['user_id']}<br>Time: {row['Time']}",
            ).add_to(m)
    elif 'lat' in data.columns and 'lon' in data.columns:
        # Filter out rows with NaN values in 'lat' or 'lon'
        data = data.dropna(subset=['lat', 'lon'])
        m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=13)
        for _, row in data.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"{row['name']}<br>Note: {row['note']}",
            ).add_to(m)
    else:
        st.error(f"Data for {title} does not contain 'Latitude'/'Longitude' or 'lat'/'lon' columns.")
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
all_user_data = load_data("all_user_data.pkl")
optimized_data = load_data("optimized_route.pkl")
optimized_data = pd.DataFrame(optimized_data)

# Streamlit UI
st.title("User Trajectories and Optimization Visualization")

tab1, tab2, tab3, tab4 = st.tabs(["User Trajectories", "Real-Time Data", "Optimization Comparison", "User Patterns"])

with tab1:
    st.header("User Trajectories")
    st.write(all_user_data.head())
    st.header("Trajectory Map")
    display_map("user_trajectories_map.html")

with tab2:
    st.header("Real-Time Data")
    sites_data = load_data("sites_data.pkl")
    deviations_data = load_data("deviations.pkl")
    st.write(sites_data.head())
    st.write("Deviations Data", deviations_data.head())

with tab3:
    st.header("Optimization Comparison")
    st.subheader("Before Optimization")
    folium_map_before = create_folium_map(all_user_data, "Before Optimization")
    if folium_map_before:
        st_folium(folium_map_before, width=700, key="before_optimization")

    st.subheader("After Optimization")
    folium_map_after = create_folium_map(optimized_data, "After Optimization")
    if folium_map_after:
        st_folium(folium_map_after, width=700, key="after_optimization")

with tab4:
    st.header("User Patterns")
    display_map("user_patterns_map.html")
