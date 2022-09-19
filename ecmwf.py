import logging.config
import numpy as np
import pandas as pd
from herbie import Herbie
from utils import latest_complete_forecast_time, longitude_east_to_west, closest_latlon_coordinates, get_times, get_farenheit_time_series, get_wind_speed_time_series, sample_dataset

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

ECMWF_FORECAST_HOURS = 60
ECMWF_FORECAST_SPACING = 3  # hours

field2key = {
    ":2t:": "temperature_K",
    ":10u:": "u_velocity",
    ":10v:": "v_velocity",
    ":tp:" : "precipitation"
}

field2dskey = {
    ":2t:": "t2m",
    ":10u:": "u10",
    ":10v:": "v10",
    ":tp:" : "tp"
}

def ecmwf_forecast_time_series(forecast_time, target_lat, target_lon, hours=ECMWF_FORECAST_HOURS, fields=[":2t:", ":10u:", ":10v:", ":tp:"]):
    target_lon = longitude_east_to_west(target_lon)
    hours_range = range(0, hours+1, ECMWF_FORECAST_SPACING)

    products = [Herbie(forecast_time, model="ecmwf", product="oper", fxx=h) for h in hours_range]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    x, y = closest_latlon_coordinates(sample_dataset(datasets), target_lat, target_lon, verbose=True)

    timeseries = {
        field2key[field]: np.array([datasets[h][field][field2dskey[field]].data[x, y] for h in range(len(hours_range))]) for field in fields
    }

    timeseries["time"] = get_times(datasets)
    timeseries["temperature_F"] = get_farenheit_time_series(timeseries["temperature_K"])
    timeseries["wind_speed"] = get_wind_speed_time_series(timeseries)

    return timeseries

def latest_ecmwf_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=6, model="ecmwf", product="oper", forecast_hours=ECMWF_FORECAST_HOURS)
    return ecmwf_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_ecmwf_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
