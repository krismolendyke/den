#!/usr/bin/env python

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=missing-docstring

from __future__ import absolute_import
import types
import unittest

import forecastio
import responses
from mock import MagicMock, patch

from den import weather


class WeatherTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {
            "apparentTemperature": 46.93,
            "cloudCover": 0.73,
            "dewPoint": 47.7,
            "humidity": 0.96,
            "icon": "rain",
            "nearestStormDistance": 0,
            "ozone": 328.35,
            "precipIntensity": 0.1685,
            "precipIntensityError": 0.0067,
            "precipProbability": 1,
            "precipType": "rain",
            "pressure": 1009.7,
            "summary": "Rain",
            "temperature": 48.71,
            "time": 1453402675,
            "visibility": 4.3,
            "windBearing": 186,
            "windSpeed": 4.64
        }

    def test_get_weather_points(self):
        with patch("forecastio.api.get_forecast") as get_forecast_patch:
            get_forecast = get_forecast_patch.return_value
            get_forecast.currently.return_value = forecastio.models.ForecastioDataPoint(self.data)

            actual = weather._get_weather_points("KEY", 0.0, 0.0)
            try:
                self.assertIsInstance(actual, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual, list)

            expected_measurement = "weather"
            actual_measurement = actual[0]["measurement"]
            self.assertEqual(expected_measurement, actual_measurement)

            actual_tags = actual[0]["tags"]
            try:
                self.assertIsInstance(actual_tags, types.DictType)
            except AttributeError:
                self.assertIsInstance(actual_tags, dict)
            self.assertNotIn("summary", actual_tags.keys())

            actual_fields = actual[0]["fields"]
            try:
                self.assertIsInstance(actual_fields, types.DictType)
            except AttributeError:
                self.assertIsInstance(actual_fields, dict)

    def test_record_writes_points_for_valid_responses(self):
        with patch("forecastio.api.get_forecast") as get_forecast_patch, \
             patch("den.weather.influxdb.InfluxDBClient") as db_patch:
            get_forecast = get_forecast_patch.return_value
            get_forecast.currently.return_value = forecastio.models.ForecastioDataPoint(self.data)
            db = db_patch.return_value
            db.write_points = MagicMock()
            self.assertIsNone(weather.record("den_test", 8087, True, "KEY", 0.0, 0.0))
            self.assertEqual(1, get_forecast_patch.call_count)
            db_patch.assert_called_once_with(database="den_test", port=8087, ssl=True)
            db.write_points.assert_called_once_with(weather._get_weather_points("KEY", 0.0, 0.0), time_precision="s")


if __name__ == "__main__":
    unittest.main(verbosity=2)
