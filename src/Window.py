from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.Pathfinder import Pathfinder
from src.DistanceAPIClient import DistanceAPIClient
from src.App import App
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets
import matplotlib.pyplot as plt
import os, random
import sys
from dotenv import load_dotenv

from threading import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        load_dotenv()

        self.setWindowTitle("Pathfinder")
        self.setGeometry(100, 200, 700, 500)
        self.UiComponents()
        self.resulting_points = None
        self.input_points = None
        self.points = None
        self.root_points = None
        self.a = None
        self.b = None

        self.pathfinder = Pathfinder()
        self.distance_api_client = DistanceAPIClient(os.getenv("API_KEY"), 'foot-walking')
        self.app = App()

    def UiComponents(self):
        title_label = QLabel("This is Pathfinder. Start with importing the gpx file.", self)
        title_label.setGeometry(10, 10, 600, 40)

        self.gpx_label = QLabel("", self)
        self.gpx_label.setGeometry(10, 30, 600, 40)

        load_file_button = QPushButton("load gpx", self)
        load_file_button.setGeometry(10, 70, 100, 40)
        load_file_button.clicked.connect(self.load_file)

        self.compute_button = QPushButton("compute", self)
        self.compute_button.setEnabled(False)
        self.compute_button.setGeometry(120, 70, 100, 40)
        self.compute_button.clicked.connect(self.compute_thread)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.move(0, 0)
        self.ax = self.figure.add_subplot(111)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(title_label)
        layout.addWidget(self.gpx_label)
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(load_file_button)
        layout_buttons.addWidget(self.compute_button)
        layout_buttons.addWidget(self.canvas)
        layout.addLayout(layout_buttons)
        self.setCentralWidget(central_widget)


    def plot(self):
        if self.points is not None:
            x, y = zip(*self.points)
            self.ax.cla()
            self.ax.plot(self.a, self.b, 'ko')
            self.ax.plot(x, y, 'ro-')
            self.ax.set_xlim([min(self.a)-0.005, max(self.a)+0.005])
            self.ax.set_ylim([min(self.b)-0.005, max(self.b)+0.005])
            self.canvas.draw()

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "./input", ".gpx Files (*.gpx);;All Files (*)")
        self.input_points = self.app.load_xml(file_name)
        self.compute_button.setEnabled(True)
        text = ",".join("(%s,%s)" % tup for tup in self.input_points)
        xpoints = [float(sublist[0]) for sublist in self.input_points]
        ypoints = [float(sublist[1]) for sublist in self.input_points]
        self.points = zip(xpoints, ypoints)
        self.root_points = zip(xpoints, ypoints)
        self.a, self.b = zip(*self.root_points)
        self.plot()
        self.gpx_label.setText(text)

    def compute_thread(self):
        thread1 = Thread(target=self.compute)
        thread1.start()

    def update_graph_progress(self, progress, points):
        self.points = points
        self.plot()
        self.gpx_label.setText(progress)

    def compute(self):
        print("Creating weighted graph...")
        self.pathfinder.graph_progress_signal.connect(self.update_graph_progress)
        graph = self.pathfinder.create_graph(self.input_points)
        self.pathfinder.graph_progress_signal.disconnect(self.update_graph_progress)
        print("Solving the TSP...")
        result = self.pathfinder.brute_force_tsp(graph)
        print("Preparing result...")
        self.resulting_points = self.app.prepare_resulting_points(result, self.input_points)
        res_gpx = self.distance_api_client.generate_result_path(self.resulting_points)
        self.app.write_result(res_gpx, self.resulting_points)
        ypoints = [float(sublist[0]) for sublist in self.resulting_points]
        xpoints = [float(sublist[1]) for sublist in self.resulting_points]
        self.points = zip(xpoints, ypoints)
        self.plot()
        self.gpx_label.setText("This is the minimal path through the given points.")
        print("DONE! You can find the result in output/result.gpx.")