import math
import os
from math import radians
import geopandas as gpd
import gpxpy
import pandas as pd
from scipy.constants import R


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-22


"""Implements functions to process user trajectories and identify destinations.
    Reads GPX files, calculates distances, and identifies destinations based on stay duration."""


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


if __name__ == "__main__":
    gdf, destinations = load_and_process_user_trajectories()
    gdf.to_pickle('gdf.pkl')
    destinations.to_pickle('dest.pkl')
    print(gdf.head())
    print(destinations.head())
