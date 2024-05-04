from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import gpxpy
import os


gpx_folder = 'user_profiles' # Directory containing GPX files
data = []


# Iterate over GPX files in the folder
for filename in os.listdir(gpx_folder):
    if filename.endswith('.gpx'):
        # Load GPX file
        gpx_file_path = os.path.join(gpx_folder, filename)
        with open(gpx_file_path, 'r') as file:
            gpx = gpxpy.parse(file)

        # Extract data from GPX file
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latitude = point.latitude
                    longitude = point.longitude
                    elevation = point.elevation
                    time = point.time
                    # Append extracted data to the list
                    data.append({'Latitude': latitude, 'Longitude': longitude, 'Elevation': elevation, 'Time': time})

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)