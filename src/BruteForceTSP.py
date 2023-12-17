import itertools, os, time
import networkx as nx
from src.DistanceAPIClient import DistanceAPIClient
from PyQt5.QtCore import QObject, pyqtSignal

from typing import Tuple, List, Dict

from src.TSPSolver import TSPSolver


class BruteForceTSP(QObject, TSPSolver):
    graph_progress_signal = pyqtSignal(str, list)

    def __init__(self) -> None:
        super().__init__()
        self.distance_api = DistanceAPIClient(os.getenv("API_KEY"), 'foot-walking')
        self.graph = nx.Graph()

    # def create_graph(self, points) -> None:
    #     """
    #     Creates a weighted graph from given set of points.
    #     """
    #     for i, point in enumerate(points):
    #         self.graph.add_node(i, pos=point)
    #     distances = {}
    #     for u, v in itertools.combinations(self.graph.nodes(), 2):
    #         weight, points = self.set_weight(u, v, distances)
    #         txt = "The distance from node {} to node {} is {}."
    #         message = txt.format(u, v, weight)
    #         self.graph_progress_signal.emit(message, points)
    #         self.graph.add_edge(u, v, weight=weight)

    # def set_weight(self, u, v, distances) -> Tuple[float, List]:
    #     if (u, v) in distances:
    #         weight = distances[(u, v)]
    #     else:
    #         ux = self.graph.nodes[u]['pos'][0]
    #         uy = self.graph.nodes[u]['pos'][1]
    #         vx = self.graph.nodes[v]['pos'][0]
    #         vy = self.graph.nodes[v]['pos'][1]
    #         weight = self.distance_api.get_distance(ux, uy, vx, vy)
    #         distances[(u, v)] = weight
    #         distances[(v, u)] = weight
    #     points = [[float(ux), float(uy)], [float(vx), float(vy)]]
    #     return weight, points

    def brute_force_tsp(self) -> Dict:
        """
        Solves the traveling salesman problem for given weighted graph using the brute force method.
        """
        # Generate all possible permutations of node indices
        nodes_count = self.graph.number_of_nodes()
        node_indices = range(nodes_count)
        all_permutations = itertools.permutations(node_indices)

        # Find permutation with minimum total weight
        min_weight = float('inf')
        min_permutation = None
        for permutation in all_permutations:
            weight = sum(
                self.graph[permutation[i]][permutation[(i + 1) % nodes_count]]['weight'] for i in range(nodes_count))
            if weight < min_weight:
                min_weight = weight
                min_permutation = permutation
                self.graph_progress_signal.emit("...", list(permutation))
                time.sleep(0.1)
        # Convert permutation to Hamiltonian circuit
        hamiltonian_circuit = list(min_permutation)
        hamiltonian_circuit.append(min_permutation[0])

        return {'points': hamiltonian_circuit, 'distance': min_weight}

    def create_result_path(self, resulting_points) -> str:
        res_gpx = self.distance_api.generate_result_path(resulting_points)
        return res_gpx
