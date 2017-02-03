"""Record `Nest API <https://developer.nest.com/documentation/api-reference>`_ data to InfluxDB.

The ``thermostat`` API is designed to persist Nest thermostat data in an `InfluxDB <http://influxdb.com/>`_ database.

"""

from contextlib import closing
try:
    from urllib.parse import SplitResult, urlencode, urlunsplit
except ImportError:
    from urllib import urlencode
    from urlparse import SplitResult, urlunsplit

import json

from influxdb import client as influxdb
import requests

from . import LOG

STRUCTURE_MEASUREMENT = "structure"
"""InfluxDB measurement name."""

STRUCTURE_TAG_KEYS = ["away", "country_code", "name", "postal_code", "structure_id", "thermostat_id", "time_zone"]
"""InfluxDB tag keys."""

STRUCTURE_FIELD_KEYS = ["away"]
"""InfluxDB field keys."""

TIMEOUT = (7, 601)
"""Nest API timeout values in seconds.

The first value is the initial connection timeout.  The second is the read timeout which ensures that the streaming
connection will not block forever if the network connection has been lost.

"""

THERMOSTAT_MEASUREMENT = "thermostat"
"""InfluxDB measurement name."""

THERMOSTAT_TAG_KEYS = [
    "can_cool", "can_heat", "device_id", "fan_timer_active", "has_fan", "has_leaf", "hvac_mode", "hvac_state",
    "is_locked", "is_online", "is_using_emergency_heat", "label", "locale", "name", "name_long", "previous_hvac_mode",
    "software_version", "structure_id", "sunlight_correction_active", "sunlight_correction_enabled",
    "temperature_scale", "time_to_target", "time_to_target_training", "where_id", "where_name"
]
"""InfluxDB tag keys."""

THERMOSTAT_FIELD_KEYS = [
    "ambient_temperature_c", "ambient_temperature_f", "away_temperature_high_c", "away_temperature_high_f",
    "away_temperature_low_c", "away_temperature_low_f", "eco_temperature_high_c", "eco_temperature_high_f",
    "eco_temperature_low_c", "eco_temperature_low_f", "fan_timer_duration", "humidity", "locked_temp_max_c",
    "locked_temp_max_f", "locked_temp_min_c", "locked_temp_min_f", "target_temperature_c", "target_temperature_f",
    "target_temperature_high_c", "target_temperature_high_f", "target_temperature_low_c", "target_temperature_low_f"
]
"""InfluxDB field keys."""

NEST_API_PROTOCOL = "https"
NEST_API_LOCATION = "developer-api.nest.com"
"""The base location of the Nest API."""

STREAM_DELIMITER = ":"
"""The token which separates line type and line data in the Nest streaming API response."""


def _get_api_url(nest_api_access_token, path=""):
    """Get a Nest API URL for the given path."""
    query = urlencode({"auth": nest_api_access_token})
    split = SplitResult(
        scheme=NEST_API_PROTOCOL, netloc=NEST_API_LOCATION, path=path.strip("/"), query=query, fragment="")
    return urlunsplit(split)


def _get_stream(nest_api_access_token, path=""):
    """Make a GET request to the Nest REST stream API and return the response object."""
    url = _get_api_url(nest_api_access_token, path)
    r = requests.get(url, headers={"Accept": "text/event-stream"}, stream=True, timeout=TIMEOUT)
    for h in r.history:
        LOG.debug("[%d] Redirect: %s", h.status_code, h.url)
    LOG.debug("[%d] URL: %s", r.status_code, r.url)
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
            LOG.debug(event)
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
            except ValueError as e:
                LOG.error("Error processing data line: '%s', '%s'", line, e)
                data = None
    return data


def _process(line):
    """Process the given line."""
    if _is_event(line):
        _process_event(line)
    return _process_data(line) if _is_data(line) else None


def _get_structure_points(data):
    """Get structure points to write to InfluxDB."""
    points = []
    for structure_data in data["data"]["structures"].values():
        for thermostat_id in structure_data["thermostats"]:
            point = {"measurement": STRUCTURE_MEASUREMENT, "tags": {"thermostat_id": thermostat_id}, "fields": {}}
            for k, v in structure_data.items():
                if k in STRUCTURE_TAG_KEYS:
                    point["tags"][k] = v
                if k in STRUCTURE_FIELD_KEYS:
                    if k == "away":
                        point["fields"]["is_away"] = 1 if "away" in v else 0
                    else:
                        point["fields"][k] = v
            points.append(point)
    return points


def _get_thermostat_points(value):
    """Get thermostat points to write to InfluxDB."""
    points = []
    for thermostat_data in value["data"]["devices"]["thermostats"].values():
        point = {"measurement": THERMOSTAT_MEASUREMENT, "tags": {}, "fields": {}}
        for k, v in thermostat_data.items():
            if k in THERMOSTAT_TAG_KEYS:
                point["tags"][k] = v
            elif k in THERMOSTAT_FIELD_KEYS:
                point["fields"][k] = float(v)
        points.append(point)
    return points


def record(database, port, ssl, nest_api_access_token):
    """Stream results from the Nest API and record them in the database.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :param str nest_api_access_token: Nest API access token.
    :rtype: :py:const:`None`
    :return: When the stream opened to the Nest API has been consumed.
    :raises: :exc:`requests.exceptions.StreamConsumedError`: if the stream has been consumed.
    :raises: :exc:`requests.exceptions.ConnectionError`: if the Nest API cannot be reached.
    :raises: :exc:`requests.exceptions.HTTPError`: if an invalid response is returned from the Nest API.
    :raises: :exc:`requests.exceptions.Timeout`: if the request to the Nest API takes too long to respond.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    with closing(_get_stream(nest_api_access_token)) as stream:
        LOG.info("[%d] Streaming %s", stream.status_code, stream.url)
        for l in stream.iter_lines():
            if l:
                value = _process(l.decode("utf-8"))
                if value:
                    LOG.debug(value)

                    structure_points = _get_structure_points(value)
                    LOG.debug(structure_points)
                    db.write_points(structure_points, time_precision="s")

                    thermostat_points = _get_thermostat_points(value)
                    LOG.debug(thermostat_points)
                    db.write_points(thermostat_points, time_precision="s")

        LOG.info("[%d] Streaming complete %s", stream.status_code, stream.url)
