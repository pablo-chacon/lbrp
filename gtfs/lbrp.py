import pandas as pd
from geopy.distance import great_circle
import sl_rtd
import user_trajectories as ut


def find_nearby_stops(user_point, nearby_stops_df, radius=150):
    nearby_stops = []
    for _, stop in nearby_stops_df.iterrows():
        stop_point = (stop['lat'], stop['lon'])
        distance = great_circle(user_point, stop_point).meters
        if distance <= radius:
            nearby_stops.append(stop['extId'])
    return nearby_stops


def match_trajectories_to_stops(user_gdf, nearby_stops_df, merged_timetable_df):
    user_gdf['nearby_stops'] = user_gdf.apply(
        lambda row: find_nearby_stops((row['Latitude'], row['Longitude']), nearby_stops_df), axis=1
    )
    matches = []
    for _, row in user_gdf.iterrows():
        for stop_id in row['nearby_stops']:
            matching_lines = merged_timetable_df[
                (merged_timetable_df['stop_id'] == stop_id) &
                (merged_timetable_df['departure_time'].between(row['Time'] - pd.Timedelta(minutes=10),
                                                               row['Time'] + pd.Timedelta(minutes=10)))
                ]
            for _, match in matching_lines.iterrows():
                matches.append({
                    'user_point': (row['Latitude'], row['Longitude']),
                    'user_time': row['Time'],
                    'stop_id': stop_id,
                    'line_id': match['line_id'],
                    'departure_time': match['departure_time']
                })
    return pd.DataFrame(matches)


if __name__ == "__main__":
    # Run sl_rtd to fetch and save data
    sl_rtd.main()

    # Load data from sl_rtd.py
    timetable_df = pd.read_pickle('timetable.pkl')
    deviations_df = pd.read_pickle('deviations.pkl')
    nearby_stops_df = pd.read_pickle('nearby_stops.pkl')

    # Get merged timetable with deviations
    merged_timetable_df = sl_rtd.current_timetable(timetable_df, deviations_df)

    # Load user trajectories
    user_gdf = ut.load_and_process_user_trajectories()

    # Match trajectories to stops
    matches_df = match_trajectories_to_stops(user_gdf, nearby_stops_df, merged_timetable_df)

    # Save matches
    matches_df.to_pickle('matched_trajectories.pkl')
    print(matches_df.head())
