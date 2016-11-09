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
    def test_get_current_data(self):
        with patch("forecastio.api.get_forecast") as get_forecast_patch:
            get_forecast = get_forecast_patch.return_value
            data = {"k0": "v0", "k2": "v2", "k1": "v1", "k3": "v3"}
            get_forecast.currently.return_value = forecastio.models.ForecastioDataPoint(data)

            actual = weather.get_current_data("KEY", 0.0, 0.0)
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
            self.assertIsNone(weather.record("den_test", 8087, True, "KEY", 0.0, 0.0))
            self.assertTrue(get_forecast.currently.called)
            self.assertTrue(db.write_points.called)


if __name__ == "__main__":
    unittest.main(verbosity=2)
