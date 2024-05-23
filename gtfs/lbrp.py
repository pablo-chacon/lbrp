import pandas as pd
import geopandas as gpd
import user_trajectories as ut
import sl_rtd as sl
import matplotlib.pyplot as plt


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-23

def load_and_process_gpx_files():
    gdf, destinations = ut.load_and_process_user_trajectories()
    return gdf, destinations


def create_optimized_timetable(user_gdf, destinations, timetable_df, deviations_df, nearby_stops_df):
    # Merge timetable with deviations
    merged_timetable_df = sl.current_timetable(timetable_df, deviations_df)

    # Create an optimized timetable based on user trajectories and deviations
    optimized_timetable = []

    for _, user_row in user_gdf.iterrows():
        user_point = user_row.geometry
        user_time = user_row.Time

        nearby_stops = nearby_stops_df.copy()
        nearby_stops['distance'] = nearby_stops.apply(
            lambda row: user_point.distance(gpd.points_from_xy([row['lon']], [row['lat']])[0]), axis=1)
        nearby_stops = nearby_stops[nearby_stops['distance'] < 0.001]  # Filter stops within 1 km

        if not nearby_stops.empty:
            for _, stop_row in nearby_stops.iterrows():
                stop_id = stop_row.id

                relevant_timetable = merged_timetable_df[
                    (merged_timetable_df['stop_area_id'] == stop_id) &
                    (merged_timetable_df['valid_from'] <= user_time) &
                    ((merged_timetable_df['valid_to'].isna()) | (merged_timetable_df['valid_to'] >= user_time))
                    ]

                if not relevant_timetable.empty:
                    optimized_timetable.append(relevant_timetable.iloc[0].to_dict())

    optimized_timetable_df = pd.DataFrame(optimized_timetable).drop_duplicates()
    return optimized_timetable_df


def main():
    # Load user trajectory data
    user_gdf, destinations = load_and_process_gpx_files()
    print("User Trajectories DataFrame:")
    print(user_gdf.head())
    print("\nDestinations DataFrame:")
    print(destinations.head())

    # Load timetable, deviations, and nearby stops data
    timetable_df, deviations_df, nearby_stops_df = sl.save_all_data()
    print("\nTimetable DataFrame:")
    print(timetable_df.head())
    print("\nDeviations DataFrame:")
    print(deviations_df.head())
    print("\nNearby Stops DataFrame:")
    print(nearby_stops_df.head())

    # Generate optimized timetable
    optimized_timetable_df = create_optimized_timetable(user_gdf, destinations, timetable_df, deviations_df,
                                                        nearby_stops_df)
    print("\nOptimized Timetable DataFrame:")
    print(optimized_timetable_df.head())

    # Save the optimized timetable to a file
    optimized_timetable_df.to_pickle('optimized_timetable.pkl')

    # Visualize the user trajectories
    fig, ax = plt.subplots(figsize=(10, 6))
    user_gdf.plot(ax=ax, color='blue', marker='o', markersize=5, label='Trajectory')
    destinations.plot(ax=ax, color='red', marker='x', markersize=5, label='Destinations')
    plt.legend()
    plt.title("User Trajectories and Destinations")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()


if __name__ == '__main__':
    main()
