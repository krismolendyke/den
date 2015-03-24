#!/usr/bin/env python

# pylint: disable=protected-access

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
