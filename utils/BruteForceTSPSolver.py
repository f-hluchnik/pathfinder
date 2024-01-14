import itertools
import time
from typing import Dict
from .BaseTSPSolver import BaseTSPSolver


class BruteForceBaseTSPSolver(BaseTSPSolver):

    def solve(self) -> Dict:
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
            weight = sum(self.graph[permutation[i]][permutation[(i + 1) % nodes_count]]['weight'] for i in
                         range(nodes_count))
            if weight < min_weight:
                min_weight = weight
                min_permutation = permutation
                # self.graph_progress_signal.emit("...", list(permutation))
                time.sleep(0.1)

        # Convert permutation to Hamiltonian circuit
        hamiltonian_circuit = list(min_permutation)
        hamiltonian_circuit.append(min_permutation[0])

        return {'points': hamiltonian_circuit, 'distance': min_weight}
