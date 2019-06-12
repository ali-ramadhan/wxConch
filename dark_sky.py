import json
import requests
from datetime import datetime

# Configure logger first before importing any sub-module that depend on the logger being already configured.
import logging.config
logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

# Dark Sky API
DARK_SKY_KEY = "81c07948c439765d630c4c60fc56634e"


def dark_sky_temp_time_series(lat, lon):
    forecast_url = "https://api.darksky.net/forecast/" + DARK_SKY_KEY + "/" + str(lat) + "," + str(lon)
    response = requests.get(forecast_url)
    
    if response.status_code != 200:
        response.raise_for_status()
    
    forecast = json.loads(response.content)

    city_lat = forecast['latitude']
    city_lon = forecast['longitude']
    city_tz = forecast['timezone']

    logger.info("Dark Sky: (lat, lon) = ({:.2f}, {:.2f}), timezone={:}".format(city_lat, city_lon, city_tz))

    currently = forecast['currently']
    current_time = currently['time']
    summary = currently['summary']
    nearest_storm_distance = currently['nearestStormDistance']
    precip_intensity = currently['precipIntensity']
    precip_prob = currently['precipProbability']
    T = currently['temperature']
    T_apparent = currently['apparentTemperature']
    dew_point = currently['dewPoint']
    humidity = currently['humidity']
    pressure = currently['pressure']
    wind_speed = currently['windSpeed']
    wind_gust = currently['windGust']
    wind_bearing = currently['windBearing']
    cloud_cover = currently['cloudCover']
    uv_index = currently['uvIndex']
    visibility = currently['visibility']

    times = []
    temps = []

    hourly_forecast = forecast['hourly']['data']
    for i, forecast in enumerate(hourly_forecast):
        time = datetime.utcfromtimestamp(forecast['time'])
        summary = forecast['summary']
        precip_intensity = forecast['precipIntensity']
        precip_prob = forecast['precipProbability']
        T = forecast['temperature']
        T_apparent = forecast['apparentTemperature']
        dew_point = forecast['dewPoint']
        humidity = forecast['humidity']
        pressure = forecast['pressure']
        wind_speed = forecast['windSpeed']
        wind_gust = forecast['windGust']
        wind_bearing = forecast['windBearing']
        cloud_cover = forecast['cloudCover']
        uv_index = forecast['uvIndex']
        visibility = forecast['visibility']
    
        times.append(time)
        temps.append(T)

    return times, temps
