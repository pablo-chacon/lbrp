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


def parse_gpx(file_path):
    with open(file_path, 'r') as file:
        gpx = gpxpy.parse(file)
        points_data = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points_data.append({'Latitude': point.latitude, 'Longitude': point.longitude, 'Time': point.time})
        return pd.DataFrame(points_data)


def haversine_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

    # Filter outliers (e.g., remove points with unrealistic speeds)
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    df['prev_point'] = df['geometry'].shift()
    df['distance'] = df.apply(lambda row: row['geometry'].distance(row['prev_point']) if row['prev_point'] else 0, axis=1)

def identify_destinations(gdf, min_stay_duration=1):
    gdf['TimeDelta'] = gdf['Time'].diff().dt.total_seconds() / 3600
    destinations = gdf[gdf['TimeDelta'] >= min_stay_duration].copy()
    destinations['is_destination'] = True
    return destinations


def load_and_process_user_trajectories():
    gpx_folder = 'user_profiles'
    user_profiles = []
    for filename in os.listdir(gpx_folder):
        if filename.endswith('.gpx'):
            gpx_file_path = os.path.join(gpx_folder, filename)
            df = parse_gpx(gpx_file_path)
            user_profiles.append(df)
    df = pd.concat(user_profiles, ignore_index=True)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    total_distance = 0
    for i in range(len(gdf) - 1):
        lat1, lon1 = gdf.iloc[i].Latitude, gdf.iloc[i].Longitude
        lat2, lon2 = gdf.iloc[i + 1].Latitude, gdf.iloc[i + 1].Longitude
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    gdf['TimeDelta'] = gdf['Time'].diff().dt.total_seconds() / 3600
    gdf['Speed'] = total_distance / gdf['TimeDelta']
    return gdf, identify_destinations(gdf)


# Function to aggregate geodata by time intervals
def aggregate_by_time(df, time_interval='hourly'):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    if time_interval == 'hourly':
        df['TimeGroup'] = df['Timestamp'].dt.floor('h')
    elif time_interval == 'daily':
        df['TimeGroup'] = df['Timestamp'].dt.date

if __name__ == "__main__":
    gdf, destinations = load_and_process_user_trajectories()
    print(gdf.head())
    print(destinations.head())
