#!/usr/bin/env python

import unittest

import mock
import requests

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

    def test_get_token(self):
        with mock.patch("den.propane._get_api_url", autospec=True) as url_mock, \
             mock.patch("den.propane.requests.get", autospec=True) as get_mock:
            propane._get_token("user", "password")
            url_mock.assert_called_once_with(path="getToken")
            get_mock.assert_called_once_with(
                url_mock(), auth=requests.auth.HTTPBasicAuth("user", "password"), verify=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
