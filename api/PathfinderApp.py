from Method import Method
from threading import Thread

import logging
from asyncio.log import logger

logging.basicConfig(level=logging.INFO)


class PathfinderApp:

    def __init__(self):
        self.method = Method.BRUTE_FORCE
        self.starting_point = 0

    def set_method(self, method: str) -> None:
        try:
            self.method = Method[method.upper().replace(" ", "_")]
        except KeyError:
            raise ValueError('Invalid method: {}'.format(method))

    def set_starting_point(self, starting_point: int) -> None:
        self.starting_point = starting_point

    def compute(self) -> None:
        """
        Does all the computations (creating weighted graph and finding the shortest path) and plots the result.
        """
        self.tsp_solver.set_method(self.method)
        self.tsp_solver.set_starting_point(self.selected_starting_point)
        logger.info("Creating weighted graph...")
        if self.tsp_solver.graph.number_of_nodes() == 0:
            self.create_graph()
        result = self.solve_tsp()
        self.prepare_points(result["points"])
        self.plot()
        res_distance = round(result["distance"] / 1000, 2)
        self.gpx_label.setText((
                                   "This is the optimal path through the given points.\n"
                                   "Distance traveled is {res_distance} km."
                                   "You can find the real path in output/result.gpx.").format(res_distance=res_distance)
                               )
        self.enable_buttons()
        logger.info("DONE! You can find the result in output/result.gpx.")

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
