"""Dump `Nest API <https://developer.nest.com/documentation/api-reference>`_ data from InfluxDB to a file.

The ``dump`` API is designed to unload Nest thermostat data stored in an `InfluxDB <http://influxdb.com/>`_ database
to a file for backup.

"""

from gzip import GzipFile

import argparse
import json
import sys

from influxdb import client as influxdb

import boto

QUERY = "select * from /.*/"


def upload(dump_file, bucket, profile=None):
    """Upload ``dump_file`` to S3.

    :param str dump_file: The database dump file name.
    :param str bucket: The S3 bucket name to upload ``dump_file`` to.
    :param str profile: (optional) The AWS IAM profile name to use when authenticating.

    """
    if profile:
        conn = boto.connect_s3(profile_name=profile)
    else:
        conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket)
    key = boto.s3.key.Key(bucket, dump_file)
    key.set_contents_from_filename(dump_file)


def dump(database, port, ssl):
    """Dump ``database`` to a file.

    The database contents will be dumped with :py:class:`json.dumps` to a GZip file with the same name as
    ``database``.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :rtype: :py:class:`str`
    :returns: The name of the dump file.

    """
    if ssl:
        from requests.packages.urllib3 import disable_warnings
        disable_warnings()

    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    dump_file = "%s.json.gz" % database
    with GzipFile(dump_file, "wb") as f:
        json.dump(db.query(QUERY), f)
    return dump_file


def main(args):
    """Parse arguments and dump database."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("database", help="Database name to dump.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    parser.add_argument("--bucket", help="AWS S3 bucket name")
    parser.add_argument("--aws-profile", help="AWS profile name to pull credentials from.")
    args = parser.parse_args()

    dump_file = _dump(args.database, args.port, args.ssl)
    if args.bucket:
        _upload(dump_file, args.bucket, args.aws_profile)


if __name__ == "__main__":
    main(sys.argv[1:])
