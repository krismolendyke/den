#!/usr/bin/env python

# pylint: disable=protected-access

import os
import unittest


os.environ["DEN_ACCESS_TOKEN"] = "TEST"
from den import record


class RecordTestCase(unittest.TestCase):
    def test_get_api_url(self):
        expected = "https://developer-api.nest.com?auth=%s" % record.NEST_API_ACCESS_TOKEN
        actual = record._get_api_url()
        self.assertEqual(expected, actual)

        expected = "https://developer-api.nest.com/structures?auth=%s" % record.NEST_API_ACCESS_TOKEN
        for path in ["structures", "/structures", "/structures/", "structures/"]:
            self.assertEqual(expected, record._get_api_url(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
