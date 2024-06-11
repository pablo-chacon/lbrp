import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from shapely.geometry import Point
from datetime import datetime, timedelta


# __Author__: pablo-chacon
# __Version__: 1.0.3
# __Date__: 2024-06-01

def preprocess_geodata(df):
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values(by=['Time'])
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    return df


def analyze_movement(df):
    df['next_point'] = df['geometry'].shift(-1)
    df['distance'] = df.apply(
        lambda row: row['geometry'].distance(row['next_point']) if pd.notnull(row['next_point']) else 0, axis=1)
    df['time_diff'] = df['Time'].diff().dt.total_seconds().shift(-1)
    df['speed'] = df.apply(lambda row: row['distance'] / row['time_diff'] if row['time_diff'] > 0 else 0, axis=1)
    return df


def cluster_user_trajectories(df, n_clusters=5):
    coords = df[['Longitude', 'Latitude']].values
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    df['cluster'] = kmeans.fit_predict(coords_scaled)
    return df, kmeans


def generate_representative_routes(df):
    numeric_cols = ['Longitude', 'Latitude']
    clusters = df.groupby('cluster')
    representative_routes = clusters[numeric_cols].mean()
    return representative_routes


def match_routes_to_optimized(representative_routes, optimized_route):
    matched_routes = []
    for idx, row in representative_routes.iterrows():
        matched = optimized_route[
            ((optimized_route['Longitude'] - row['Longitude']).abs() < 0.001) &
            ((optimized_route['Latitude'] - row['Latitude']).abs() < 0.001)
            ]
        matched_routes.append(matched)
    return pd.concat(matched_routes)


def generate_generalized_timetable(matched_routes):
    matched_routes['scheduled'] = pd.to_datetime(matched_routes['scheduled'])
    matched_routes['expected'] = pd.to_datetime(matched_routes['expected'])
    generalized_timetable = matched_routes.groupby(['site_id', 'line_id', 'destination']).agg({
        'scheduled': 'mean',
        'expected': 'mean',
        'transport_mode': 'first'
    }).reset_index()
    return generalized_timetable


def user_patterns():
    user_profiles_folder = 'user_profiles'
    all_user_data = pd.read_pickle('all_user_data.pkl')

    if all_user_data is not None:
        print("All user data:", all_user_data.head())

    all_user_data = preprocess_geodata(all_user_data)
    aggregated_data = analyze_movement(all_user_data)
    clustered_data, kmeans_model = cluster_user_trajectories(aggregated_data)
    representative_routes = generate_representative_routes(clustered_data)
    print("Representative Routes DataFrame:", representative_routes.head())

    # Load optimized route
    try:
        with open('optimized_route.pkl', 'rb') as f:
            optimized_route = pickle.load(f)
    except Exception as e:
        print(f"Error loading optimized_route.pkl: {e}")
        return

    if isinstance(optimized_route, list):
        optimized_route = pd.DataFrame(optimized_route)
    print("Optimized Route DataFrame:", optimized_route.head())

    optimized_route.rename(columns={'waypoint_lon': 'Longitude', 'waypoint_lat': 'Latitude'}, inplace=True)
    print("Adjusted Optimized Route DataFrame:", optimized_route.head())

    matched_routes = match_routes_to_optimized(representative_routes, optimized_route)
    print("Matched Routes DataFrame:", matched_routes.head())

    generalized_optimized_timetable = generate_generalized_timetable(matched_routes)
    print("Generalized Optimized Timetable:", generalized_optimized_timetable)

    generalized_optimized_timetable.to_pickle('generalized_optimized_timetable.pkl')
