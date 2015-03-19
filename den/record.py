#!/usr/bin/env python

"""Record Nest API data to InfluxDB."""

from contextlib import closing
from urllib import urlencode
from urlparse import SplitResult, urlunsplit

import argparse
import json
import logging
import os
import sys

from influxdb import client as influxdb
from requests.exceptions import ConnectionError, HTTPError, StreamConsumedError, Timeout
from requests.packages.urllib3 import disable_warnings

import requests


NEST_API_PROTOCOL = "https"
NEST_API_LOCATION = "developer-api.nest.com"
NEST_API_ACCESS_TOKEN = os.environ["DEN_ACCESS_TOKEN"]


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


def _configure_logging():
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


def main(args):
    """Record Nest API data."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("database", help="Database name to record into.")
    parser.add_argument("--port", default=8086, help="Database port.")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS.")
    args = parser.parse_args()

    _configure_logging()
    disable_warnings()

    while True:
        try:
            record(args.database, args.port, args.ssl)
        except KeyboardInterrupt as e:
            logging.warn("Keyboard interrupt %s", e)
            sys.exit()
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


if __name__ == "__main__":
    main(sys.argv[1:])
