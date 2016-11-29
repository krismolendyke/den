"""Record propane data to InfluxDB."""

import logging

from influxdb import client as influxdb

MEASUREMENT = "propane"
"""InfluxDB measurement value."""

TAG_KEYS = []
"""InfluxDB tag keys."""

FIELD_KEYS = []
"""InfluxDB field keys."""


def _get_points(api_key):
    """Get data prepared for InfluxDB insertion.

    :param str api_key:
    :rtype: :py:class:`list`
    :returns: The current data prepared for insertion into InfluxDB.

    """
    reading = {}  # TODO make call for device
    logging.debug("dict: %s", reading)
    point = {"measurement": MEASUREMENT, "tags": {}, "fields": {}}
    for k, v in reading.items():
        if k in TAG_KEYS:
            point["tags"][k] = v
        elif k in FIELD_KEYS:
            point["fields"][k] = float(v)
        else:
            logging.warning("Unknown property: '%s': '%s'", k, v)
    logging.debug("Point: %s", point)
    return [point]


def record(database, port, ssl, api_key):
    """Record current propane data into the database.

    .. note::

       Propane data is recorded at hour precision.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :param str api_key:
    :rtype: :py:const:`None`
    :return: When the current propane data has been written to the database.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    db.write_points(_get_points(api_key), time_precision="h")
