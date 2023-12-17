import unittest
from src.App import App


class TestPrepareResultingPoints(unittest.TestCase):

    def test_prepare_resulting_points(self):
        app = App()
        res = {'points': [0, 3, 2, 1], 'distance': 5}
        points = [("16.60", "49.20"), ("16.59", "49.21"), ("16.58", "49.22"), ("16.57", "49.23")]
        result_points = app.prepare_resulting_points(res, points)
        self.assertEqual(len(result_points), len(points))
        self.assertEqual(type(result_points[0][0]), float)
        self.assertEqual(type(result_points[0][1]), float)
        self.assertEqual(result_points[0][0], float(points[0][1]))
        self.assertEqual(result_points[0][1], float(points[0][0]))
        self.assertEqual(result_points[0], [49.20, 16.60])
        self.assertEqual(result_points[1], [49.23, 16.57])
        self.assertEqual(result_points[2], [49.22, 16.58])
        self.assertEqual(result_points[3], [49.21, 16.59])


if __name__ == '__main__':
    unittest.main()
