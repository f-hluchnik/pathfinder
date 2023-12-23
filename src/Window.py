from src.App import App
from src.TSPSolver import TSPSolver
from src.Method import Method

import os
import random
from threading import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from dotenv import load_dotenv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import Dict, Callable
import qdarkstyle

import logging
from asyncio.log import logger

logging.basicConfig(level=logging.INFO)


class Window(QMainWindow):
    _POINT_NAME_X_OFFSET = - 0.0001
    _POINT_NAME_Y_OFFSET = - 0.0007
    _WINDOW_WIDTH = 1000
    _WINDOW_HEIGHT = 600
    _DEFAULT_STARTING_POINT = 0
    _FIGURE_FACE_COLOUR = (0, 0, 0, 0)
    _PLOT_FACE_COLOUR = (0, 0, 0, 0.2)

    def __init__(self) -> None:
        super().__init__()
        self.stylesheet = None
        self.gpx_label = QLabel()
        self.method_label = QLabel()
        self.method_brute_force = QRadioButton()
        self.method_nearest_neighbour = QRadioButton()
        self.dropdown_menu = QComboBox()
        self.button_load_file = QRadioButton()
        self.button_compute = QRadioButton()
        self.figure = Figure()
        self.canvas = FigureCanvas()
        self.ax = None
        load_dotenv()

        self.setWindowTitle("Pathfinder")
        self.setGeometry(100, 200, self._WINDOW_WIDTH, self._WINDOW_HEIGHT)
        self.setWindowIcon(QIcon('media/icon.png'))
        self.load_stylesheet()
        self.method = Method.BRUTE_FORCE
        self.selected_starting_point = self._DEFAULT_STARTING_POINT
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

        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    def ui_components(self) -> None:
        """
        Sets up the user interface components for the application.

        This method initializes and configures various graphical user interface components,
        including labels, buttons, a dropdown menu, and a canvas for displaying graphs.
        """
        self.create_gpx_label()
        self.create_method_label()
        self.create_radio_buttons()
        self.create_toolbar()
        self.create_dropdown_menu()
        self.create_push_buttons()
        self.create_figure()
        self.create_layout()

    def create_gpx_label(self) -> None:
        self.gpx_label = QLabel("", self)
        self.gpx_label.setGeometry(10, 30, 600, 40)

    def create_method_label(self) -> None:
        self.method_label = QLabel(
            "Choose the computing method."
            "In case of the nearest neighbour method, you can choose also the starting point.",
            self)
        self.method_label.setGeometry(10, 50, 600, 40)

    def create_radio_buttons(self) -> None:
        self.method_brute_force = self.create_radio_button(
            label=Method.BRUTE_FORCE.label(),
            callback=self.set_method_to_brute_force,
            checked=True
        )
        self.method_nearest_neighbour = self.create_radio_button(
            label=Method.NEAREST_NEIGHBOUR.label(),
            callback=self.set_method_to_nearest_neighbour,
            checked=False
        )

    def create_radio_button(self, label: str, callback: Callable, checked: bool) -> QAbstractButton:
        button = QRadioButton(label, self)
        button.setChecked(checked)
        button.clicked.connect(callback)
        return button

    def create_toolbar(self) -> None:
        toolbar = QButtonGroup(self)
        toolbar.addButton(self.method_brute_force)
        toolbar.addButton(self.method_nearest_neighbour)

    def create_dropdown_menu(self) -> None:
        self.dropdown_menu = QComboBox(self)
        self.dropdown_menu.setFixedWidth(80)
        self.dropdown_menu.addItem('random')
        self.dropdown_menu.setEnabled(False)
        self.dropdown_menu.currentIndexChanged.connect(self.selection_changed)

    def create_push_buttons(self) -> None:
        self.button_load_file = self.create_push_button(
            label="load gpx",
            enabled=True,
            geometry=QRect(10, 70, 80, 40),
            cursor_type=Qt.PointingHandCursor,
            callback=self.load_file
        )

        self.button_compute = self.create_push_button(
            label="compute",
            enabled=False,
            geometry=QRect(10, 150, 80, 40),
            cursor_type=Qt.PointingHandCursor,
            callback=self.compute_thread
        )

    def create_push_button(
            self,
            label: str,
            enabled: bool,
            geometry: QRect,
            cursor_type: Qt.CursorShape,
            callback: Callable
    ) -> QAbstractButton:
        button = QPushButton(label, self)
        button.setEnabled(enabled)
        button.setGeometry(geometry)
        self.button_load_file.setCursor(QCursor(cursor_type))
        self.button_load_file.clicked.connect(callback)
        return button

    def create_figure(self) -> None:
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor=self._FIGURE_FACE_COLOUR, edgecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.move(0, 0)
        self.ax = self.figure.add_subplot(111)
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.set_facecolor(self._PLOT_FACE_COLOUR)

    def create_layout(self) -> None:
        title_label = QLabel(
            "Begin with importing the gpx file.\n"
            "If the program stops while creating the graph, don't panic.\n"
            "The API has requests per minute limit, so we are just waiting 60 seconds to renew the limit.",
            self)
        title_label.setGeometry(10, 10, 600, 40)
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
        self.method = Method.BRUTE_FORCE

    def set_method_to_nearest_neighbour(self) -> None:
        """
        Sets the method for computation to the nearest neighbor algorithm.
        """
        self.method_brute_force.setChecked(False)
        if self.dropdown_menu.count() > 1:
            self.dropdown_menu.setEnabled(True)
        self.method = Method.NEAREST_NEIGHBOUR

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
        if self.method == Method.NEAREST_NEIGHBOUR and self.dropdown_menu.count() > 1:
            self.dropdown_menu.setEnabled(True)

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
        self.gpx_label.setText((
                                   "This is the optimal path through the given points.\n"
                                   "Distance traveled is {res_distance} km."
                                   "You can find the real path in output/result.gpx.").format(res_distance=res_distance)
                               )
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
                self.ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(
                        self.a[i] + self._POINT_NAME_X_OFFSET,
                        self.b[i] + self._POINT_NAME_Y_OFFSET),
                    color='white'
                )
        else:
            self.ax.cla()
            self.ax.set_xlim([min(self.a) - 0.05, max(self.a) + 0.05])
            self.ax.set_ylim([min(self.b) - 0.05, max(self.b) + 0.05])
            self.ax.plot(self.a, self.b, 'ro-', ms=5)
        self.canvas.draw()
