#!/usr/bin/env python

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=missing-docstring

import json
import os
import types
import unittest

import requests
import responses
from mock import MagicMock, patch

from . import _reset_environ
_reset_environ()
from den import record, weather

record.configure_logging(filename=os.devnull)


class RecordTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__), "responses.txt"), "r") as f:
            cls.responses = [l for l in f]

    def test_missing_env_variable_raises_key_error(self):
        with patch.dict("os.environ", {}):
            del os.environ["DEN_ACCESS_TOKEN"]
            with self.assertRaisesRegexp(KeyError, r"Please set the environment variable 'DEN_ACCESS_TOKEN'."):
                try:
                    reload(record)
                except NameError:
                    import importlib
                    importlib.reload(record)

    def test_get_api_url(self):
        expected = "https://developer-api.nest.com?auth=%s" % record.NEST_API_ACCESS_TOKEN
        actual = record._get_api_url()
        self.assertEqual(expected, actual)

        expected = "https://developer-api.nest.com/structures?auth=%s" % record.NEST_API_ACCESS_TOKEN
        for path in ["structures", "/structures", "/structures/", "structures/"]:
            self.assertEqual(expected, record._get_api_url(path))

    @responses.activate
    def test_get_stream(self):
        url = record._get_api_url("")
        responses.add(responses.GET,
                      url,
                      body="".join(self.responses),
                      status=200,
                      content_type="text/event-stream",
                      stream=True,
                      adding_headers={"Accept": "text/event-stream"},
                      match_querystring=True)
        actual = record._get_stream()
        self.assertIsInstance(actual, requests.Response)
        self.assertEqual(len(self.responses), len(list(actual.iter_lines())))

    def test_is_event(self):
        self.assertTrue(record._is_event("event:"))
        self.assertFalse(record._is_event("event"))
        self.assertFalse(record._is_event("data:"))

    def test_is_data(self):
        self.assertTrue(record._is_data("data:"))
        self.assertFalse(record._is_data("data"))
        self.assertFalse(record._is_data("event:"))

    def test_process_event_returns_none_for_invalid_line(self):
        invalid_lines = ["", ":", "event:", "event: "]
        for line in invalid_lines:
            self.assertIsNone(record._process_event(line))

    def test_process_event_returns_none_for_keep_alive_line(self):
        self.assertIsNone(record._process_event("event: keep-alive"))
        self.assertIsNone(record._process_event("event:keep-alive"))

    def test_process_event_returns_event_for_valid_line(self):
        expected = "Test event"
        actual = record._process_event("event: " + expected)
        self.assertEqual(expected, actual)
        actual = record._process_event("event:" + expected)
        self.assertEqual(expected, actual)

    def test_process_data_returns_none_for_invalid_line(self):
        invalid_lines = ["", ":", "data:", "data: ", "data: not JSON"]
        for line in invalid_lines:
            self.assertIsNone(record._process_data(line))

    def test_process_data_returns_list_for_valid_line(self):
        expected = [{"key": "val"}]
        actual = record._process_data("data: " + json.dumps(expected))
        self.assertEqual(expected, actual)
        actual = record._process_data("data:" + json.dumps(expected))
        self.assertEqual(expected, actual)

    def test_process_returns_none_for_non_data_line(self):
        invalid_lines = ["", ":", "event:", "event: "]
        for line in invalid_lines:
            self.assertIsNone(record._process(line))

    def test_process_returns_none_for_invalid_data_line(self):
        invalid_lines = ["", ":", "data:", "data: ", "data: not JSON"]
        for line in invalid_lines:
            self.assertIsNone(record._process(line))

    def test_process_returns_list_for_valid_data_line(self):
        expected = [{"key": "val"}]
        actual = record._process("data: " + json.dumps(expected))
        self.assertEqual(expected, actual)
        actual = record._process("data:" + json.dumps(expected))
        self.assertEqual(expected, actual)

        for r in self.responses:
            actual = record._process(r)
            if r.startswith("event"):
                self.assertIsNone(actual)
            elif r.startswith("data"):
                try:
                    self.assertIsInstance(actual, types.DictType)
                except AttributeError:
                    self.assertIsInstance(actual, dict)

    def test_get_structures_returns_empty_list_for_invalid_data(self):
        expected = []
        actual = record._get_structures(None)
        self.assertEqual(expected, actual)
        actual = record._get_structures({})
        self.assertEqual(expected, actual)
        actual = record._get_structures({"data": {}})
        self.assertEqual(expected, actual)
        actual = record._get_structures({"data": {"structures": {}}})
        self.assertEqual(expected, actual)

    def test_get_structures_returns_list_for_valid_data(self):
        expected = [{}]
        actual = record._get_structures({"data": {"structures": {"STRUCTUREID": {}}}})
        self.assertEqual(expected, actual)
        structure = {
            "name": "Home",
            "away": "home",
            "time_zone": "America/New_York",
            "postal_code": "19335",
            "thermostats": ["THERMOSTATID0", "THERMOSTATID1"],
            "country_code": "US",
            "structure_id": "STRUCTUREID"
        }
        expected = [structure]
        actual = record._get_structures({"data": {"structures": {"STRUCTUREID": structure}}})
        self.assertEqual(expected, actual)

        for r in self.responses:
            result = record._process(r)
            actual = record._get_structures(result)
            try:
                self.assertIsInstance(actual, types.ListType)
            except AttributeError:
                self.assertIsInstance(actual, list)
            if result:
                self.assertEqual(1, len(actual))
                self.assertIn("structure_id", actual[0])
                self.assertIn("thermostats", actual[0])
            else:
                self.assertEqual([], actual)

    def test_get_structure_data_returns_empty_structure_for_invalid_data(self):
        expected = [{"name": "structures", "columns": [], "points": []}]
        actual = record._get_structure_data(None)
        self.assertEqual(expected, actual)
        actual = record._get_structure_data({})
        self.assertEqual(expected, actual)
        actual = record._get_structure_data({"data": {"structures": {"": {"thermostats_is_missing": "not here"}}}})
        self.assertNotIn("thermostats", actual)

    def test_get_structure_data_returns_list_for_valid_data(self):
        for r in self.responses:
            result = record._process(r)
            if result:
                actual = record._get_structure_data(result)
                try:
                    self.assertEqual("structures", actual[0]["name"])
                except AttributeError:
                    self.assertIsInstance(actual[0]["name"], list)
                try:
                    self.assertIsInstance(actual[0]["columns"], types.ListType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["columns"], list)
                try:
                    self.assertIsInstance(actual[0]["points"], types.ListType)
                except AttributeError:
                    self.assertIsInstance(actual[0]["points"], list)
                self.assertNotIn("thermostats", actual[0])
                self.assertNotIn("wheres", actual[0])

    def test_get_thermostats_returns_empty_list_for_invalid_data(self):
        expected = []
        actual = record._get_thermostats(None)
        self.assertEqual(expected, actual)
        actual = record._get_thermostats("")
        self.assertEqual(expected, actual)
        actual = record._get_thermostats({})
        self.assertEqual(expected, actual)

    def test_get_thermostats_returns_list_for_valid_data(self):
        for r in self.responses:
            result = record._process(r)
            actual = record._get_thermostats(result)
            if actual:
                try:
                    self.assertIsInstance(actual, types.ListType)
                except AttributeError:
                    self.assertIsInstance(actual, list)

    def test_get_thermostat_data_returns_empty_structure_for_invalid_data(self):
        expected = [{"name": "thermostats", "columns": [], "points": []}]
        actual = record._get_thermostat_data(None)
        self.assertEqual(expected, actual)
        actual = record._get_thermostat_data({})
        self.assertEqual(expected, actual)

    def test_get_thermostat_data_returns_list_for_valid_data(self):
        for r in self.responses:
            result = record._process(r)
            if result:
                for thermostat in record._get_thermostats(result):
                    actual = record._get_thermostat_data(thermostat)
                    try:
                        self.assertIsInstance(actual, types.ListType)
                    except AttributeError:
                        self.assertIsInstance(actual, list)
                    try:
                        self.assertIsInstance(actual[0]["columns"], types.ListType)
                    except AttributeError:
                        self.assertIsInstance(actual[0]["columns"], list)
                    try:
                        self.assertIsInstance(actual[0]["points"], types.ListType)
                    except AttributeError:
                        self.assertIsInstance(actual[0]["points"], list)
                    try:
                        self.assertIsInstance(actual[0]["points"][0], types.ListType)
                    except AttributeError:
                        self.assertIsInstance(actual[0]["points"][0], list)
                    self.assertEqual(len(actual[0]["columns"]), len(actual[0]["points"][0]))
                    self.assertEqual("thermostats", actual[0]["name"])

    @responses.activate
    def test_record_writes_points_for_valid_responses(self):
        url = record._get_api_url("")
        responses.add(responses.GET,
                      url,
                      body="".join(self.responses),
                      status=200,
                      content_type="text/event-stream",
                      stream=True,
                      adding_headers={"Accept": "text/event-stream"},
                      match_querystring=True)
        with patch("den.record.influxdb.InfluxDBClient") as db_patch:
            db = db_patch.return_value
            db.write_points = MagicMock()
            self.assertIsNone(record.record("den_test", port=8087, ssl=True))
            self.assertTrue(db.write_points.called)
            expected = 0
            for r in self.responses:
                result = record._process(r)
                expected += len(record._get_structures(result)) + len(record._get_thermostats(result))
            self.assertEqual(expected, db.write_points.call_count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
