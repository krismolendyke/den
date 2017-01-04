"""Record propane data to InfluxDB."""

try:
    from urllib.parse import SplitResult, urlencode, urlunsplit
except ImportError:
    from urllib import urlencode
    from urlparse import SplitResult, urlunsplit

from influxdb import client as influxdb
import requests

from . import LOG

PROPANE_API_PROTOCOL = "https"
PROPANE_API_LOCATION = "data.tankutility.com"
"""The base location of the propane API."""

MEASUREMENT = "propane"
"""InfluxDB measurement value."""

TAG_KEYS = ["name", "address", "status", "orientation", "fuelType"]
"""InfluxDB tag keys."""

FIELD_KEYS = ["capacity", "tank", "temperature"]
"""InfluxDB field keys."""


def _get_api_url(token="", path=""):
    """Get an API URL for the given path.

    :param str token: (optional) API token
    :param str path: (optional) API path
    :rtype: :py:class:`str`
    :returns: An API URL

    """
    query = urlencode({"token": token}) if token else ""
    api_path = "/".join(["api", path]).strip("/")
    split = SplitResult(
        scheme=PROPANE_API_PROTOCOL, netloc=PROPANE_API_LOCATION, path=api_path, query=query, fragment="")
    return urlunsplit(split)


def _get_token(username, password):
    """Get an API token.

    Unfortunately, the Tank Utility API only offers basic authentication and expires each API token after 24 hours.

    :param str username:
    :param str password:
    :rtype: :py:class:`str`
    :returns: An API token

    """
    r = requests.get(_get_api_url(path="getToken"),
                     auth=requests.auth.HTTPBasicAuth(username, password),
                     verify=False)
    LOG.debug("[%d] URL: %s", r.status_code, r.url)
    r.raise_for_status()
    return r.json()["token"]


def _get_devices(token):
    """Get devices currently associated with ``api_key``.

    :param str token:
    :rtype: :py:class:`list`

    """
    r = requests.get(_get_api_url(token=token, path="devices"), verify=False)
    LOG.debug("[%d] URL: %s", r.status_code, r.url)
    r.raise_for_status()
    return r.json()["devices"]


def _get_data(token, device):
    """Get current data from ``device``.

    :param str token:
    :param str device: Device id
    :rtype: :py:class:`dict`

    """
    path = "/".join(["devices", device])
    r = requests.get(_get_api_url(token=token, path=path), verify=False)
    LOG.debug("[%d] URL: %s", r.status_code, r.url)
    r.raise_for_status()
    return r.json()


def _get_points(token, device):
    """Get data prepared for InfluxDB insertion.

    :param str token:
    :param str device: Device id
    :rtype: :py:class:`list`
    :returns: The current data prepared for insertion into InfluxDB.

    """
    devices = _get_devices(token)
    points = []
    for device in devices:
        data = _get_data(token, device)
        LOG.debug("dict: %s", data)
        point = {"measurement": MEASUREMENT, "tags": {"device": device}, "fields": {}}
        for k, v in data["device"].items():
            if k in TAG_KEYS:
                point["tags"][k] = v
            elif k == "lastReading":
                for k, v in data["device"]["lastReading"].items():
                    if k in FIELD_KEYS:
                        point["fields"][k] = float(v)
            elif k in FIELD_KEYS:
                point["fields"][k] = float(v)
            else:
                LOG.warning("Unknown property: '%s': '%s'", k, v)
        points.append(point)
        LOG.debug("Point: %s", point)
    return points


def record(database, port, ssl, username, password):
    """Record current propane data into the database.

    .. note::

       Propane data is recorded at second precision.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :param str username:
    :param str password:
    :rtype: :py:const:`None`
    :return: When the current propane data has been written to the database.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    token = _get_token(username, password)
    for device in _get_devices(token):
        db.write_points(_get_points(token, device), time_precision="s")
