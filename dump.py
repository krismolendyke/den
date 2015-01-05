#!/usr/bin/env python

"""Dump an InfluxDB database."""

from gzip import GzipFile

import argparse
import json
import sys

from influxdb import client as influxdb


QUERY = "select * from /.*/"


def _dump(database, port, ssl):
    """Dump the given database.

    The database contents will be dumped as JSON to a GZip file with the same name as the database.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    with GzipFile("%s.json.gz" % database, "wb") as f:
        json.dump(db.query(QUERY), f)


def main(args):
    """Parse arguments and dump database."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("database", help="Database name to dump.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    args = parser.parse_args()
    _dump(args.database, args.port, args.ssl)


if __name__ == "__main__":
    main(sys.argv[1:])
