"""Load `Nest API <https://developer.nest.com/documentation/api-reference>`_ JSON data from a file into InfluxDB.

The ``load`` API is designed to insert Nest thermostat data previously dumped from an `InfluxDB
<http://influxdb.com/>`_ database to a compressed JSON file back into InfluxDB.

"""

from gzip import GzipFile

import json
import sys

from influxdb import client as influxdb
from requests.exceptions import ConnectionError


def load(dump_file, database, port, ssl):
    """Load ``dump_file`` into ``database`` database.

    :param str dump_file: The database dump file name.
    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.

    """
    if ssl:
        from requests.packages.urllib3 import disable_warnings
        disable_warnings()

    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    try:
        db.create_database(database)
    except influxdb.InfluxDBClientError:  # pylint: disable=pointless-except
        pass
    except ConnectionError as e:
        sys.exit("Could not connect to database: %s" % e)

    with GzipFile(dump_file, "rb") as f:
        data = json.load(f)
        print "Loading into '%s':" % database
        for d in data:
            print "Series: %s, Points: %d" % (d["name"], len(d["points"]))
        db.write_points(data)
