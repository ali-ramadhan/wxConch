import logging.config
import numpy as np
import pandas as pd
import xarray as xr
from herbie import Herbie
from utils import longitude_east_to_west, K2F, uv2knots, latest_complete_forecast_time, closest_latlon_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

ECMWF_FORECAST_HOURS = 60
ECMWF_FORECAST_SPACING = 3  # hours

def merge_ecmwf_fields(product):
    # We drop the heightAboveGround coordinate since T is at 2m and u,v are at 10m.
    # We just want to merge the datasets and don't need to keep track of z location.
    T = product.xarray(":2t:").drop_vars("heightAboveGround")
    u = product.xarray(":10u:").drop_vars("heightAboveGround")
    v = product.xarray(":10v:").drop_vars("heightAboveGround")
    P = product.xarray(":tp:").drop_vars("surface")

    return xr.merge([T, u, v, P])

def ecmwf_forecast_dataset(forecast_time, fields, hours_range):
    products = [Herbie(forecast_time, model="ecmwf", product="oper", fxx=h) for h in hours_range]
    [product.download(field, verbose=True) for field in fields for product in products]
    ds = xr.concat([merge_ecmwf_fields(product) for product in products], dim="step")
    return ds

def ecmwf_forecast_time_series(forecast_time, target_lat, target_lon, hours=ECMWF_FORECAST_HOURS, fields=[":2t:", ":10u:", ":10v:", ":tp:"]):
    target_lon = longitude_east_to_west(target_lon)

    hours_range = range(0, hours+1, ECMWF_FORECAST_SPACING)
    ds = ecmwf_forecast_dataset(forecast_time, fields, hours_range)
    x, y = closest_latlon_coordinates(ds, target_lat, target_lon, verbose=True)

    model_times = ds.time + ds.step

    temperature_K = ds.t2m.isel(latitude=x, longitude=y)
    temperature = K2F(temperature_K)

    u = ds.u10.isel(latitude=x, longitude=y)
    v = ds.v10.isel(latitude=x, longitude=y)
    wind_speed = uv2knots(u, v)

    precipitation = ds.tp.isel(latitude=x, longitude=y)

    timeseries = pd.DataFrame({
        "temperature": temperature,
        "wind_speed": wind_speed,
        "precipitation": precipitation
    }, index=model_times)

    return timeseries

def latest_ecmwf_forecast_time_series(lat, lon):
    forecast_time = latest_complete_forecast_time(n=6, freq_hours=12, model="ecmwf", product="oper", forecast_hours=ECMWF_FORECAST_HOURS)
    return ecmwf_forecast_time_series(forecast_time, lat, lon)

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = latest_ecmwf_forecast_time_series(lat_Boston, lon_Boston)
    print(timeseries)
