"""Common test."""

import os


def _reset_environ():
    """Reset the environment with test values."""
    os.environ["DEN_ACCESS_TOKEN"] = "TEST"
    os.environ["DEN_FORECAST_IO_API_KEY"] = "TEST"
    os.environ["DEN_LAT"] = "39.952447"
    os.environ["DEN_LON"] = "-75.1635083"
