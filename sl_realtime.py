from google.transit import gtfs_realtime_pb2
import requests

key = "b366e4ab8bc44017b4c65229323fa7b0"
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get("https://opendata.samtrafiken.se/gtfs-rt-sweden/{operator}/VehiclePositionsSweden.pb?key={key}")
feed.ParseFromString(response.content)
for entity in feed.entity:
    if entity.HasField('trip_update'):
        print(entity.trip_update)
