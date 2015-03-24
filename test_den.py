#!/usr/bin/env python

# pylint: disable=protected-access

import json
import os
import unittest

from mock import patch

os.environ["DEN_ACCESS_TOKEN"] = "TEST"
from den import record


class RecordTestCase(unittest.TestCase):

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

    def test_process_data_returns_a_list_for_valid_line(self):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
