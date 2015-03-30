"""Record `Nest API <https://developer.nest.com/documentation/api-reference>`_ data to InfluxDB.

The ``record`` API is designed to persist Nest thermostat data in an `InfluxDB <http://influxdb.com/>`_ database.

.. note::

   The environment variable ``DEN_ACCESS_TOKEN`` is required to authenticate with the Nest API.  Please refer to the
   Nest API `access token
   <https://developer.nest.com/documentation/cloud/how-to-auth#exchange-your-authorization-code-for-an-access-token>`_
   documentation for instructions on how to generate this value.

:raises: :py:exc:`~exceptions.KeyError` if the environment variable ``DEN_ACCESS_TOKEN`` is missing.

"""

from contextlib import closing
from urllib import urlencode
from urlparse import SplitResult, urlunsplit

import json
import logging
import os

from influxdb import client as influxdb

import requests


try:
    NEST_API_ACCESS_TOKEN = os.environ["DEN_ACCESS_TOKEN"]
    """The Nest API `access token
    <https://developer.nest.com/documentation/cloud/how-to-auth#exchange-your-authorization-code-for-an-access-token>`_
    value.

    This value is retrieved from the required environment variable ``DEN_ACCESS_TOKEN``.

    """
except KeyError:
    raise KeyError("Please set the environment variable 'DEN_ACCESS_TOKEN'.")

NEST_API_PROTOCOL = "https"
NEST_API_LOCATION = "developer-api.nest.com"

STREAM_DELIMITER = ":"

def _get_api_url(path=""):
    """Get a Nest API URL for the given path."""
    query = urlencode({"auth": NEST_API_ACCESS_TOKEN})
    split = SplitResult(scheme=NEST_API_PROTOCOL, netloc=NEST_API_LOCATION, path=path.strip("/"), query=query,
                        fragment="")
    return urlunsplit(split)


def _get_stream(path=""):
    """Make a GET request to the Nest REST stream API and return the response object."""
    r = requests.get(_get_api_url(path), headers={"Accept": "text/event-stream"}, stream=True)
    for h in r.history:
        logging.debug("[%d] Redirect: %s", h.status_code, h.url)
    logging.debug("[%d] URL: %s", r.status_code, r.url)
    r.raise_for_status()
    return r


def _is_event(line):
    """Determine if ``line`` represents an event."""
    return line.startswith("event" + STREAM_DELIMITER)


def _is_data(line):
    """Determine if ``line`` represents data."""
    return line.startswith("data" + STREAM_DELIMITER)


def _process_event(line):
    """Process the given event line."""
    event = None
    if STREAM_DELIMITER in line:
        _, event = line.split(STREAM_DELIMITER, 1)
        event = event.strip()
        if event:
            logging.debug(event)
            if event == "keep-alive":
                event = None
        else:
            event = None
    return event


def _process_data(line):
    """Process the given data line."""
    data = None
    if STREAM_DELIMITER in line:
        _, data_str = line.split(STREAM_DELIMITER, 1)
        data_str = data_str.strip()
        if data_str:
            try:
                data = json.loads(data_str)
            except ValueError, e:
                logging.error("Error processing data line: '%s', '%s'", line, e)
                data = None
    return data


def _process(line):
    """Process the given line."""
    if _is_event(line):
        _process_event(line)
    return _process_data(line) if _is_data(line) else None


def _get_structures(data):
    """Get structure data from the given data dict."""
    structures = []
    try:
        structures = data["data"]["structures"].values()
    except TypeError:
        logging.error("Invalid data: '%s'", data)
    except KeyError:
        logging.error("No structures found in data: '%s'", data)
    return structures


def _get_structure_data(data):
    """Get structure data to write to InfluxDB."""
    name = "structures"
    structures = _get_structures(data)
    points = []
    for s in structures:
        try:
            del s["thermostats"]
        except KeyError:  # pylint: disable=pointless-except
            pass
        points.append(s.values())
    columns = structures[0].keys() if structures else []
    return [{"name": name, "columns": columns, "points": points}]


def _get_thermostats(data):
    """Get thermostat data from the given data dict."""
    thermostats = []
    try:
        thermostats = data["data"]["devices"]["thermostats"].values()
    except TypeError:
        logging.error("Invalid data: '%s'", data)
    except KeyError:
        logging.error("No thermostats found in data: '%s'", data)
    return thermostats


def _get_thermostat_data(data):
    """Get thermostat data to write to InfluxDB."""
    name = "thermostats"
    thermostats = _get_thermostats(data)
    columns = []
    points = []
    if thermostats:
        columns = thermostats[0].keys()
        points = [t.values() for t in thermostats]
    return [{"name": name, "columns": columns, "points": points}]


def configure_logging():
    """Configure basic logging."""
    logging.basicConfig(filename="den.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


def record(database, port, ssl):
    """Stream results from the Nest API and record them in the database.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :rtype: :py:const:`None`
    :return: When the stream opened to the Nest API has been consumed.
    :raises: :exc:`requests.exceptions.StreamConsumedError`: if the stream has been consumed.
    :raises: :exc:`requests.exceptions.ConnectionError`: if the Nest API cannot be reached.
    :raises: :exc:`requests.exceptions.HTTPError`: if an invalid response is returned from the Nest API.
    :raises: :exc:`requests.exceptions.Timeout`: if the request to the Nest API takes too long to respond.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    with closing(_get_stream()) as stream:
        logging.debug("[%d] Streaming %s", stream.status_code, stream.url)
        for l in stream.iter_lines():
            if l:
                value = _process(l)
                if value:
                    logging.info(value)
                    db.write_points(_get_structure_data(value))
                    db.write_points(_get_thermostat_data(value))
        logging.debug("[%d] Streaming complete %s", stream.status_code, stream.url)
