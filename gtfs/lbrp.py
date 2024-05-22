import user_trajectories as ut
import sl_rtd as sl
import pandas as pd


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-22

"""Implements matching user trajectories to nearby stops and find possible routes."""


def match_trajectories_to_stops(user_gdf, nearby_stops_df, merged_timetable_df):
    matches = []

    print("Merged Timetable Columns:", merged_timetable_df.columns)

    for idx, user_point in user_gdf.iterrows():
        closest_stop = nearby_stops_df.loc[
            (nearby_stops_df['lat'] - user_point['Latitude']).abs().idxmin()]
        stop_id = closest_stop['extId']
        matched_routes = []

        # Handle the nested structure in 'scope.lines'
        for _, row in merged_timetable_df.iterrows():
            if isinstance(row['scope.lines'], list):
                line_ids = [line['id'] for line in row['scope.lines'] if 'id' in line]
                if stop_id in line_ids:
                    matched_routes.append(row)

        matched_routes_df = pd.DataFrame(matched_routes)

        for _, route in matched_routes_df.iterrows():
            match = {
                'user_point_index': idx,
                'user_latitude': user_point['Latitude'],
                'user_longitude': user_point['Longitude'],
                'stop_id': stop_id,
                'route': route['line_name']
            }
            matches.append(match)

    matches_df = pd.DataFrame(matches)
    return matches_df


def main():
    # Load and process user trajectories
    user_gdf, destinations = ut.load_and_process_user_trajectories()
    print(user_gdf.head())

    # Save and load data from sl_rtd
    timetable_df, deviations_df, nearby_stops_df = sl.save_all_data()
    print(timetable_df.head())
    print(deviations_df.head())
    print(nearby_stops_df.head())

    # Match user trajectories to stops and find possible routes
    merged_timetable_df = sl.current_timetable(timetable_df, deviations_df)
    print("Merged Timetable DataFrame:", merged_timetable_df.head())
    matches_df = match_trajectories_to_stops(user_gdf, nearby_stops_df, merged_timetable_df)
    print(matches_df.head())


if __name__ == "__main__":
    main()
