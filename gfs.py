import logging.config
import numpy as np
import pandas as pd
from herbie import Herbie
from herbie.tools import Herbie_latest
from utils import latest_complete_forecast_time, closest_latlon_coordinates, get_times, sample_dataset

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

GFS_FORECAST_HOURS = 36

def get_T_timeseries(datasets, x, y, hours):
    ts = [datasets[h][":TMP:2 m"][0].t2m.data[x, y] for h in range(hours+1)]
    return np.array(ts)

def get_u_timeseries(datasets, x, y, hours):
    ts = [datasets[h][":UGRD:10 m"][0].u10.data[x, y] for h in range(hours+1)]
    return np.array(ts)

def get_v_timeseries(datasets, x, y, hours):
    ts = [datasets[h][":VGRD:10 m"][0].v10.data[x, y] for h in range(hours+1)]
    return np.array(ts)

def gfs_forecast_time_series(forecast_time, target_lat, target_lon, hours=GFS_FORECAST_HOURS, fields=[":TMP:2 m", ":UGRD:10 m", ":VGRD:10 m"]):
    products = [Herbie(forecast_time, model="gfs", product="pgrb2.0p25", fxx=h) for h in range(hours+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    x, y = closest_latlon_coordinates(sample_dataset(datasets), target_lat, target_lon, verbose=True)

    timeseries = {}
    timeseries["time"] = get_times(sample_dataset(datasets), hours)
    timeseries["T"] = get_T_timeseries(datasets, x, y, hours)
    timeseries["u"] = get_u_timeseries(datasets, x, y, hours)
    timeseries["v"] = get_v_timeseries(datasets, x, y, hours)

    return timeseries

def latest_gfs_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=6, model="gfs", product="pgrb2.0p25", forecast_hours=GFS_FORECAST_HOURS)
    return gfs_forecast_time_series(forecast_time, lat_Boston, lon_Boston)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_gfs_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
