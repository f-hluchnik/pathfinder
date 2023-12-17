import errno
import os
import re
import xml.etree.ElementTree as ElementTree
from os.path import exists as file_exists
from typing import List, Tuple


class App:

    # noinspection PyMethodMayBeStatic
    def load_gpx(self, file_name: str) -> List[Tuple[str, str]]:
        """
        Loads the input file and parses the xml. It returns a list of points (a list of tuples).

        Args:
            file_name: name of the file containing the GPS coordinates

        Returns:
            list of the locations from the GPX file
        """
        locations = list()
        if file_exists(file_name):
            tree = ElementTree.parse(file_name)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_name)
        root = tree.getroot()
        for child in root:
            locations.append((child.attrib["lat"], child.attrib["lon"]))
        return locations

    # noinspection PyMethodMayBeStatic
    def prepare_resulting_points(self, computed_points, initial_points) -> List:
        """
        Prepares a list of the resulting points.
        """
        result_points = list()
        for i in computed_points:
            point = [float(initial_points[i][1]), float(initial_points[i][0])]
            result_points.append(point)
        return result_points

    # noinspection PyMethodMayBeStatic
    def write_result(self, res_gpx: str, resulting_points: List, output_dir: str = 'output/result.gpx') -> None:
        """
        Writes the result in the output gpx file. It appends the initial waypoints to the resulting gpx file.
        """
        res_gpx = re.sub(r'</gpx>$', '', res_gpx)
        for point in resulting_points[:-1]:
            wpt_prep = '<wpt lat="{lat}" lon="{lon}"></wpt>'
            wpt = wpt_prep.format(lat=point[1], lon=point[0])
            res_gpx += wpt
        res_gpx += "</gpx>"
        with open(output_dir, 'w') as file:
            file.write(res_gpx)
