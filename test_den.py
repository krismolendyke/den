#!/usr/bin/env python

# pylint: disable=protected-access,too-many-public-methods,missing-docstring

import logging
import json
import os
import types
import unittest

from mock import patch

os.environ["DEN_ACCESS_TOKEN"] = "TEST"
from den import record


logging.basicConfig(filename=os.devnull)


class RecordTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open("responses.txt", "r") as f:
            cls.responses = [l for l in f]

    def test_missing_env_variable_raises_key_error(self):
        with patch.dict("os.environ", {}):
            del os.environ["DEN_ACCESS_TOKEN"]
            with self.assertRaisesRegexp(KeyError, r"Please set the environment variable 'DEN_ACCESS_TOKEN'."):
                reload(record)

    def test_get_api_url(self):
        expected = "https://developer-api.nest.com?auth=%s" % record.NEST_API_ACCESS_TOKEN
        actual = record._get_api_url()
        self.assertEqual(expected, actual)

        expected = "https://developer-api.nest.com/structures?auth=%s" % record.NEST_API_ACCESS_TOKEN
        for path in ["structures", "/structures", "/structures/", "structures/"]:
            self.assertEqual(expected, record._get_api_url(path))

    def test_is_event(self):
        self.assertTrue(record._is_event("event:"))
        self.assertFalse(record._is_event("event"))
        self.assertFalse(record._is_event("data:"))

    def test_is_data(self):
        self.assertTrue(record._is_data("data:"))
        self.assertFalse(record._is_data("data"))
        self.assertFalse(record._is_data("event:"))

    def test_process_event_returns_none_for_invalid_line(self):
        invalid_lines = [
            "",
            ":",
            "event:",
            "event: "
        ]
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
        invalid_lines = [
            "",
            ":",
            "data:",
            "data: ",
            "data: not JSON"
        ]
        for line in invalid_lines:
            self.assertIsNone(record._process_data(line))

    def test_process_data_returns_list_for_valid_line(self):
        expected = [{"key": "val"}]
        actual = record._process_data("data: " + json.dumps(expected))
        self.assertEqual(expected, actual)
        actual = record._process_data("data:" + json.dumps(expected))
        self.assertEqual(expected, actual)

    def test_process_returns_none_for_non_data_line(self):
        invalid_lines = [
            "",
            ":",
            "event:",
            "event: "
        ]
        for line in invalid_lines:
            self.assertIsNone(record._process(line))

    def test_process_returns_none_for_invalid_data_line(self):
        invalid_lines = [
            "",
            ":",
            "data:",
            "data: ",
            "data: not JSON"
        ]
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
                self.assertIsInstance(actual, types.DictType)

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
        structure = {"name": "Home",
                     "away": "home",
                     "time_zone": "America/New_York",
                     "postal_code": "19335",
                     "thermostats": ["THERMOSTATID0", "THERMOSTATID1"],
                     "country_code": "US",
                     "structure_id": "STRUCTUREID"}
        expected = [structure]
        actual = record._get_structures({"data": {"structures": {"STRUCTUREID": structure}}})
        self.assertEqual(expected, actual)

        for r in self.responses:
            result = record._process(r)
            actual = record._get_structures(result)
            self.assertIsInstance(actual, types.ListType)
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
                self.assertIsInstance(actual, types.ListType)
                self.assertEqual("structures", actual[0]["name"])
                self.assertIsInstance(actual[0]["columns"], types.ListType)
                self.assertIsInstance(actual[0]["points"], types.ListType)
                self.assertNotIn("thermostats", actual[0])

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
                self.assertIsInstance(actual, types.ListType)
                self.assertEqual(1, len(actual))

    def test_get_thermostat_data_returns_empty_structure_for_invalid_data(self):
        expected = [{"name": "thermostats", "columns": [], "points": []}]
        actual = record._get_thermostat_data(None)
        self.assertEqual(expected, actual)
        actual = record._get_thermostat_data({})
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main(verbosity=2)
