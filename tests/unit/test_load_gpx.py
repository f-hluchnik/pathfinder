import unittest
from src.App import App


class TestLoadGpx(unittest.TestCase):

    def test_load_gpx(self):
        app = App()
        file_path = "../test_input/test_export.gpx"
        locations = app.load_gpx(file_path)
        self.assertEqual(len(locations), 2)
        self.assertEqual(locations[0], ("49.20", "16.60"))
        self.assertEqual(locations[1], ("49.21", "16.59"))

    def test_file_not_exists(self):
        app = App()
        file_path = "../test_input/non_existent.gpx"
        with self.assertRaises(FileNotFoundError):
            locations = app.load_gpx(file_path)


if __name__ == '__main__':
    unittest.main()
