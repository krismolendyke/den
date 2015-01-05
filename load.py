#!/usr/bin/env python

"""Load data into an InfluxDB database."""

from gzip import GzipFile

import argparse
import json
import sys

from influxdb import client as influxdb
from requests.exceptions import ConnectionError


def _load(dump_file, database, port, ssl):
    """Load the given dump file into the given InfluxDB database."""
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    try:
        db.create_database(database)
    except influxdb.InfluxDBClientError:
        pass
    except ConnectionError as e:
        sys.exit("Could not connect to database: %s" % e)

    with GzipFile(dump_file, "rb") as f:
        data = json.load(f)
        print "Loading into '%s':" % database
        for d in data:
            print "Series: %s, Points: %d" % (d["name"], len(d["points"]))
        db.write_points(data)


def main(args):
    """Load InfluxDB data."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("dump_file", help="Compressed data JSON dump file.")
    parser.add_argument("database", help="Database name to load data into.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    args = parser.parse_args(args)
    _load(args.dump_file, args.database, args.port, args.ssl)


if __name__ == "__main__":
    main(sys.argv[1:])
