from utils.Method import Method
from threading import Thread
from utils.BruteForceTSPSolver import BruteForceBaseTSPSolver
from utils.NearestNeighbourTSPSolver import NearestNeighbourTSPSolver
from utils.BaseTSPSolver import BaseTSPSolver
from utils.FileUtils import read_gpx_points
from utils.utils import prepare_resulting_points

import logging
from asyncio.log import logger

logging.basicConfig(level=logging.INFO)


class PathfinderApp:

    def __init__(self):
        self.method = Method.BRUTE_FORCE
        self.starting_point = 0
        self.tsp_solver = None
        self.set_solver_instance()
        self.input_points = read_gpx_points()
        self.resulting_points = None
        self.points = None
        self.distance = 0

    def set_method(self, method: str) -> None:
        try:
            self.method = Method[method.upper().replace(" ", "_")]
            logger.info(self.method)
        except KeyError:
            raise ValueError('Invalid method: {}'.format(method))
        self.set_solver_instance()

    def set_solver_instance(self) -> None:
        match self.method:
            case Method.BRUTE_FORCE:
                self.tsp_solver = BruteForceBaseTSPSolver()
            case Method.NEAREST_NEIGHBOUR:
                self.tsp_solver = NearestNeighbourTSPSolver()
            case _:
                self.tsp_solver = BruteForceBaseTSPSolver()

    def set_starting_point(self, starting_point: int) -> None:
        self.starting_point = starting_point

    def compute(self) -> float:
        """
        Does all the computations (creating weighted graph and finding the shortest path) and plots the result.
        """
        self.tsp_solver.set_method(self.method)
        self.tsp_solver.set_starting_point(self.starting_point)
        logger.info("Creating weighted graph...")
        if self.tsp_solver.graph.number_of_nodes() == 0:
            self.tsp_solver.create_graph(self.input_points)
        result = self.tsp_solver.solve()
        self.prepare_points(result["points"])
        res_distance = round(result["distance"] / 1000, 2)
        self.distance = res_distance
        logger.info("DONE! You can find the result in output/result.gpx.")
        return res_distance

    def compute_thread(self) -> None:
        """
        Creates and starts a new thread to execute the 'compute' method.

        This method is designed to run the 'compute' method in a separate thread. The
        created thread is set as a daemon, meaning it will exit when the main program
        exits.
        """
        thread1 = Thread(target=self.compute)
        thread1.daemon = True
        thread1.start()

    def prepare_points(self, resulting_points) -> None:
        """
        Prepares and processes resulting points from the computation.
        Args:
            resulting_points: The points obtained from a computation.
        """
        logger.info("Preparing result...")
        self.resulting_points = prepare_resulting_points(resulting_points, self.input_points)
        res_gpx = self.tsp_solver.create_result_path(self.resulting_points)
        # self.app.write_result(res_gpx, self.resulting_points)
        self.points = [(float(sublist[1]), float(sublist[0])) for sublist in self.resulting_points]
