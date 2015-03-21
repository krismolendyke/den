"""Record Nest API data to InfluxDB.

The ``record`` API is designed to persist Nest thermostat data in an InfluxDB database.

"""

from contextlib import closing
from urllib import urlencode
from urlparse import SplitResult, urlunsplit

import json
import logging
import os

from influxdb import client as influxdb

import requests


NEST_API_PROTOCOL = "https"
NEST_API_LOCATION = "developer-api.nest.com"
NEST_API_ACCESS_TOKEN = os.environ["DEN_ACCESS_TOKEN"]
"""The Nest API `access token
<https://developer.nest.com/documentation/cloud/how-to-auth#exchange-your-authorization-code-for-an-access-token>`_.

.. note::

   This value is taken from the environment variable ``DEN_ACCESS_TOKEN``.  It is required to authenticate with the
   Nest API.

"""


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
    """Is the given line an event line?"""
    return line.startswith("event:")


def _is_data(line):
    """Is the given line a data line?"""
    return line.startswith("data:")


def _process_event(line):
    """Process the given event line."""
    _, event = line.split(":", 1)
    event = event.strip()
    logging.debug(event)
    return None if event == "keep-alive" else event


def _process_data(line):
    """Process the given data line."""
    _, data_str = line.split(":", 1)
    return json.loads(data_str.strip())


def _process(line):
    """Process the given line."""
    if _is_event(line):
        _process_event(line)
    return _process_data(line) if _is_data(line) else None


def _get_structures(data):
    """Get structure data from the given data dict."""
    structures = data["data"]["structures"]
    return [structures[s] for s in structures]


def _get_structure_data(data):
    """Get structure data to write to InfluxDB."""
    name = "structures"
    structures = _get_structures(data)
    points = []
    for s in structures:
        try:
            del s["thermostats"]
        except KeyError:
            pass
        points.append(s.values())
    columns = structures[0].keys()
    return [{"name": name, "columns": columns, "points": points}]


def _get_thermostats(data):
    """Get thermostat data from the given data dict."""
    thermostats = data["data"]["devices"]["thermostats"]
    return [thermostats[t] for t in thermostats]


def _get_thermostat_data(data):
    """Get thermostat data to write to InfluxDB."""
    name = "thermostats"
    thermostats = _get_thermostats(data)
    columns = thermostats[0].keys()
    points = [t.values() for t in thermostats]
    return [{"name": name, "columns": columns, "points": points}]


def configure_logging():
    """Configure basic logging."""
    logging.basicConfig(filename="den.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


def record(database, port, ssl):
    """Stream results from the API and record them in the database."""
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
