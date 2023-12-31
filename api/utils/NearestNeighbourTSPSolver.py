import sys
import time
from random import randrange
from typing import Dict

from .BaseTSPSolver import BaseTSPSolver


class NearestNeighbourTSPSolver(BaseTSPSolver):

    def solve(self) -> Dict:
        """
        nearest_neighbour_tsp ... Function solves the traveling salesman problem for
            given weighted graph using the nearest neighbour method.
        """
        visited = set()
        if self.starting_point == 0:
            start = randrange(0, len(self.graph.nodes()) - 1)
        else:
            start = self.starting_point - 1
        visited.add(start)
        path = [start]
        sum_distance = 0

        while len(path) < len(self.graph.nodes()):
            nearest_neighbour = None
            nearest_distance = sys.maxsize
            for neighbour in self.graph.neighbors(start):
                if neighbour not in visited:
                    distance = self.graph.get_edge_data(start, neighbour)["weight"]
                    if distance < nearest_distance:
                        nearest_neighbour = neighbour
                        nearest_distance = distance
            start = nearest_neighbour
            sum_distance += nearest_distance
            visited.add(start)
            path.append(start)
            # self.graph_progress_signal.emit("...", path)
            time.sleep(0.1)

        path.append(path[0])
        sum_distance += self.graph.get_edge_data(path[-2], path[-1])["weight"]
        return {'points': path, 'distance': sum_distance}
