"""Record weather data to InfluxDB."""

from influxdb import client as influxdb
import forecastio

from . import LOG

MEASUREMENT = "weather"
"""InfluxDB measurement value."""

TAG_KEYS = ["icon", "precipType"]
"""InfluxDB tag keys."""

FIELD_KEYS = [
    "apparentTemperature", "cloudCover", "dewPoint", "humidity", "nearestStormBearing", "nearestStormDistance",
    "ozone", "precipIntensity", "precipProbability", "pressure", "temperature", "time", "visibility", "windBearing",
    "windSpeed"
]
"""InfluxDB field keys."""


def _get_weather_points(api_key, lat, lon):
    """Get data prepared for InfluxDB insertion.

    :param str api_key:
    :param float lat: Latitude
    :param float lon: Longitude
    :rtype: :py:class:`list`
    :returns: The current weather data prepared for insertion into InfluxDB.

    """
    forecast = forecastio.load_forecast(api_key, lat, lon)
    currently = forecast.currently()
    current_data = currently.d
    LOG.debug("Weather dict: %s", current_data)
    point = {"measurement": MEASUREMENT, "tags": {}, "fields": {}}
    for k, v in current_data.items():
        if k in TAG_KEYS:
            point["tags"][k] = v
        elif k in FIELD_KEYS:
            point["fields"][k] = float(v)
        else:
            LOG.warning("Weather unknown property: '%s': '%s'", k, v)
    LOG.debug("Weather point: %s", point)
    return [point]


def record(database, port, ssl, api_key, lat, lon):
    """Record current weather data into the database.

    .. note::

       Weather data is recorded at second precision.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :param str api_key:
    :param float lat: Latitude
    :param float lon: Longitude
    :rtype: :py:const:`None`
    :return: When the current weather data has been written to the database.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    db.write_points(_get_weather_points(api_key, lat, lon), time_precision="s")
