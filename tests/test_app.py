import json
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_charts_and_controls(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.get("plotly_chart")), 4)
        initial = json.loads(app.get("plotly_chart")[3].proto.spec)
        self.assertIn("Close Shave", initial["data"][0]["customdata"][0][0])
        app.slider(key="rating_floor").set_value(150).run()
        self.assertEqual(len(app.exception), 0)
        changed = json.loads(app.get("plotly_chart")[3].proto.spec)
        self.assertIn("Schindler", changed["data"][0]["customdata"][0][0])
        self.assertNotEqual(initial, changed)
        app.radio(key="genre_measure").set_value("Share of movies").run()
        self.assertEqual(len(app.exception), 0)
        distribution = json.loads(app.get("plotly_chart")[0].proto.spec)
        self.assertIn("%", distribution["data"][0]["text"][0])
        self.assertEqual(json.loads(app.get("plotly_chart")[3].proto.spec), changed)


if __name__ == "__main__":
    unittest.main()
