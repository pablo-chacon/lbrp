import requests


api_key = ""
url = "https://opendata.samtrafiken.se/gtfs/sl/sl.zip?key="


def get_data():
    response = requests.get(url)
    data = response.json()
    return data


print(get_data())