#!/usr/bin/env python

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=missing-docstring

from __future__ import absolute_import
import sys

import mock

import unittest

from den import __main__


class MainTestCase(unittest.TestCase):
    def test_weather(self):
        with mock.patch.object(sys, "argv", "prog test weather".split()), \
             mock.patch("den.weather.record", autospec=True) as record_mock:
            __main__.main()
            record_mock.assert_called_once_with('test', 8086, False, '', 39.9528, 75.1638)


if __name__ == "__main__":
    unittest.main(verbosity=2)
