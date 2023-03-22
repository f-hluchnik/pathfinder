import xml.etree.ElementTree as ET
import os, re

class App:
    def load_xml(self, file_name):
        """
        load_xml ... Function loads the input file and parses the xml. It returns
            a list of points (a list of tuples).
        """
        locations = list()
        tree = ET.parse(file_name)
        root = tree.getroot()
        for child in root:
            locations.append((child.attrib["lat"], child.attrib["lon"]))
        return locations

    def prepare_resulting_points(self, res, points):
        """
        prepare_resulting_points ... Function prepares a list of the resulting points.
        """
        result_points = list()
        for i in res['points']:
            point = [float(points[i][1]), float(points[i][0])]
            result_points.append(point)
        return result_points

    def write_result(self, res_gpx, resulting_points):
        """
        write_result ... Function writes the result in the output gpx file.
            It appends the initial waypoints to the resulting gpx file.
        """
        res_gpx = re.sub(r'</gpx>$', '', res_gpx)
        for point in resulting_points[:-1]:
            wpt_prep = '<wpt lat="{lat}" lon="{lon}"></wpt>'
            wpt = wpt_prep.format(lat=point[1], lon=point[0])
            res_gpx += wpt
        res_gpx += "</gpx>"
        with open('output/result.gpx', 'w') as file:
            file.write(res_gpx)
