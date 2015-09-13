"""Den weather functionality."""

import os

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


def get_current():
    """Get the current weather data.

    :rtype: A ``ForecastioDataPoint`` object.
    :returns: The current weather data.

    """
    forecast = forecastio.load_forecast(FORECAST_IO_API_KEY, LAT, LON)
    return forecast.currently()
