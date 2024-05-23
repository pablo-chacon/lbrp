import streamlit as st
import sl_rtd as sl
import user_trajectories as ut
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-23

# Fetch and save all data
sl.save_all_data()

# Load the pickled data
timetable = pd.read_pickle('timetable.pkl')
ut_df = pd.read_pickle('gdf.pkl')
dest_df = pd.read_pickle('dest.pkl')
deviations = pd.read_pickle('deviations.pkl')
nearby_stops = pd.read_pickle('nearby_stops.pkl')

# Streamlit app title
st.title('SL Real-Time Data and User Trajectories Visualization')

# Display the dataframes
st.header("Timetable DataFrame")
st.dataframe(timetable)

st.header("User Trajectories DataFrame")
st.dataframe(ut_df)

st.header("Destinations DataFrame")
st.dataframe(dest_df)

st.header("Deviations DataFrame")
st.dataframe(deviations)

st.header("Nearby Stops DataFrame")
st.dataframe(nearby_stops)

# Plotting the user trajectories
st.header('User Trajectories and Destinations')
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(ut_df['Longitude'], ut_df['Latitude'], c='blue', label='User Trajectories', s=1)
ax.scatter(dest_df['Longitude'], dest_df['Latitude'], c='red', label='Destinations', s=10)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('User Trajectories and Destinations')
ax.legend()
st.pyplot(fig)

# Plotting the timetable data
st.header('Number of Lines per Transport Mode')
if 'transport_mode' in timetable.columns:
    timetable_modes = timetable['transport_mode'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    timetable_modes.plot(kind='bar', ax=ax)
    ax.set_xlabel('Transport Mode')
    ax.set_ylabel('Number of Lines')
    ax.set_title('Number of Lines per Transport Mode')
    st.pyplot(fig)
else:
    st.write("The column 'transport_mode' is not present in timetable_df.")

# Plotting the deviations data
st.header('Number of Deviations per Priority Level')
if 'priority.importance_level' in deviations.columns:
    deviations_priority = deviations['priority.importance_level'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    deviations_priority.plot(kind='bar', ax=ax)
    ax.set_xlabel('Priority Level')
    ax.set_ylabel('Number of Deviations')
    ax.set_title('Number of Deviations per Priority Level')
    st.pyplot(fig)
else:
    st.write("The column 'priority.importance_level' is not present in deviations_df.")

# Convert user trajectories DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(ut_df, geometry=gpd.points_from_xy(ut_df.Longitude, ut_df.Latitude))

# Plotting the trajectories on a map
st.header('User Trajectories on Map')
fig, ax = plt.subplots(figsize=(10, 6))
gdf.plot(ax=ax, marker='o', color='blue', markersize=1)
ax.set_title('User Trajectories on Map')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
st.pyplot(fig)
