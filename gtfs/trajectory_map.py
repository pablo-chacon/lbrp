import math
import os
import gpxpy
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.constants import R
from shapely.geometry import Point, LineString
from math import radians
import sl_rtd as sl


# Function to parse GPX file and extract waypoint data
def parse_gpx(file_path):
    with open(file_path, 'r') as file:
        gpx = gpxpy.parse(file)
        points_data = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points_data.append({'Latitude': point.latitude, 'Longitude': point.longitude, 'Time': point.time})
        return pd.DataFrame(points_data)


# Calculate the great circle distance between gps points
def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


# Read GPX files and parse waypoints
gpx_folder = 'user_profiles'
user_profiles = []

for filename in os.listdir(gpx_folder):
    if filename.endswith('.gpx'):
        gpx_file_path = os.path.join(gpx_folder, filename)
        df = parse_gpx(gpx_file_path)
        user_profiles.append(df)

# Concatenate DataFrames into one
df = pd.concat(user_profiles, ignore_index=True)

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

# Calculate distance and speed
total_distance = 0
for i in range(len(gdf) - 1):
    lat1, lon1 = gdf.iloc[i].Latitude, gdf.iloc[i].Longitude
    lat2, lon2 = gdf.iloc[i + 1].Latitude, gdf.iloc[i + 1].Longitude
    total_distance += haversine_distance(lat1, lon1, lat2, lon2)

gdf['TimeDelta'] = gdf['Time'].diff().dt.total_seconds() / 3600
gdf['Speed'] = total_distance / gdf['TimeDelta']

# Plot waypoints
gdf.plot(marker='o', color='red', markersize=5)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Waypoints Visualization')
plt.show()

# Plot trajectory
trajectory = LineString(gdf['geometry'])
trajectory_gdf = gpd.GeoDataFrame(geometry=[trajectory])
trajectory_gdf.plot()
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Trajectory')
plt.show()

print(gdf.head())
