import json
import random
from typing import Dict

import requests
import time
from requests import Response
import logging

logger = logging.getLogger('asyncio')


class DistanceAPIClient:

    def __init__(self, api_key: str, profile) -> None:
        self.profile = profile
        self.api_key = api_key

    def get_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        """
        Contacts the openrouteservice API and returns the distance between two points.
        """
        req_url_prep = 'https://api.openrouteservice.org/v2/directions/{profile}?api_key={key}&start={start_lon},{start_lat}&end={end_lon},{end_lat}' # NOQA E501
        req_url = req_url_prep.format(
            profile=self.profile,
            key=self.api_key,
            start_lat=lat1,
            start_lon=lon1,
            end_lat=lat2,
            end_lon=lon2)
        response = self.make_request(req_url)
        path = json.loads(response.text)
        if 'features' in path:
            return path['features'][0]['properties']['segments'][0]['distance']
        else:
            time.sleep(60)
            response = self.make_request(req_url)
            path = json.loads(response.text)
            if 'features' in path:
                return path['features'][0]['properties']['segments'][0]['distance']
            else:
                logger.info(response.text)
                raise SystemExit()

    # noinspection PyMethodMayBeStatic
    def make_request(self, req_url: str) -> Response:
        """
        Sends an HTTP GET request to the specified URL and returns the response.
        Args:
            req_url: The URL to which the GET request is made.

        Returns:
            response: An object representing the HTTP response.
        """
        response = Response()
        try:
            response = requests.get(req_url)
        except requests.exceptions.RequestException as e:
            logger.info(response.text)
            raise SystemExit(e)
        return response

    # noinspection PyMethodMayBeStatic
    def get_random_distance(self) -> int:
        """
        Returns:
            Random distance between two points. Mainly for testing purposes.
        """
        return random.randrange(1, 100, 1)

    def generate_result_path(self, points: Dict) -> str:
        """
        Contacts the openrouteservice API and returns the route through given list of points.
        """
        headers = {
            'Authorization': self.api_key
        }
        data = {
            "coordinates": points,
            "instructions": "false"
        }
        req_url_prep = 'https://api.openrouteservice.org/v2/directions/{profile}/gpx'
        req_url = req_url_prep.format(profile=self.profile)
        response = requests.post(req_url, headers=headers, json=data)
        return response.text
