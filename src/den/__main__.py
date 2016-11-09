#!/usr/bin/env python
"""Den is a home for your Nest thermostat data."""

from __future__ import absolute_import

import argparse
import logging
import os
import sys

from requests.exceptions import ConnectionError, HTTPError, StreamConsumedError, Timeout

from . import __version__
from . import record
from . import weather


def _record(args):  # noqa
    """Record Nest thermostat data into the database.

    This function will attempt to recover from various network errors.  It will run indefinitely until interrupted
    from the keyboard or an unexpected exception occurs.

    """
    record.configure_logging()

    while True:
        try:
            record.record(args.database, args.port, args.ssl, args.access_token)
        except KeyboardInterrupt as e:
            logging.warn("Keyboard interrupt %s", e)
            return True
        except StreamConsumedError as e:
            logging.warn("Stream consumed %s", e)
        except ConnectionError as e:
            logging.error("Connection error %s", e)
        except HTTPError as e:
            logging.error("HTTPError %s", e)
        except Timeout as e:
            logging.error("Timeout %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logging.critical("Unexpected error %s", e)
            if e.message == "EOF occurred in violation of protocol":
                logging.info("Re-establishing connection")
            elif e.message == "400: invalid payload":
                logging.critical("Could not write response to database")
            else:
                return False


def _weather(args):
    """Record weather data into the database."""
    weather.record(args.database, args.port, args.ssl, args.api_key, args.lat, args.lon)


def _configure_logging(log_to_file):
    """Configure basic logging.

    :param bool log_to_file: Whether or not output should be logged to a file.

    """
    log_format = "%(asctime)s %(levelname)s %(message)s"
    if log_to_file:
        logging.basicConfig(filename="%s.log" % os.path.splitext(__file__)[0], level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.DEBUG, format=log_format)


def _add_record_subparser(subparsers):
    """Add record subparser.

    :param argparse.ArgumentParser subparsers:
    :rtype: :py:const:`None`

    """
    parser = subparsers.add_parser(
        "record", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=_record.__doc__)
    parser.add_argument(
        "--access-token",
        help="Nest API access token. Defaults to environment DEN_ACCESS_TOKEN value.",
        default=os.environ.get("DEN_ACCESS_TOKEN", ""))
    parser.set_defaults(func=_record)


def _add_weather_subparser(subparsers):
    """Add weather subparser.

    :param argparse.ArgumentParser subparsers:
    :rtype: :py:const:`None`

    """
    parser = subparsers.add_parser(
        "weather", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=_weather.__doc__)
    parser.add_argument(
        "--api-key",
        help="Weather API key. Defaults to environment DEN_FORECAST_IO_API_KEY value.",
        default=os.environ.get("DEN_FORECAST_IO_API_KEY", ""))
    parser.add_argument(
        "--lat",
        help="Latitude. Defaults to environment DEN_LAT value.",
        default=float(os.environ.get("DEN_LAT", 39.9528)))
    parser.add_argument(
        "--lon",
        help="Longitude. Defaults to environment DEN_LON value.",
        default=float(os.environ.get("DEN_LON", 75.1638)))
    parser.set_defaults(func=_weather)


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
    parser.add_argument("--log-to-file", action="store_true", help="Log to a file instead of stdout.")
    subparsers = parser.add_subparsers(title="sub-commands")
    _add_record_subparser(subparsers)
    _add_weather_subparser(subparsers)
    return parser


def main():
    """The main entry point to the den program.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`int`
    :return: ``0`` if successful, ``1`` if unsuccessful.

    """
    args = _get_parser().parse_args()
    _configure_logging(args.log_to_file)
    return 0 if args.func(args) else 1


if __name__ == "__main__":
    sys.exit(main())
