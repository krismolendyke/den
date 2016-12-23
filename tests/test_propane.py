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

    def test_get_points(self):
        with mock.patch("den.propane._get_devices", autospec=True) as devices_mock, \
             mock.patch("den.propane._get_data", autospec=True) as data_mock:
            devices_mock.return_value = ["54df6a066667531535371367", "54ff69057492666782350667"]
            data_mock.return_value = {
                "device": {
                    "name": "Sample Device",
                    "address": "6 Dane St., Somerville, MA 02143, USA",
                    "capacity": 100,
                    "status": "deployed",
                    "orientation": "horizontal",
                    "fuelType": "propane",
                    "lastReading": {
                        "tank": 20,
                        "temperature": 72.12,
                        "time": 1444338760345,
                        "time_iso": "2015-10-08T21:12:40.345Z"
                    }
                }
            }
            expected = [
                {
                    "measurement": "propane",
                    "tags": {
                        "device": devices_mock.return_value[0],
                        "name": "Sample Device",
                        "fuelType": "propane",
                        "address": "6 Dane St., Somerville, MA 02143, USA",
                        "status": "deployed",
                        "orientation": "horizontal"
                    },
                    "fields": {
                        "capacity": 100.0,
                        "tank": 20.0,
                        "temperature": 72.12
                    }
                },
                {
                    "measurement": "propane",
                    "tags": {
                        "device": devices_mock.return_value[1],
                        "name": "Sample Device",
                        "fuelType": "propane",
                        "address": "6 Dane St., Somerville, MA 02143, USA",
                        "status": "deployed",
                        "orientation": "horizontal"
                    },
                    "fields": {
                        "capacity": 100.0,
                        "tank": 20.0,
                        "temperature": 72.12
                    }
                }
            ]
            actual = propane._get_points("token", "device")
            self.assertEqual(expected, actual)
            devices_mock.assert_called_once_with("token")
            data_mock.assert_any_call("token", devices_mock.return_value[0])
            data_mock.assert_any_call("token", devices_mock.return_value[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
