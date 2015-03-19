#!/usr/bin/env python

"""Den is a home for your Nest thermostat data."""

import argparse
import sys


def record(args):
    """Record Nest thermostat data into the database."""
    print args
    return True


def dump(args):
    """Dump Nest thermostat data from the database to an AWS S3 bucket."""
    print args
    return True


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
                                          help=record.__doc__)
    parser_record.set_defaults(func=record)

    parser_dump = subparsers.add_parser("dump", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                        help=dump.__doc__)
    parser_dump.add_argument("bucket", help="AWS S3 bucket name.")
    parser_dump.add_argument("--aws-profile", help="AWS profile name to use for credentials.")
    parser_dump.set_defaults(func=dump)

    return parser


def _main():
    """The main entry point to the den program.

    :param list argv: A list of command line arguments.
    :rtype: :py:class:`int`
    :return: ``0`` if successful, ``1`` if unsuccessful.

    """
    args = _get_parser().parse_args()
    return 0 if args.func(args) else 1


if __name__ == "__main__":
    sys.exit(_main())
