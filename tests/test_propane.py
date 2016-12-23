#!/usr/bin/env python

import unittest

from den import propane

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods


class PropaneTestCase(unittest.TestCase):
    def test_get_api_url(self):
        expected = "https://data.tankutility.com/api"
        actual = propane._get_api_url()
        self.assertEqual(expected, actual)

        token = "test"
        expected = "https://data.tankutility.com/api?token=test"
        actual = propane._get_api_url(token=token)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main(verbosity=2)
