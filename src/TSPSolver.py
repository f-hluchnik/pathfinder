import itertools
import os

import networkx as nx
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Tuple, List, Dict

from src.DistanceAPIClient import DistanceAPIClient


class TSPSolver(QObject):
    graph_progress_signal = pyqtSignal(str, list)

    def __init__(self) -> None:
        super().__init__()
        self.tsp_solver = None
        self.distance_api = DistanceAPIClient(os.getenv("API_KEY"), 'foot-walking')
        self.graph = nx.Graph()
        self.method = 'brute_force'
        self.starting_point = 0

    def create_graph(self, points) -> None:
        """
        Creates a weighted graph from given set of points.
        """
        for i, point in enumerate(points):
            self.graph.add_node(i, pos=point)
        distances = {}
        for u, v in itertools.combinations(self.graph.nodes(), 2):
            weight, points = self.set_weight(u, v, distances)
            txt = "The distance from node {} to node {} is {}."
            message = txt.format(u, v, weight)
            self.graph_progress_signal.emit(message, points)
            self.graph.add_edge(u, v, weight=weight)

    def set_weight(self, u, v, distances) -> Tuple[float, List]:
        """
        Sets the weight for an edge between nodes 'u' and 'v' based on distances.
        Args:
            u: The source node.
            v: The target node.
            distances: A dictionary storing distances between nodes.

        Returns:
            A tuple containing the weight of the edge and the list of geographical coordinates for visualization.
        """
        ux, uy, vx, vy = 0, 0, 0, 0
        if (u, v) in distances:
            weight = distances[(u, v)]
        else:
            ux = self.graph.nodes[u]['pos'][0]
            uy = self.graph.nodes[u]['pos'][1]
            vx = self.graph.nodes[v]['pos'][0]
            vy = self.graph.nodes[v]['pos'][1]
            weight = self.distance_api.get_distance(ux, uy, vx, vy)
            distances[(u, v)] = weight
            distances[(v, u)] = weight
        points = [[float(ux), float(uy)], [float(vx), float(vy)]]
        return weight, points

    def create_result_path(self, resulting_points) -> str:
        res_gpx = self.distance_api.generate_result_path(resulting_points)
        return res_gpx

    def solve_tsp(self) -> Dict:
        match self.method:
            case 'nearest_neighbour':
                from src.NearestNeighbourTSPSolver import NearestNeighbourTSPSolver
                self.tsp_solver = NearestNeighbourTSPSolver(self.starting_point)
            case 'brute_force':
                from src.BruteForceTSPSolver import BruteForceTSPSolver
                self.tsp_solver = BruteForceTSPSolver()
            case _:
                self.solve(tsp_solver=self.tsp_solver)
        return self.tsp_solver.solve(self)

    def solve(self, tsp_solver) -> Dict:
        return {'points': [], 'distance': 0}

    def set_method(self, method):
        self.method = method

    def set_starting_point(self, starting_point):
        self.starting_point = starting_point
