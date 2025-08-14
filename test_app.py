import unittest
from unittest.mock import patch
import app

class TestWeather(unittest.TestCase):
    @patch("app.requests.get")
    def test_get_weather_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "weather": [{"description": "clear sky"}],
            "main": {"temp": 20, "humidity": 50}
        }
        mock_get.return_value.raise_for_status = lambda: None
        # This is GUI-driven, so we mainly check no exceptions.
        try:
            app.result_lbl = type("", (), {"config": lambda *a, **k: None})()
            app.city_entry = type("", (), {"get": lambda: "London"})()
            app.get_weather()
        except Exception as e:
            self.fail(f"get_weather raised {e}")
