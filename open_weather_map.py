import json
import requests
import logging.config
from datetime import datetime

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Request headers
OWM_HEADERS = {
    "User-Agent": "wxConch (Python3.7) https://github.com/ali-ramadhan/wxConch",
    "From": "alir@mit.edu"
}

# OpenWeatherMap API
OWM_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"


def open_weather_map_temp_time_series(city_id):
    req_params = {
        'APPID': "c7f3d1b2657114c4c2ba33b64b8fa3a7",
        'id': city_id,
        'units': "imperial"
    }

    response = requests.get(OWM_FORECAST_URL, params=req_params)

    if response.status_code != 200:
        response.raise_for_status()

    forecast = json.loads(response.content)

    city_id = forecast['city']['id']
    city_name = forecast['city']['name']
    city_lat = forecast['city']['coord']['lat']
    city_lon = forecast['city']['coord']['lon']
    city_country = forecast['city']['country']

    logger.info("OpenWeatherMap: {:s}, {:s} ({:.4f}°N, {:.4f}°E) [ID: {:d}] "
                 .format(city_name, city_country, city_lat, city_lon, city_id))

    times = []
    temps = []

    for i, forecast_entry in enumerate(forecast['list']):
        t_txt = forecast_entry['dt_txt']
        T = forecast_entry['main']['temp']
        T_min = forecast_entry['main']['temp_min']
        T_max = forecast_entry['main']['temp_max']

        times.append(datetime.strptime(t_txt, "%Y-%m-%d %H:%M:%S"))
        temps.append(T)

        logger.info("{:s} T={:.1f}°F, T_min={:.1f}°F, T_max={:.1f}°F".format(t_txt, T, T_min, T_max))

    return times, temps
