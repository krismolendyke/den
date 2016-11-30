#!/usr/bin/env python

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=missing-docstring

from __future__ import absolute_import
import json
import os
import types
import unittest

import requests
import responses
from mock import MagicMock, patch

from den import thermostat


class ThermostatTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__), "responses.txt"), "r") as f:
            cls.responses = [l for l in f]

    def test_get_api_url(self):
        expected = "https://developer-api.nest.com?auth=TEST"
        actual = thermostat._get_api_url("TEST")
        self.assertEqual(expected, actual)

        expected = "https://developer-api.nest.com/structures?auth=TEST"
        for path in ["structures", "/structures", "/structures/", "structures/"]:
            self.assertEqual(expected, thermostat._get_api_url("TEST", path))

    @responses.activate
    def test_get_stream(self):
        url = thermostat._get_api_url("TEST")
        responses.add(responses.GET,
                      url,
                      body="".join(self.responses),
                      status=200,
                      content_type="text/event-stream",
                      stream=True,
                      adding_headers={"Accept": "text/event-stream"},
                      match_querystring=True)
        actual = thermostat._get_stream("TEST")
        self.assertIsInstance(actual, requests.Response)
        self.assertEqual(len(self.responses), len(list(actual.iter_lines())))

    def test_is_event(self):
        self.assertTrue(thermostat._is_event("event:"))
        self.assertFalse(thermostat._is_event("event"))
        self.assertFalse(thermostat._is_event("data:"))

    def test_is_data(self):
        self.assertTrue(thermostat._is_data("data:"))
        self.assertFalse(thermostat._is_data("data"))
        self.assertFalse(thermostat._is_data("event:"))

    def test_process_event_returns_none_for_invalid_line(self):
        invalid_lines = ["", ":", "event:", "event: "]
        for line in invalid_lines:
            self.assertIsNone(thermostat._process_event(line))

    def test_process_event_returns_none_for_keep_alive_line(self):
        self.assertIsNone(thermostat._process_event("event: keep-alive"))
        self.assertIsNone(thermostat._process_event("event:keep-alive"))

    def test_process_event_returns_event_for_valid_line(self):
        expected = "Test event"
        actual = thermostat._process_event("event: " + expected)
        self.assertEqual(expected, actual)
        actual = thermostat._process_event("event:" + expected)
        self.assertEqual(expected, actual)

    def test_process_data_returns_none_for_invalid_line(self):
        invalid_lines = ["", ":", "data:", "data: ", "data: not JSON"]
        for line in invalid_lines:
            self.assertIsNone(thermostat._process_data(line))

    def test_process_data_returns_list_for_valid_line(self):
        expected = [{"key": "val"}]
        actual = thermostat._process_data("data: " + json.dumps(expected))
        self.assertEqual(expected, actual)
        actual = thermostat._process_data("data:" + json.dumps(expected))
        self.assertEqual(expected, actual)

    def test_process_returns_none_for_non_data_line(self):
        invalid_lines = ["", ":", "event:", "event: "]
        for line in invalid_lines:
            self.assertIsNone(thermostat._process(line))

    def test_process_returns_none_for_invalid_data_line(self):
        invalid_lines = ["", ":", "data:", "data: ", "data: not JSON"]
        for line in invalid_lines:
            self.assertIsNone(thermostat._process(line))

    def test_process_returns_list_for_valid_data_line(self):
        expected = [{"key": "val"}]
        actual = thermostat._process("data: " + json.dumps(expected))
        self.assertEqual(expected, actual)
        actual = thermostat._process("data:" + json.dumps(expected))
        self.assertEqual(expected, actual)

        for r in self.responses:
            actual = thermostat._process(r)
            if r.startswith("event"):
                self.assertIsNone(actual)
            elif r.startswith("data"):
                try:
                    self.assertIsInstance(actual, types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual, dict)

    def test_get_structure_points_returns_list_for_valid_data(self):
        for r in self.responses:
            result = thermostat._process(r)
            if result:
                actual = thermostat._get_structure_points(result)
                try:
                    self.assertIsInstance(actual, types.ListType)
                except AttributeError:
                    self.assertIsInstance(actual, list)
                self.assertEqual("structure", actual[0]["measurement"])
                try:
                    self.assertIsInstance(actual[0]["tags"], types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["tags"], dict)
                try:
                    self.assertIsInstance(actual[0]["fields"], types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["fields"], dict)

    def test_get_structure_points_away(self):
        data = {"data": {"structures": {"sid0": {"away": "away", "thermostats": ["tid0"]}}}}
        points = thermostat._get_structure_points(data)
        actual = points[0]["fields"]["is_away"]
        self.assertEqual(1, actual)

        data = {"data": {"structures": {"sid0": {"away": "auto-away", "thermostats": ["tid0"]}}}}
        points = thermostat._get_structure_points(data)
        actual = points[0]["fields"]["is_away"]
        self.assertEqual(1, actual)

        data = {"data": {"structures": {"sid0": {"away": "home", "thermostats": ["tid0"]}}}}
        points = thermostat._get_structure_points(data)
        actual = points[0]["fields"]["is_away"]
        self.assertEqual(0, actual)

    def test_get_thermostat_points_returns_list_for_valid_data(self):
        for r in self.responses:
            result = thermostat._process(r)
            if result:
                actual = thermostat._get_thermostat_points(result)
                try:
                    self.assertIsInstance(actual, types.ListType)
                except AttributeError:
                    self.assertIsInstance(actual, list)
                self.assertEqual("thermostat", actual[0]["measurement"])
                try:
                    self.assertIsInstance(actual[0]["tags"], types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["tags"], dict)
                try:
                    self.assertIsInstance(actual[0]["fields"], types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["fields"], dict)

    @responses.activate
    def test_record_writes_points_for_valid_responses(self):
        url = thermostat._get_api_url("TEST")
        responses.add(responses.GET,
                      url,
                      body="".join(self.responses),
                      status=200,
                      content_type="text/event-stream",
                      stream=True,
                      adding_headers={"Accept": "text/event-stream"},
                      match_querystring=True)
        with patch("den.thermostat.influxdb.InfluxDBClient") as db_patch:
            db = db_patch.return_value
            db.write_points = MagicMock()
            self.assertIsNone(thermostat.record("den_test", 8087, True, "TEST"))
            expected = 24
            self.assertEqual(expected, db.write_points.call_count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
