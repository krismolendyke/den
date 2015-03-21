#!/usr/bin/env python

"""Den is a home for your Nest thermostat data."""

import argparse
import logging
import sys

from requests.packages import urllib3
from requests.exceptions import ConnectionError, HTTPError, StreamConsumedError, Timeout

import den.record


def _record(args):
    """Record Nest thermostat data into the database."""
    print args

    den.record.configure_logging()
    urllib3.disable_warnings()

    while True:
        try:
            den.record.record(args.database, args.port, args.ssl)
        except KeyboardInterrupt as e:
            logging.warn("Keyboard interrupt %s", e)
            return 1
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
            else:
                sys.exit("Unexpected error %s" % e)


def _dump(args):
    """Dump Nest thermostat data from the database to an AWS S3 bucket."""
    print args
    return True


def _configure_logging():
    """Configure basic logging."""
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


def _get_parser():
    """Get a command line argument parser.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("database", help="Database name.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    subparsers = parser.add_subparsers(title="sub-commands")

    parser_record = subparsers.add_parser("record", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=_record.__doc__)
    parser_record.set_defaults(func=_record)

    parser_dump = subparsers.add_parser("dump", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                        help=_dump.__doc__)
    parser_dump.add_argument("bucket", help="AWS S3 bucket name.")
    parser_dump.add_argument("--aws-profile", help="AWS profile name to use for credentials.")
    parser_dump.set_defaults(func=_dump)

    return parser


def _main():
    """The main entry point to the den program.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`int`
    :return: ``0`` if successful, ``1`` if unsuccessful.

    """
    args = _get_parser().parse_args()
    _configure_logging()
    return 0 if args.func(args) else 1


if __name__ == "__main__":
    sys.exit(_main())
