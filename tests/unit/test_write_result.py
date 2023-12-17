import unittest, os
from src.App import App


class TestWriteResult(unittest.TestCase):

    def test_write_result(self):
        app = App()
        res_gpx = "<gpx></gpx>"
        resulting_points = [[49.2, 16.6], [49.23, 16.57], [49.22, 16.58], [49.21, 16.59], [49.2, 16.6]]
        app.write_result(res_gpx, resulting_points, "../test_output/test_result.gpx")
        self.assertTrue(os.path.exists("../test_output/test_result.gpx"))
        with open("../test_output/test_result.gpx", "r") as file:
            content = file.read()
        expected_content = "<gpx><wpt lat=\"16.6\" lon=\"49.2\"></wpt><wpt lat=\"16.57\" lon=\"49.23\"></wpt><wpt lat=\"16.58\" lon=\"49.22\"></wpt><wpt lat=\"16.59\" lon=\"49.21\"></wpt></gpx>"
        self.assertEqual(content, expected_content)


if __name__ == '__main__':
    unittest.main()
