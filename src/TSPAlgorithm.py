from abc import ABC, abstractmethod


class TSPAlgorithm(ABC):
    @abstractmethod
    def create_graph(self, points):
        pass

    @abstractmethod
    def solve(self, graph):
        pass
