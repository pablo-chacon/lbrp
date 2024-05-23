import pandas as pd
import user_trajectories as ut
import sl_rtd as sl


def main():
    # Load and process user trajectories
    user_gdf, destinations = ut.load_and_process_user_trajectories()
    print("User Trajectories DataFrame:")
    print(user_gdf.head())

    # Save processed user trajectories
    user_gdf.to_pickle('gdf.pkl')
    destinations.to_pickle('dest.pkl')

    # Load timetable and deviations data
    timetable_df, deviations_df, nearby_stops_df = sl.save_all_data()

    # Print dataframes for verification
    print("\nTimetable DataFrame:")
    print(timetable_df.head())

    print("\nDeviations DataFrame:")
    print(deviations_df.head())

    print("\nNearby Stops DataFrame:")
    print(nearby_stops_df.head())

    # Merge timetable and deviations data
    merged_timetable_df = sl.current_timetable(timetable_df, deviations_df)
    print("\nMerged Timetable DataFrame:")
    print(merged_timetable_df.head())

    # Create personalized timetable
    personalized_timetable = create_personalized_timetable(user_gdf, destinations, merged_timetable_df, nearby_stops_df)
    print("\nPersonalized Timetable:")
    print(personalized_timetable.head())

    # Save personalized timetable
    personalized_timetable.to_pickle('personalized_timetable.pkl')


def create_personalized_timetable(user_gdf, destinations, merged_timetable_df, nearby_stops_df):
    # Extract and expand the scope.lines column
    lines_data = merged_timetable_df['scope.lines'].apply(pd.Series)
    lines_data.columns = ['line_id', 'transport_authority', 'designation', 'transport_mode', 'line_name',
                          'group_of_lines']

    # Extract and expand the scope.stop_areas column
    stop_areas_data = merged_timetable_df['scope.stop_areas'].explode().apply(pd.Series)
    stop_areas_data = stop_areas_data.groupby(level=0).first()  # To handle multiple stop areas per row

    # Merge the extracted data back into the main dataframe
    personalized_timetable = pd.concat(
        [merged_timetable_df.drop(['scope.lines', 'scope.stop_areas'], axis=1), lines_data, stop_areas_data], axis=1)

    # Placeholder for your logic to further personalize timetable
    # For now, we'll return the processed timetable as the personalized timetable
    return personalized_timetable


if __name__ == '__main__':
    main()
