import logging.config
import numpy as np
import pandas as pd
import xarray as xr
from herbie import Herbie
from utils import K2F, uv2knots, latest_complete_forecast_time, closest_latlon_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

GFS_FORECAST_HOURS = 48

def merge_gfs_fields(product):
    # We drop the heightAboveGround coordinate since T is at 2m and u,v are at 10m.
    # We just want to merge the datasets and don't need to keep track of z location.
    # Index 0 is the one with height coordinates so we pick it.
    T = product.xarray(":TMP:2 m")[0].drop_vars("heightAboveGround")
    u = product.xarray(":UGRD:10 m")[0].drop_vars("heightAboveGround")
    v = product.xarray(":VGRD:10 m")[0].drop_vars("heightAboveGround")

    return xr.merge([T, u, v])

def gfs_forecast_dataset(forecast_time, fields, hours):
    products = [Herbie(forecast_time, model="gfs", product="pgrb2.0p25", fxx=h) for h in range(hours+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    ds = xr.concat([merge_gfs_fields(product) for product in products], dim="step")
    return ds

def gfs_forecast_time_series(forecast_time, target_lat, target_lon, hours=GFS_FORECAST_HOURS, fields=[":TMP:2 m", ":UGRD:10 m", ":VGRD:10 m"]):
    ds = gfs_forecast_dataset(forecast_time, fields, hours)

    x, y = closest_latlon_coordinates(ds, target_lat, target_lon, verbose=True)

    model_times = ds.time + ds.step

    temperature_K = ds.t2m.isel(latitude=x, longitude=y)
    temperature = K2F(temperature_K)

    u = ds.u10.isel(latitude=x, longitude=y)
    v = ds.v10.isel(latitude=x, longitude=y)
    wind_speed = uv2knots(u, v)

    timeseries = pd.DataFrame({
        "temperature": temperature,
        "wind_speed": wind_speed
    }, index=model_times)

    return timeseries

def latest_gfs_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=6, model="gfs", product="pgrb2.0p25", forecast_hours=GFS_FORECAST_HOURS)
    return gfs_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_gfs_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
