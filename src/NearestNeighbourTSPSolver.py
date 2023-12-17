import sys, time
from random import randrange
from src.TSPSolver import TSPSolver
from src.TSPAlgorithm import TSPAlgorithm

from typing import Dict


class TSPMeta(type(TSPSolver), type(TSPAlgorithm)):
    pass


class NearestNeighbourTSPSolver(TSPSolver, TSPAlgorithm, metaclass=TSPMeta):

    def __init__(self, starting_point) -> None:
        self.starting_point = starting_point

    def create_graph(self, points) -> None:
        return super().create_graph(points)

    def solve(self, tsp_solver: TSPSolver) -> Dict:
        """
        brute_force_tsp ... Function solves the traveling salesman problem for
            given weighted graph using the nearest neighbour method.
        """
        visited = set()
        if self.starting_point == 0:
            start = randrange(0, len(tsp_solver.graph.nodes()) - 1)
        else:
            start = self.starting_point - 1
        visited.add(start)
        path = [start]
        sum_distance = 0

        while len(path) < len(tsp_solver.graph.nodes()):
            nearest_neighbor = None
            nearest_distance = sys.maxsize
            for neighbor in tsp_solver.graph.neighbors(start):
                if neighbor not in visited:
                    distance = tsp_solver.graph.get_edge_data(start, neighbor)["weight"]
                    if distance < nearest_distance:
                        nearest_neighbor = neighbor
                        nearest_distance = distance
            start = nearest_neighbor
            sum_distance += nearest_distance
            visited.add(start)
            path.append(start)
            tsp_solver.graph_progress_signal.emit("...", path)
            time.sleep(0.1)

        path.append(path[0])
        sum_distance += tsp_solver.graph.get_edge_data(path[-2], path[-1])["weight"]
        return {'points': path, 'distance': sum_distance}
