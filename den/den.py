#!/usr/bin/env python

"""Den is a home for your Nest thermostat data."""

import argparse
import sys


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

    subparsers.add_parser("record", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                          help="Record Nest thermostat data into the database.")

    parser_dump = subparsers.add_parser("dump", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                        help="Dump Nest thermostat data from the database to an AWS S3 bucket.")
    parser_dump.add_argument("bucket", help="AWS S3 bucket name.")
    parser_dump.add_argument("--aws-profile", help="AWS profile name to use for credentials.")

    return parser


def _main():
    """The main entry point to the den program.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`int`
    :return: ``0`` when successful.

    """
    args = _get_parser().parse_args()
    print args
    return 0


if __name__ == "__main__":
    sys.exit(_main())
