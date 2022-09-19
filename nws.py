import json
import requests
import logging.config
import pandas as pd
from utils import longitude_east_to_west

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

MILES_PER_HOUR_TO_KNOTS = 0.868976  # See https://en.wikipedia.org/wiki/Knot_(unit)#Definitions

def nws_forecast_time_series(lat, lon):
    lon = longitude_east_to_west(lon)

    api_url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(api_url)

    if response.status_code != 200:
        response.raise_for_status()

    point = json.loads(response.content)

    wfo = point["properties"]["cwa"]
    X = point["properties"]["gridX"]
    Y = point["properties"]["gridY"]
    forecast_url = point["properties"]["forecast"]
    hourly_forecast_url = point["properties"]["forecastHourly"]

    logger.info(f"National Weather Service: WFO={wfo}, (X,Y)=({X},{Y})")
    logger.info(f"Forecast URL: {forecast_url}")
    logger.info(f"Hourly forecast URL: {hourly_forecast_url}")

    response = requests.get(hourly_forecast_url)
    hourly_forecast = json.loads(response.content)

    periods = hourly_forecast["properties"]["periods"]
    n_periods = len(periods)

    times = [pd.Timestamp(periods[p]["startTime"]).tz_convert("UTC").tz_localize(None) for p in range(n_periods)]
    temperature = [periods[p]["temperature"] for p in range(n_periods)]
    wind_speed = [MILES_PER_HOUR_TO_KNOTS * float(periods[p]["windSpeed"].split()[0]) for p in range(n_periods)]

    timeseries = pd.DataFrame({
        "temperature": temperature,
        "wind_speed": wind_speed,
    }, index=times)

    return timeseries

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = nws_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
