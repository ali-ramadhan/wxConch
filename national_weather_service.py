import json
import requests
import logging.config
from dateutil.parser import parse
from utils import longitude_east_to_west

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def nws_time_series(lat, lon):
    lon = longitude_east_to_west(lon)

    api_url = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
    response = requests.get(api_url)

    if response.status_code != 200:
        response.raise_for_status()

    point = json.loads(response.content)

    wfo = point['properties']['cwa']
    X = point['properties']['gridX']
    Y = point['properties']['gridY']
    forecast_url = point['properties']['forecast']
    hourly_forecast_url = point['properties']['forecastHourly']

    logger.info("National Weather Service: WFO={:s}, (X,Y)=({:d},{:d})".format(wfo, X, Y))
    logger.info("Forecast URL: {:s}".format(forecast_url))
    logger.info("Hourly forecast URL: {:s}".format(hourly_forecast_url))

    response = requests.get(hourly_forecast_url)
    hourly_forecast = json.loads(response.content)

    periods = hourly_forecast["properties"]["periods"]
    n_periods = len(periods)

    timeseries = {
        "times": [periods[p]["startTime"] for p in range(n_periods)],
        "temperature_F": [periods[p]["temperature"] for p in range(n_periods)],
        "wind_speed": [periods[p]["windSpeed"] for p in range(n_periods)]
    }

    return timeseries
