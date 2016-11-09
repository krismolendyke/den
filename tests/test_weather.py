#!/usr/bin/env python

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=missing-docstring

import os
import types
import unittest

import forecastio
import responses
from mock import MagicMock, patch

from . import _reset_environ
_reset_environ()
from den import weather


class WeatherTestCase(unittest.TestCase):
    def test_missing_env_variable_raises_key_error(self):
        with patch.dict("os.environ", {}):
            del os.environ["DEN_FORECAST_IO_API_KEY"]
            with self.assertRaisesRegexp(KeyError, r"Please set the environment variable 'DEN_FORECAST_IO_API_KEY'."):
                try:
                    reload(weather)
                except NameError:
                    import importlib
                    importlib.reload(weather)

            _reset_environ()
            del os.environ["DEN_LAT"]
            with self.assertRaisesRegexp(KeyError, r"Please set the environment variable 'DEN_LAT'."):
                try:
                    reload(weather)
                except NameError:
                    import importlib
                    importlib.reload(weather)

            _reset_environ()
            del os.environ["DEN_LON"]
            with self.assertRaisesRegexp(KeyError, r"Please set the environment variable 'DEN_LON'."):
                try:
                    reload(weather)
                except NameError:
                    import importlib
                    importlib.reload(weather)

    def test_lat_lon_are_floats(self):
        try:
            self.assertIsInstance(weather.LAT, types.FloatType)
        except AttributeError:
            self.assertIsInstance(weather.LAT, float)
        try:
            self.assertIsInstance(weather.LON, types.FloatType)
        except AttributeError:
            self.assertIsInstance(weather.LON, float)

    def test_get_current_data(self):
        with patch("forecastio.api.get_forecast") as get_forecast_patch:
            get_forecast = get_forecast_patch.return_value
            data = {"k0": "v0", "k2": "v2", "k1": "v1", "k3": "v3"}
            get_forecast.currently.return_value = forecastio.models.ForecastioDataPoint(data)

            actual = weather.get_current_data()
            try:
                self.assertIsInstance(actual, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual, list)

            actual_columns = actual[0]["columns"]
            try:
                self.assertIsInstance(actual_columns, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual_columns, list)

            actual_points = actual[0]["points"]
            try:
                self.assertIsInstance(actual_points, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual_points, list)

            actual_values = actual_points[0]
            try:
                self.assertIsInstance(actual_values, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual_values, list)

    def test_record_writes_points_for_valid_responses(self):
        with patch("forecastio.api.get_forecast") as get_forecast_patch, \
             patch("den.weather.influxdb.InfluxDBClient") as db_patch:
            get_forecast = get_forecast_patch.return_value
            data = {"k0": "v0", "k2": "v2", "k1": "v1", "k3": "v3"}
            get_forecast.currently.return_value = forecastio.models.ForecastioDataPoint(data)
            db = db_patch.return_value
            db.write_points = MagicMock()
            self.assertIsNone(weather.record("den_test", port=8087, ssl=True))
            self.assertTrue(get_forecast.currently.called)
            self.assertTrue(db.write_points.called)


if __name__ == "__main__":
    unittest.main(verbosity=2)
