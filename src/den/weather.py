"""Record `forecast.io <http://forecast.io>`_ weather data to InfluxDB."""

import logging

from influxdb import client as influxdb
import forecastio


def get_current_data(api_key, lat, lon):
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
    logging.debug("Weather dict: %s", current_data)
    data = [{"name": "weather", "columns": list(current_data.keys()), "points": [list(current_data.values())]}]
    logging.debug("Weather data: %s", data)
    return data


def record(database, port, ssl, api_key, lat, lon):
    """Record current weather data into the database.

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
    db.write_points(get_current_data(api_key, lat, lon))
