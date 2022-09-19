import logging.config
import numpy as np
from herbie import Herbie
from utils import latest_complete_forecast_time, closest_xy_coordinates, get_times, get_farenheit_time_series, get_wind_speed_time_series, sample_dataset

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

HRRR_FORECAST_HOURS = 18
HRRR_SUBHOURLY_OUTPUTS = 4

field2key = {
    ":TMP:2 m": "temperature_K",
    ":UGRD:10 m": "u_velocity",
    ":VGRD:10 m": "v_velocity",
    ":APCP:" : "precipitation"
}

field2dskey = {
    ":TMP:2 m": "t2m",
    ":UGRD:10 m": "u10",
    ":VGRD:10 m": "v10",
    ":APCP:" : "tp"
}

def hrrr_forecast_time_series(forecast_time, target_lat, target_lon, hours=HRRR_FORECAST_HOURS, fields=[":TMP:2 m", ":UGRD:10 m", ":VGRD:10 m", ":APCP:"]):
    products = [Herbie(forecast_time, model="hrrr", product="sfc", fxx=h) for h in range(hours+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    x, y = closest_xy_coordinates(sample_dataset(datasets), target_lat, target_lon, verbose=True)

    timeseries = {
        field2key[field]: np.array([datasets[h][field][field2dskey[field]].data[x, y] for h in range(hours+1)]) for field in fields
    }

    timeseries["time"] = get_times(datasets)
    timeseries["temperature_F"] = get_farenheit_time_series(timeseries["temperature_K"])
    timeseries["wind_speed"] = get_wind_speed_time_series(timeseries)

    return timeseries

def latest_hrrr_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=1, model="hrrr", product="sfc", forecast_hours=HRRR_FORECAST_HOURS)
    return hrrr_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_hrrr_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
