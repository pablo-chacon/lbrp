import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import gpxpy
import math
from shapely.geometry import Point, LineString


def extract_point_data(point):
    return {
        'Latitude': point.latitude,
        'Longitude': point.longitude,
        'Elevation': point.elevation,
        'Time': point.time
    }


# Parse GPX file, extract waypoints
def parse_gpx(file_path):
    with open(file_path, 'r') as file:
        gpx = gpxpy.parse(file)
        points_data = [extract_point_data(point) for track in gpx.tracks for segment in track.segments for point in
                       segment.points]
        return pd.DataFrame(points_data)


# Calculate distance between two points
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


# GPX files
gpx_folder = 'user_profiles'
R = 6371.0  # Earth Radius
radians = math.radians
# DataFrame objects
dfs = []

# Iterate GPX files.
for filename in os.listdir(gpx_folder):
    if filename.endswith('.gpx'):
        # Load and parse GPX file
        gpx_file_path = os.path.join(gpx_folder, filename)
        df = parse_gpx(gpx_file_path)
        dfs.append(df)

# Concatenate DataFrames into a DataFrame
df = pd.concat(dfs, ignore_index=True)

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
gdf.head()
# Waypoints
gdf.plot(marker='o', color='red', markersize=5)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Waypoints Visualization')
plt.show()

# Total distance.
total_distance = 0
for i in range(len(gdf) - 1):
    lat1, lon1 = gdf.iloc[i].Latitude, gdf.iloc[i].Longitude
    print(lat1, lon1)
    lat2, lon2 = gdf.iloc[i + 1].Latitude, gdf.iloc[i + 1].Longitude
    cords = [lat1, lon1, lat2, lon2]
    total_distance += haversine_distance(*cords)

print(f'Total distance traveled: {total_distance:.2f} kilometers')

# Calculate speed.
gdf['TimeDelta'] = gdf['Time'].diff().dt.total_seconds() / 3600  # Difference in hours
gdf['Speed'] = total_distance / gdf['TimeDelta']  # km/h

# Plot speed over time
plt.plot(gdf['Time'], gdf['Speed'])
plt.xlabel('Time')
plt.ylabel('Speed (km/h)')
plt.title('Speed Over Time')
plt.show()

# Calculate and plot trajectory
trajectory = LineString(gdf['geometry'])
trajectory_gdf = gpd.GeoDataFrame(geometry=[trajectory])
trajectory_gdf.plot()
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Trajectory')
#plt.show()

# Plot point-to-point movement for each user
fig, ax = plt.subplots(figsize=(10, 10))

# Group data by user and iterate over each group
for user_id, group_data in gdf.groupby(level=0):
    # Extract coordinates as LineString
    line = LineString(group_data['geometry'])
    # Plot the LineString
    ax.plot(line.xy[0], line.xy[1], label=f'User {user_id}')

# Set labels and title
ax.set_xlabel('Longitude')

ax.set_ylabel('Latitude')
ax.set_title('Point-to-Point Movement for Each User')
ax.legend()

# Show plot
plt.show()
