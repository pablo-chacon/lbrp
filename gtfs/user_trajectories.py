import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import xml.etree.ElementTree as ET
from datetime import timedelta


# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23

def parse_gpx(gpx_file_path):
    tree = ET.parse(gpx_file_path)
    root = tree.getroot()
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
    data = []
    for trkpt in root.findall('.//default:trkpt', ns):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        time = trkpt.find('default:time', ns).text
        data.append([lat, lon, time])
    return pd.DataFrame(data, columns=['Latitude', 'Longitude', 'Time'])


def identify_destinations(gdf):
    gdf['is_destination'] = False
    gdf.loc[gdf.index[-1], 'is_destination'] = True
    return gdf


def process_user_trajectories():
    gpx_folder = 'user_profiles'
    user_profiles = []
    for filename in os.listdir(gpx_folder):
        if filename.endswith('.gpx'):
            gpx_file_path = os.path.join(gpx_folder, filename)
            df = parse_gpx(gpx_file_path)
            df['user_id'] = filename
            user_profiles.append(df)
    df = pd.concat(user_profiles, ignore_index=True)
    df['Time'] = pd.to_datetime(df['Time'])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    total_distance = 0
    for i in range(len(gdf) - 1):
        lat1, lon1 = gdf.iloc[i].Latitude, gdf.iloc[i].Longitude
        lat2, lon2 = gdf.iloc[i + 1].Latitude, gdf.iloc[i + 1].Longitude
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    gdf['TimeDelta'] = gdf['Time'].diff().dt.total_seconds() / 3600
    gdf['Speed'] = total_distance / gdf['TimeDelta']
    return gdf, identify_destinations(gdf)


def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0  # Earth radius in km.
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def regenerate_48_hour_movements(all_user_data):
    regenerated_data = pd.DataFrame()
    for user_id, group in all_user_data.groupby('user_id'):
        start_time = group['Time'].min()
        end_time = start_time + timedelta(hours=48)
        pattern_data = group[(group['Time'] >= start_time) & (group['Time'] <= end_time)]
        regenerated_data = pd.concat([regenerated_data, pattern_data])
    return regenerated_data


if __name__ == "__main__":
    gdf, destinations = process_user_trajectories()
    print("gdf:", gdf.head())
    print("destinations:", destinations.head())
    gdf.to_pickle('all_user_data.pkl')

    # Regenerate 48-hour movements.
    regenerated_data = regenerate_48_hour_movements(pd.read_pickle('all_user_data.pkl'))

    # Save regenerated data.
    regenerated_data.to_pickle('regenerated_48_hour_data.pkl')
