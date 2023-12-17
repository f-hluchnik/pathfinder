import itertools, os, time
from src.TSPSolver import TSPSolver
from src.TSPAlgorithm import TSPAlgorithm

from typing import Dict


class TSPMeta(type(TSPSolver), type(TSPAlgorithm)):
    pass


class BruteForceTSPSolver(TSPSolver, TSPAlgorithm, metaclass=TSPMeta):

    def create_graph(self, points) -> None:
        return super().create_graph(points)

    def solve(self, tsp_solver: TSPSolver) -> Dict:
        """
        Solves the traveling salesman problem for given weighted graph using the brute force method.
        """
        # Generate all possible permutations of node indices
        nodes_count = tsp_solver.graph.number_of_nodes()
        node_indices = range(nodes_count)
        all_permutations = itertools.permutations(node_indices)

        # Find permutation with minimum total weight
        min_weight = float('inf')
        min_permutation = None
        for permutation in all_permutations:
            weight = sum(tsp_solver.graph[permutation[i]][permutation[(i + 1) % nodes_count]]['weight'] for i in
                         range(nodes_count))
            if weight < min_weight:
                min_weight = weight
                min_permutation = permutation
                tsp_solver.graph_progress_signal.emit("...", list(permutation))
                time.sleep(0.1)

        # Convert permutation to Hamiltonian circuit
        hamiltonian_circuit = list(min_permutation)
        hamiltonian_circuit.append(min_permutation[0])

        return {'points': hamiltonian_circuit, 'distance': min_weight}
