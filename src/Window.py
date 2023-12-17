import os
import random
from threading import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from dotenv import load_dotenv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Dict

import logging
from asyncio.log import logger
logging.basicConfig(level=logging.INFO)
from src.App import App
from src.TSPSolver import TSPSolver


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.stylesheet = None
        load_dotenv()

        self.setWindowTitle("Pathfinder")
        self.setGeometry(100, 200, 1000, 600)
        self.setWindowIcon(QIcon('media/icon.png'))
        self.load_stylesheet()
        self.method = 'brute_force'
        self.selected_starting_point = 0
        self.ui_components()
        self.tsp_solver = TSPSolver()
        self.input_points = None
        self.resulting_points = None
        self.points = None
        self.root_points = None
        self.a = tuple(random.random() for _ in range(7))
        self.b = tuple(random.random() for _ in range(7))
        self.plot()

        if os.getenv("API_KEY") is None:
            self.gpx_label.setText(
                "API_KEY not found. Please check if the .env file exists and the API_KEY variable is set to valid key "
                "to OpenRouteService API.")
            self.button_load_file.setEnabled(False)
        else:
            self.app = App()

    def load_stylesheet(self) -> None:
        """
        Loads and applies a stylesheet for styling the graphical user interface.
        """
        with open('styles/styles.qss', 'r') as f:
            self.stylesheet = f.read()
        self.setStyleSheet(self.stylesheet)

    def ui_components(self) -> None:
        """
        Sets up the user interface components for the application.

        This method initializes and configures various graphical user interface components,
        including labels, buttons, a dropdown menu, and a canvas for displaying graphs.
        """
        title_label = QLabel(
            "Begin with importing the gpx file.\nIf the program stops while creating the graph, don't panic.\nThe API has requests per minute limit, so we are just waiting 60 seconds to renew the limit.",
            self)
        title_label.setGeometry(10, 10, 600, 40)

        self.gpx_label = QLabel("", self)
        self.gpx_label.setGeometry(10, 30, 600, 40)

        self.method_label = QLabel(
            "Choose the computing method. In case of the nearest neighbour method, you can choose also the starting point.",
            self)
        self.method_label.setGeometry(10, 50, 600, 40)

        toolbar = QButtonGroup(self)
        self.method_brute_force = QRadioButton('brute force', self)
        self.method_brute_force.setChecked(True)
        self.method_brute_force.clicked.connect(self.set_method_to_brute_force)

        self.method_nearest_neighbour = QRadioButton('nearest neighbour', self)
        self.method_nearest_neighbour.setCheckable(True)
        self.method_nearest_neighbour.clicked.connect(self.set_method_to_nearest_neighbour)

        toolbar.addButton(self.method_brute_force)
        toolbar.addButton(self.method_nearest_neighbour)

        self.dropdown_menu = QComboBox(self)
        self.dropdown_menu.setFixedWidth(80)
        self.dropdown_menu.addItem('random')
        self.dropdown_menu.setEnabled(False)
        self.dropdown_menu.currentIndexChanged.connect(self.selection_changed)

        self.button_load_file = QPushButton("load gpx", self)
        self.button_load_file.setGeometry(10, 70, 80, 40)
        self.button_load_file.setStyleSheet(self.stylesheet)
        self.button_load_file.setCursor(QCursor(Qt.PointingHandCursor))
        self.button_load_file.clicked.connect(self.load_file)

        self.button_compute = QPushButton("compute", self)
        self.button_compute.setEnabled(False)
        self.button_compute.setGeometry(10, 150, 80, 40)
        self.button_compute.setStyleSheet(self.stylesheet)
        self.button_compute.setCursor(QCursor(Qt.PointingHandCursor))
        self.button_compute.clicked.connect(self.compute_thread)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.move(0, 0)
        self.ax = self.figure.add_subplot(111)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(title_label)
        layout.addWidget(self.gpx_label)
        layout.addWidget(self.method_label)
        layout.addWidget(self.method_brute_force)
        layout.addWidget(self.method_nearest_neighbour)
        layout.addWidget(self.dropdown_menu)
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_load_file)
        layout_buttons.addWidget(self.button_compute)
        layout_buttons.addStretch()
        layout.addLayout(layout_buttons)
        layout.addWidget(self.canvas)
        self.setCentralWidget(central_widget)

    def set_method_to_brute_force(self) -> None:
        """
        Sets the method for computation to the brute force algorithm.
        """
        self.method_nearest_neighbour.setChecked(False)
        self.dropdown_menu.setEnabled(False)
        self.method = 'brute_force'

    def set_method_to_nearest_neighbour(self) -> None:
        """
        Sets the method for computation to the nearest neighbor algorithm.
        """
        self.method_brute_force.setChecked(False)
        self.dropdown_menu.setEnabled(True)
        self.method = 'nearest_neighbour'

    def populate_dropdown_menu(self) -> None:
        """
        Populates the dropdown menu with items based on the input points.

        This method adds items to the dropdown menu, each representing a body (bod)
        and its corresponding index. The items are labeled as 'bod 1', 'bod 2', etc.,
        based on the index of the input points.
        """
        if len(self.input_points) > 0:
            for i in range(0, len(self.input_points)):
                self.dropdown_menu.addItem('bod ' + str(i + 1))

    def selection_changed(self) -> None:
        """
        Handles the event when the selection in the dropdown menu changes.

        This method is called when the user selects a different item in the dropdown menu.
        It updates the 'selected_starting_point' attribute with the index of the currently
        selected item in the dropdown menu.
        """
        self.selected_starting_point = self.dropdown_menu.currentIndex()

    def load_file(self) -> None:
        """
        Function loads gpx file, parses it and stores the GPS points.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "./input", ".gpx Files (*.gpx);;All Files (*)")
        if file_name and os.path.isfile(file_name):
            self.tsp_solver.graph.clear()
            self.input_points = self.app.load_gpx(file_name)
            self.populate_dropdown_menu()
            # text = ",\n".join("(%s,%s)" % tup for tup in self.input_points)
            self.gpx_label.setText(f"You have loaded {len(self.input_points)} points.")
            x_points, y_points = zip(*self.input_points)
            self.points = list(zip(map(float, x_points), map(float, y_points)))
            self.root_points = self.points[:]
            self.a, self.b = zip(*self.root_points)
            self.plot()
            self.button_compute.setEnabled(True)

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

    def update_graph_progress(self, progress, points) -> None:
        """
        Updates the graph progress and visualizes the corresponding points.

        Args:
            progress: The progress information to be displayed.
            points: The list of points to be used for updating the graph.
        """
        self.points = points
        self.plot()
        self.gpx_label.setText(progress)

    def update_path_progress(self, progress, points) -> None:
        """
        Updates the path progress based on the given points.

        Args:
            points: A list of points representing the path progress.
        """
        x, y = zip(*self.app.prepare_resulting_points(points, self.input_points))
        self.points = zip(y, x)
        self.plot()

    def compute(self) -> None:
        """
        Does all the computations (creating weighted graph and finding the shortest path) and plots the result.
        """
        self.disable_buttons()
        self.tsp_solver.set_method(self.method)
        self.tsp_solver.set_starting_point(self.selected_starting_point)
        logger.info("Creating weighted graph...")
        if self.tsp_solver.graph.number_of_nodes() == 0:
            self.create_graph()
        result = self.solve_tsp()
        self.prepare_points(result["points"])
        self.plot()
        res_distance = round(result["distance"] / 1000, 2)
        self.gpx_label.setText(
            f"This is the optimal path through the given points.\nDistance traveled is {res_distance} km. You can find the real path in output/result.gpx.")
        self.enable_buttons()
        logger.info("DONE! You can find the result in output/result.gpx.")

    def disable_buttons(self) -> None:
        self.button_compute.setEnabled(False)
        self.button_load_file.setEnabled(False)

    def enable_buttons(self) -> None:
        self.button_load_file.setEnabled(True)
        self.button_compute.setEnabled(True)

    def create_graph(self) -> None:
        """
        Creates a graph based on the input points using the configured TSP solver.
        """
        self.tsp_solver.graph_progress_signal.connect(self.update_graph_progress)
        self.tsp_solver.create_graph(self.input_points)
        self.tsp_solver.graph_progress_signal.disconnect(self.update_graph_progress)

    def solve_tsp(self) -> Dict:
        """
        Solves the Traveling Salesman Problem (TSP) using the configured TSP solver.

        Returns:
            Dict: A dictionary containing information about the TSP solution.
        """
        logger.info("Solving the TSP...")
        self.tsp_solver.graph_progress_signal.connect(self.update_path_progress)
        result = self.tsp_solver.solve_tsp()
        self.tsp_solver.graph_progress_signal.disconnect(self.update_path_progress)
        return result

    def prepare_points(self, resulting_points) -> None:
        """
        Prepares and processes resulting points from the computation.
        Args:
            resulting_points: The points obtained from a computation.
        """
        logger.info("Preparing result...")
        self.resulting_points = self.app.prepare_resulting_points(resulting_points, self.input_points)
        res_gpx = self.tsp_solver.create_result_path(self.resulting_points)
        self.app.write_result(res_gpx, self.resulting_points)
        self.points = [(float(sublist[1]), float(sublist[0])) for sublist in self.resulting_points]

    def plot(self) -> None:
        """
        Plots the graph.
        """
        if self.points is not None:
            x, y = zip(*self.points)
            self.ax.cla()
            self.ax.set_xlim([min(self.a) - 0.008, max(self.a) + 0.008])
            self.ax.set_ylim([min(self.b) - 0.008, max(self.b) + 0.008])
            self.ax.plot(self.a, self.b, 'ko', ms=10)
            self.ax.plot(x, y, 'go-', ms=15)
            for i in range(0, len(self.a)):
                label = str(i + 1)
                x, y = self.a[i], self.b[i]
                self.ax.annotate(label, xy=(x, y), xytext=(self.a[i] - 0.00025, self.b[i] - 0.0015), color='white')
        else:
            self.ax.cla()
            self.ax.set_xlim([min(self.a) - 0.05, max(self.a) + 0.05])
            self.ax.set_ylim([min(self.b) - 0.05, max(self.b) + 0.05])
            self.ax.plot(self.a, self.b, 'ro-', ms=5)
        self.canvas.draw()
