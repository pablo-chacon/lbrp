import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import pickle


# __Author__: pablo-chacon
# __Version__: 1.0.2
# __Date__: 2024-05-23


def main():
    # Load user trajectory data
    all_user_data = pd.read_pickle('all_user_data.pkl')
    print("All user data:", all_user_data.head())

    # Preprocess data
    all_user_data['Time'] = pd.to_datetime(all_user_data['Time'])
    all_user_data.sort_values(by=['user_id', 'Time'], inplace=True)

    # Cluster user trajectories
    clustering = DBSCAN(eps=0.01, min_samples=5).fit(all_user_data[['Latitude', 'Longitude']])
    all_user_data['cluster'] = clustering.labels_

    # Generate representative routes
    representative_routes = all_user_data.groupby('cluster')[['Longitude', 'Latitude']].mean()
    print("Representative Routes DataFrame:", representative_routes.head())

    # Load optimized route data
    with open('optimized_route.pkl', 'rb') as f:
        optimized_route = pickle.load(f)
    if isinstance(optimized_route, list):
        optimized_route_df = pd.DataFrame(optimized_route)
    else:
        optimized_route_df = optimized_route

    if optimized_route_df.empty:
        print("Optimized Route DataFrame is empty")
        return

    optimized_route_df.rename(columns={
        'waypoint_lon': 'Longitude',
        'waypoint_lat': 'Latitude',
        'site_lat': 'site_lat',
        'site_lon': 'site_lon',
        'site_lat': 'site_lat_dest',
        'site_lon': 'site_lon_dest'
    }, inplace=True)

    print("Optimized Route DataFrame:", optimized_route_df.head())

    # Match representative routes to optimized routes
    matched_routes = []
    for _, row in representative_routes.iterrows():
        matched = optimized_route_df[
            ((optimized_route_df['Longitude'] - row['Longitude']).abs() < 0.001) &
            ((optimized_route_df['Latitude'] - row['Latitude']).abs() < 0.001)
            ]
        matched_routes.append(matched)
    matched_routes_df = pd.concat(matched_routes)
    print("Matched Routes DataFrame:", matched_routes_df.head())

    # Generate generalized optimized timetable
    matched_routes_df['scheduled'] = pd.to_datetime(matched_routes_df['scheduled'])
    matched_routes_df['expected'] = pd.to_datetime(matched_routes_df['expected'])
    generalized_timetable = matched_routes_df.groupby(['site_id', 'line_id', 'destination']).agg({
        'scheduled': 'mean',
        'expected': 'mean',
        'transport_mode': 'first',
        'site_lat_dest': 'first',
        'site_lon_dest': 'first'
    }).reset_index()

    print("Generalized Optimized Timetable:", generalized_timetable.head())
    generalized_timetable.to_pickle('generalized_optimized_timetable.pkl')


if __name__ == '__main__':
    main()
