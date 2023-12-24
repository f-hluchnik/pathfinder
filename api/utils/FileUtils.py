import gpxpy
import json


class FileUtils:

    def __init__(self):
        self.content = ''


def parse_gpx_file(file) -> None:
    locations = list()
    gpx = gpxpy.parse(file)

    # Extract locations from the GPX data
    for waypoint in gpx.waypoints:
        locations.append((waypoint.latitude, waypoint.longitude))
    save(locations)


def save(data):
    with open('./tmp/data.json', 'w') as f:
        json.dump(data, f)


def read_gpx_points() -> str:
    with open('./tmp/data.json', 'r') as f:
        loaded_data = json.load(f)
    return loaded_data
