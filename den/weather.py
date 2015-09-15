"""Den weather functionality."""

import logging
import os

from influxdb import client as influxdb
import forecastio

try:
    FORECAST_IO_API_KEY = os.environ["DEN_FORECAST_IO_API_KEY"]
    """A `forecast.io API <https://developer.forecast.io/>`_ key."""
except KeyError:
    raise KeyError("Please set the environment variable 'DEN_FORECAST_IO_API_KEY'.")

try:
    LAT = float(os.environ["DEN_LAT"])
    """Latitude"""
except KeyError:
    raise KeyError("Please set the environment variable 'DEN_LAT'.")

try:
    LON = float(os.environ["DEN_LON"])
    """Longitude"""
except KeyError:
    raise KeyError("Please set the environment variable 'DEN_LON'.")


def get_current_data():
    """Get data prepared for InfluxDB insertion.

    :rtype: :py:class:`dict`
    :returns: The current weather data.

    """
    forecast = forecastio.load_forecast(FORECAST_IO_API_KEY, LAT, LON)
    currently = forecast.currently()
    current_data = currently.d
    logging.debug("Weather dict: %s", current_data)
    data = [{"name": "weather", "columns": current_data.keys(), "points": [current_data.values()]}]
    logging.debug("Weather data: %s", data)
    return data


def record(database, port, ssl):
    """Record current weather data into the database.

    :param str database: The name of the database.
    :param int port: The port number the database is listening on.
    :param bool ssl: Whether or not to use SSL to communicate with the database.
    :rtype: :py:const:`None`
    :return: When the current weather data has been written to the database.

    """
    db = influxdb.InfluxDBClient(database=database, port=port, ssl=ssl)
    db.write_points(get_current_data())


if __name__ == "__main__":
    print get_current_data()
