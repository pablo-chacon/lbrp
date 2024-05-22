import os
import gpxpy
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt
import numpy as np


# Function to load user profiles
def load_user_profiles(profiles_folder):
    profiles = []
    for filename in os.listdir(profiles_folder):
        if filename.endswith('.gpx'):
            profile_path = os.path.join(profiles_folder, filename)
            with open(profile_path, 'r') as file:
                gpx = gpxpy.parse(file)
                points_data = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            points_data.append({
                                'Latitude': point.latitude,
                                'Longitude': point.longitude,
                                'Elevation': point.elevation,
                                'Timestamp': point.time if point.time else "N/A"
                                # Extract timestamp from GPX point, handle missing values
                            })
                profile_df = pd.DataFrame(points_data)
                profiles.append(profile_df)
    if profiles:
        return pd.concat(profiles, ignore_index=True)
    else:
        return pd.DataFrame()


# Function to preprocess geodata
def preprocess_geodata(df):
    # Drop duplicates
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'])

    # Handle missing 'Timestamp' values
    df['Timestamp'].replace("N/A", pd.NaT, inplace=True)

    # Filter outliers (e.g., remove points with unrealistic speeds)
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    df['prev_point'] = df['geometry'].shift()
    df['distance'] = df.apply(lambda row: row['geometry'].distance(row['prev_point']) if row['prev_point'] else 0,
                              axis=1)

    speed_threshold = 0.1  # Example speed threshold in km/s
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['Time'] = df['Timestamp']
    df['prev_time'] = df['Time'].shift()
    df['time_diff'] = (df['Time'] - df['prev_time']).dt.total_seconds()
    df['speed'] = df['distance'] / df['time_diff']

    # Filter rows where speed exceeds threshold
    df = df[df['speed'] <= speed_threshold].copy()

    return df


# Function to aggregate geodata by time intervals
def aggregate_by_time(df, time_interval='hourly'):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    if time_interval == 'hourly':
        df['TimeGroup'] = df['Timestamp'].dt.floor('h')
    elif time_interval == 'daily':
        df['TimeGroup'] = df['Timestamp'].dt.date

    # Exclude non-numeric columns for aggregation
    numeric_df = df.select_dtypes(include=[np.number])
    aggregated_data = numeric_df.groupby(df['TimeGroup']).mean().reset_index()
    return aggregated_data


# Function to analyze movement characteristics
def analyze_movement(df):
    if 'Timestamp' not in df.columns:
        raise ValueError("Timestamp column not found in DataFrame.")

    df = df.sort_values(by='Timestamp')
    df['next_point'] = df['geometry'].shift(-1)
    df['distance'] = df.apply(lambda row: row['geometry'].distance(row['next_point']) if row['next_point'] else 0,
                              axis=1)
    df['next_time'] = df['Timestamp'].shift(-1)
    df['time_diff'] = (df['next_time'] - df['Timestamp']).dt.total_seconds() / 3600  # hours
    df['speed'] = df['distance'] / df['time_diff']

    df['next_speed'] = df['speed'].shift(-1)
    df['acceleration'] = (df['next_speed'] - df['speed']) / df['time_diff']

    return df


# Function to identify patterns
def identify_patterns(df):
    coords = df[['Longitude', 'Latitude']].values
    clustering = DBSCAN(eps=0.001, min_samples=5).fit(coords)
    df['cluster'] = clustering.labels_
    return df


# Function to build a model
def build_model(df):
    features = df[['speed', 'acceleration']]
    labels = df['cluster']

    model = DecisionTreeClassifier()
    model.fit(features, labels)

    return model


# Function to evaluate and refine the model
def evaluate_and_refine_model(model, validation_data):
    if validation_data is not None:
        X_val = validation_data[['speed', 'acceleration']]
        y_val = validation_data['cluster']

        predictions = model.predict(X_val)

        accuracy = accuracy_score(y_val, predictions)
        precision = precision_score(y_val, predictions, average='weighted')
        recall = recall_score(y_val, predictions, average='weighted')

        print(f"Model Accuracy: {accuracy}")
        print(f"Model Precision: {precision}")
        print(f"Model Recall: {recall}")

    return model


# Function to visualize movement pattern
def visualize_movement_pattern(df):
    fig, ax = plt.subplots(figsize=(10, 10))

    for cluster, group_data in df.groupby('cluster'):
        x = group_data['Longitude']
        y = group_data['Latitude']
        ax.scatter(x, y, label=f'Cluster {cluster}', alpha=0.5)

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Movement Patterns')
    ax.legend()
    plt.show()


# Main function
def main():
    # Load user profiles
    profiles_folder = 'user_profiles'
    user_profiles = load_user_profiles(profiles_folder)

    # Preprocess geodata
    preprocessed_data = preprocess_geodata(user_profiles)

    # Aggregate geodata by time intervals
    time_interval = 'hourly'  # Options: 'hourly', 'daily'
    aggregated_data = aggregate_by_time(preprocessed_data, time_interval)

    # Analyze movement characteristics
    movement_characteristics = analyze_movement(aggregated_data)

    # Identify patterns
    patterns = identify_patterns(movement_characteristics)

    # Build a model
    model = build_model(patterns)

    # Evaluate and refine the model
    validation_data = None  # Add validation data if available
    refined_model = evaluate_and_refine_model(model, validation_data)

    # Visualize movement pattern
    visualize_movement_pattern(patterns)


if __name__ == "__main__":
    main()
