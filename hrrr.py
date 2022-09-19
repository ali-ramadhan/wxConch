import logging.config
import numpy as np
import pandas as pd
import xarray as xr
from herbie import Herbie
from utils import K2F, uv2knots, latest_complete_forecast_time, closest_xy_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

HRRR_FORECAST_HOURS = 18
HRRR_SUBHOURLY_OUTPUTS = 4

def merge_hrrr_fields(product):
    # We drop the heightAboveGround coordinate since T is at 2m and u,v are at 10m.
    # We just want to merge the datasets and don't need to keep track of z location.
    T = product.xarray(":TMP:2 m").drop_vars("heightAboveGround")
    u = product.xarray(":UGRD:10 m").drop_vars("heightAboveGround")
    v = product.xarray(":VGRD:10 m").drop_vars("heightAboveGround")
    P = product.xarray(":APCP:").drop_vars("surface")

    return xr.merge([T, u, v, P])

def hrrr_forecast_dataset(forecast_time, fields, hours):
    products = [Herbie(forecast_time, model="hrrr", product="sfc", fxx=h) for h in range(hours+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    ds = xr.concat([merge_hrrr_fields(product) for product in products], dim="step")
    return ds

def hrrr_forecast_time_series(forecast_time, target_lat, target_lon, hours=HRRR_FORECAST_HOURS, fields=[":TMP:2 m", ":UGRD:10 m", ":VGRD:10 m", ":APCP:"]):
    ds = hrrr_forecast_dataset(forecast_time, fields, hours)

    x, y = closest_xy_coordinates(ds, target_lat, target_lon, verbose=True)

    model_times = ds.time + ds.step

    temperature_K = ds.t2m.isel(x=y, y=x)
    temperature = K2F(temperature_K)

    u = ds.u10.isel(x=y, y=x)
    v = ds.v10.isel(x=y, y=x)
    wind_speed = uv2knots(u, v)

    precipitation = ds.tp.isel(x=y, y=x)

    timeseries = pd.DataFrame({
        "temperature": temperature,
        "wind_speed": wind_speed,
        "precipitation": precipitation
    }, index=model_times)

    return timeseries

def latest_hrrr_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=1, model="hrrr", product="sfc", forecast_hours=HRRR_FORECAST_HOURS)
    return hrrr_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_hrrr_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
