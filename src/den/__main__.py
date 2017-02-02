#!/usr/bin/env python
"""Den is a home for your home's data."""

from __future__ import absolute_import

import argparse
import os
import sys

from requests.exceptions import ConnectionError, HTTPError, StreamConsumedError, Timeout
import backoff

from . import __version__
from . import LOG
from . import propane
from . import thermostat
from . import weather


@backoff.on_exception(backoff.expo, (ConnectionError, HTTPError, Timeout))
def _thermostat(args):  # noqa
    """Record Nest thermostat data into the database.

    This function will attempt to recover from various network errors.  It will run indefinitely until interrupted
    from the keyboard or an unexpected exception occurs.

    """
    while True:
        try:
            thermostat.record(args.database, args.port, args.ssl, args.access_token)
        except KeyboardInterrupt as e:
            LOG.warn("Keyboard interrupt %s", e)
            return True
        except StreamConsumedError as e:
            LOG.warn("Stream consumed %s", e)
        except ConnectionError as e:
            LOG.exception("Connection error %s", e)
            raise e
        except HTTPError as e:
            LOG.exception("HTTPError %s", e)
            raise e
        except Timeout as e:
            LOG.exception("Timeout %s", e)
            raise e
        except Exception as e:  # pylint: disable=broad-except
            LOG.critical("Unexpected error %s", e)
            if e.message == "EOF occurred in violation of protocol":
                LOG.info("Re-establishing connection")
            elif e.message == "400: invalid payload":
                LOG.critical("Could not write response to database")
            else:
                return False


def _weather(args):
    """Record weather data into the database. Powered by Dark Sky."""
    weather.record(args.database, args.port, args.ssl, args.api_key, args.lat, args.lon)


def _propane(args):
    """Record propane data into the database."""
    propane.record(args.database, args.port, args.ssl, args.username, args.password)


def _add_thermostat_subparser(subparsers):
    """Add record subparser.

    :param argparse.ArgumentParser subparsers:
    :rtype: :py:const:`None`

    """
    parser = subparsers.add_parser(
        "thermostat", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=_thermostat.__doc__)
    parser.add_argument(
        "--access-token",
        help="Nest API access token. Defaults to environment DEN_ACCESS_TOKEN value.",
        default=os.environ.get("DEN_ACCESS_TOKEN", ""))
    parser.set_defaults(func=_thermostat)


def _add_weather_subparser(subparsers):
    """Add weather subparser.

    :param argparse.ArgumentParser subparsers:
    :rtype: :py:const:`None`

    """
    parser = subparsers.add_parser(
        "weather", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=_weather.__doc__)
    parser.add_argument(
        "--api-key",
        help="Weather API key. Defaults to environment DEN_WEATHER_API_KEY value.",
        default=os.environ.get("DEN_WEATHER_API_KEY", ""))
    parser.add_argument(
        "--lat",
        help="Latitude. Defaults to environment DEN_LAT value.",
        default=float(os.environ.get("DEN_LAT", 39.9528)))
    parser.add_argument(
        "--lon",
        help="Longitude. Defaults to environment DEN_LON value.",
        default=float(os.environ.get("DEN_LON", 75.1638)))
    parser.set_defaults(func=_weather)


def _add_propane_subparser(subparsers):
    """Add propane subparser.

    :param argparse.ArgumentParser subparsers:
    :rtype: :py:const:`None`

    """
    parser = subparsers.add_parser(
        "propane", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=_propane.__doc__)
    parser.add_argument("--username", help="Propane API username.", default=os.environ.get("DEN_PROPANE_USERNAME"))
    parser.add_argument("--password", help="Propane API password.", default=os.environ.get("DEN_PROPANE_PASSWORD"))
    parser.set_defaults(func=_propane)


def _get_parser():
    """Get a command line argument parser.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", "-v", action="version", version=__version__)
    parser.add_argument("database", help="Database name.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    subparsers = parser.add_subparsers(title="sub-commands")
    _add_thermostat_subparser(subparsers)
    _add_weather_subparser(subparsers)
    _add_propane_subparser(subparsers)
    return parser


def main():
    """The main entry point to the den program.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`int`
    :return: ``0`` if successful, ``1`` if unsuccessful.

    """
    args = _get_parser().parse_args()
    return 0 if args.func(args) else 1


if __name__ == "__main__":
    sys.exit(main())
