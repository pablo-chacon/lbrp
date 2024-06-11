import gpxpy
import gpxpy.gpx
import random
from datetime import datetime, timedelta


# __Author__: pablo-chacon
# __Version__: 1.0.0
# __Date__: 2024-05-11

# Params
num_users = 10
start_lat, start_lon = 59.3293, 18.0686  # Stockholm coordinates
radius = 0.05  # Random offset.
workday_locations = ["Workplace", "Park", "Cafe", "Gym"]  # Possible locations for workdays
weekend_locations = ["Sture P", "Parents", "IKEA", "Countryside", "Gym"]  # Possible locations for weekends


def gen_rand_location(center_lat, center_lon, radius):
    # Random location within radius.
    lat_offset = random.uniform(-radius, radius)
    lon_offset = random.uniform(-radius, radius)
    return center_lat + lat_offset, center_lon + lon_offset


def generate_user_profile(start_time, end_time):
    # Generate user profile.
    user_gpx = gpxpy.gpx.GPX()

    # Initialize track, segment
    track = gpxpy.gpx.GPXTrack()
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)
    user_gpx.tracks.append(track)

    # Random locations
    locations = {
        "workdays": random.sample(workday_locations, 4),  # 4 workday locations
        "weekends": random.sample(weekend_locations, 4)  # 4 weekend locations
    }

    # User movements
    current_time = start_time
    while current_time <= end_time:
        # Return to starting point once every 24 hours
        if current_time.hour == 0 and current_time.minute == 0:
            lat, lon = start_lat, start_lon
        else:
            lat, lon = gen_rand_location(start_lat, start_lon, radius)

        # Random location 6-9 hours mon-fri
        if current_time.weekday() < 5:
            stay_time = random.randint(6, 9)
            location = random.choice(locations["workdays"])
        # Rec time 1-2 hours on workdays.
        elif current_time.weekday() < 7:
            stay_time = random.randint(1, 2)
            location = random.choice(locations["workdays"])
        # Weekend stuff.
        else:
            stay_time = random.randint(2, 10)
            location = random.choice(locations["weekends"])

        # Create GPX track point
        point = gpxpy.gpx.GPXTrackPoint(
            latitude=lat,
            longitude=lon,
            elevation=0,  # Elevation can be adjusted if needed
            time=current_time
        )
        user_gpx.tracks[0].segments[0].points.append(point)

        # Update time for next point
        current_time += timedelta(hours=stay_time)

    return user_gpx


# Generate random locations
random.seed(42)  # Ensure reproducibility
workday_locations = [gen_rand_location(start_lat, start_lon, radius) for _ in range(len(workday_locations))]
weekend_locations = [gen_rand_location(start_lat, start_lon, radius) for _ in range(len(weekend_locations))]

# Generate profiles
user_profiles = []
for i in range(num_users):
    start_time = datetime(2024, 3, 1, 8, 0, 0)  # Start time
    end_time = start_time + timedelta(days=30)  # End time (30 days simulation)
    user_gpx = generate_user_profile(start_time, end_time)
    user_profiles.append(user_gpx)


# Write GPX user files
for i, user_gpx in enumerate(user_profiles):
    with open(f"user_{i + 1}_profile.gpx", "w") as gpx_file:
        gpx_file.write(user_gpx.to_xml())

print("User profiles generated successfully.")
