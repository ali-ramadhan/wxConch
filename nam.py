import logging.config
import numpy as np
import pandas as pd
import xarray as xr
from herbie import Herbie
from utils import K2F, uv2knots, latest_complete_forecast_time, closest_xy_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

NAM_FORECAST_HOURS = 48  # NAM 5km goes up to 60 hours but we only need 48 hours max to cover the WxChallenge forecast period.

def merge_nam_fields(product):
    # We drop the heightAboveGround coordinate since T is at 2m and u,v are at 10m.
    # We just want to merge the datasets and don't need to keep track of z location.
    T = product.xarray(":TMP:2 m").drop_vars("heightAboveGround")
    uv = product.xarray(":VGRD:10 m")[0].drop_vars("heightAboveGround")  # we want the dataset at index 0 which uses heightAboveGround
    P = product.xarray(":APCP:").drop_vars("surface")

    return xr.merge([T, uv, P])

def nam_forecast_dataset(forecast_time, fields, hours):
    products = [Herbie(forecast_time, model="nam", product="conusnest.hiresf", fxx=h) for h in range(hours+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    ds = xr.concat([merge_nam_fields(product) for product in products], dim="step")
    return ds

def nam_forecast_time_series(forecast_time, target_lat, target_lon, hours=NAM_FORECAST_HOURS, fields=[":TMP:2 m", ":VGRD:10 m", ":APCP:"]):
    ds = nam_forecast_dataset(forecast_time, fields, hours)

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

def latest_nam_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=24, freq_hours=1, model="nam", product="conusnest.hiresf", forecast_hours=NAM_FORECAST_HOURS)
    return nam_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_nam_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
