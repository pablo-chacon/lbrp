# user_patterns.py

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt
import numpy as np
import user_trajectories as ut

# Directory containing GPX files
user_profiles_folder = 'user_profiles'

# Function to preprocess geodata
def preprocess_geodata(df):
    # Rename 'Time' column to 'Timestamp' for consistency
    df = df.rename(columns={'Time': 'Timestamp'})

    # Drop duplicates
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'])

    # Handle missing 'Timestamp' values
    df.loc[df['Timestamp'] == "N/A", 'Timestamp'] = pd.NaT

    # Filter outliers (e.g., remove points with unrealistic speeds)
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    df['prev_point'] = df['geometry'].shift()
    df['distance'] = df.apply(lambda row: row['geometry'].distance(row['prev_point']) if row['prev_point'] else 0,
                              axis=1)

    speed_threshold = 0.1  # Example speed threshold in km/s
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['prev_time'] = df['Timestamp'].shift()
    df['time_diff'] = (df['Timestamp'] - df['prev_time']).dt.total_seconds()
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

    # Ensure 'Timestamp' and 'geometry' columns are included
    aggregated_data['Timestamp'] = df['TimeGroup']
    aggregated_data['geometry'] = df.groupby('TimeGroup')['geometry'].first().values

    return aggregated_data


# Function to analyze movement characteristics
def analyze_movement(df):
    if 'Timestamp' not in df.columns:
        raise ValueError("Timestamp column not found in DataFrame.")
    if 'geometry' not in df.columns:
        raise ValueError("Geometry column not found in DataFrame.")

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

    # Filter out infinite or very large values
    features = features.replace([np.inf, -np.inf], np.nan).dropna()

    model = DecisionTreeClassifier()
    model.fit(features, labels.loc[features.index])

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


# Function to visualize movement pattern with clearer scattering
def visualize_movement_pattern(df):
    fig, ax = plt.subplots(figsize=(12, 10))
    unique_clusters = df['cluster'].unique()
    colors = plt.cm.get_cmap('tab20', len(unique_clusters))  # Use a colormap with enough distinct colors

    for cluster in unique_clusters:
        cluster_data = df[df['cluster'] == cluster]
        x = cluster_data['Longitude']
        y = cluster_data['Latitude']
        ax.scatter(x, y, s=50, edgecolor='k', alpha=0.6, label=f'Cluster {cluster}', color=colors(cluster))

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Movement Patterns')
    ax.legend(loc='best')
    plt.grid(True)
    plt.show()

# Directory containing GPX files
user_profiles_folder = 'user_profiles'

def load_and_process_all_gpx_files(folder):
    all_data = pd.DataFrame()

    for filename in os.listdir(folder):
        if filename.endswith(".gpx"):
            filepath = os.path.join(folder, filename)
            user_data = ut.parse_gpx(filepath)
            all_data = pd.concat([all_data, user_data], ignore_index=True)

    return all_data

def main():
    # Load and process all GPX files
    all_user_data = load_and_process_all_gpx_files(user_profiles_folder)

    # Save the consolidated DataFrame to a pickle file
    all_user_data.to_pickle('all_user_data.pkl')

    # Preprocess geodata
    preprocessed_data = preprocess_geodata(all_user_data)

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
