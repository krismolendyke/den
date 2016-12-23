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

        expected = "https://data.tankutility.com/api?token=token"
        actual = propane._get_api_url(token="token")
        self.assertEqual(expected, actual)

    @staticmethod
    def test_get_token():
        with mock.patch("den.propane._get_api_url", autospec=True) as url_mock, \
             mock.patch("den.propane.requests.get", autospec=True) as get_mock:
            propane._get_token("user", "password")
            url_mock.assert_called_once_with(path="getToken")
            get_mock.assert_called_once_with(
                url_mock(), auth=requests.auth.HTTPBasicAuth("user", "password"), verify=False)

    @staticmethod
    def test_get_devices():
        with mock.patch("den.propane._get_api_url", autospec=True) as url_mock, \
             mock.patch("den.propane.requests.get", autospec=True) as get_mock:
            propane._get_devices("token")
            url_mock.assert_called_once_with(token="token", path="devices")
            get_mock.assert_called_once_with(url_mock(), verify=False)

    @staticmethod
    def test_get_data():
        with mock.patch("den.propane._get_api_url", autospec=True) as url_mock, \
             mock.patch("den.propane.requests.get", autospec=True) as get_mock:
            propane._get_data("token", "device")
            url_mock.assert_called_once_with(token="token", path="devices/device")
            get_mock.assert_called_once_with(url_mock(), verify=False)

    def test_points(self):
        with mock.patch("den.propane._get_devices", autospec=True) as devices_mock:
            propane._get_points("token", "device")
            devices_mock.assert_called_once_with("token")


if __name__ == "__main__":
    unittest.main(verbosity=2)
