from typing import List


def prepare_resulting_points(computed_points, initial_points) -> List:
    """
    Prepares a list of the resulting points.
    """
    result_points = list()
    for i in computed_points:
        point = [float(initial_points[i][1]), float(initial_points[i][0])]
        result_points.append(point)
    return result_points
