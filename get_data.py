"""import zipfile
import requests
import io
import pandas as pd


# __Author__ = 'pablo-chacon'
# __Date__ = '2024-02-20'
# __Version__ = '0.1'


#Simple class get data from SL (Stockholm Public Transport) GTFS feed


class SL:

    def __init__(self):
        self.zipped_data = zipfile.ZipFile('/data_sets/sl.zip')


    def get_file(self, filename):
        data = pd.read_csv(self.zipped_data.open(filename))
        #data_zip = zipfile.ZipFile(io.BytesIO(requests.get(self.url, headers=self.header).content))
        #data = pd.read_csv(data_zip.open(filename))
        return data

    def get_calendar(self):
        calendar = self.zip.open('calendar.txt')
        return calendar

    def get_calendar_dates(self):
        calendar_dates = self.zip.open('calendar_dates.txt')
        return calendar_dates

    def get_routes(self):
        routes = self.zip.open('routes.txt')
        return routes

    def get_shapes(self):
        shapes = self.zip.open('shapes.txt')
        return shapes

    def get_stop_times(self):
        stop_times = self.zip.open('stop_times.txt')
        return stop_times

    def get_stops(self):
        stops = self.zip.open('stops.txt')
        return stops

    def get_trips(self):
        trips = self.zip.open('trips.txt')
        return trips

    def extract_all(self):
        self.zip.extractall()
        return 'All files extracted'
"""

