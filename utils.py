import os
import logging.config
import pandas as pd

from subprocess import run
from numpy import deg2rad, sin, cos, sqrt, arctan2, abs, maximum, min, where, array, datetime64
from xarray import Dataset
from herbie import Herbie
from herbie.tools import Herbie_latest

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Herbie

def latest_complete_forecast_time(n, freq_hours, model, product, forecast_hours, verbose=True):
    freq = f"{freq_hours}h"
    latest_product = Herbie_latest(n=n, freq=freq, model=model, product=product)

    if verbose:
        logging.info(f"Latest forecast (model={model}, product={product}, freq={freq}): {latest_product.date}")

    max_forecast = Herbie(latest_product.date, model=model, product=product, fxx=forecast_hours)

    if any([max_forecast.grib is not None, max_forecast.idx is not None]):
        forecast_time = latest_product.date
        logging.info("Latest forecast complete.")
    else:
        forecast_time = latest_product.date - pd.Timedelta(freq_hours, "h")
        logging.info(f"Latest forecast not complete. Using forecast from {forecast_time}")

    return forecast_time

# Physics and unit conversions

def K2F(K):
    return (K - 273.15) * (9/5) + 32

def longitude_east_to_west(lon):
    return lon - 360

def haversine_distance(lat1, lon1, lat2, lon2, R=6371.228e3):
    # Calculate the distance between two points on the Earth (lat1, lon1) and (lat2, lon2) using the haversine formula.
    # See: http://www.movable-type.co.uk/scripts/latlong.html

    lat1, lon1, lat2, lon2 = deg2rad([lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon/2)**2
    c = 2 * arctan2(sqrt(a), sqrt(1-a))
    return R*c

# Data wrangling

def closest_xy_coordinates(ds, target_lat, target_lon, verbose=True):
    lats = ds.latitude
    lons = ds.longitude

    abs_lat = abs(lats - target_lat)
    abs_lon = abs(lons - target_lon)
    abs_distance = maximum(abs_lon, abs_lat)

    x, y = where(abs_distance == min(abs_distance))
    x, y = x[0], y[0]

    if verbose:
        closest_lat = lats.data[x, y]
        closest_lon = lons.data[x, y]
        distance = haversine_distance(target_lat, target_lon, closest_lat, closest_lon)

        logging.info(f"Target coordinates: {target_lat:.6f}°N, {target_lon:.6f}°E")
        logging.info(f"Closest coordinates: {closest_lat:.6f}°N, {closest_lon:.6f}°E @ (x={x}, y={y}) (Δ={distance/1000:.3f} km)")

    return x, y

def closest_latlon_coordinates(ds, target_lat, target_lon, verbose=True):
    lats = ds.latitude.data
    lons = ds.longitude.data
    x = abs(lats - target_lat).argmin()
    y = abs(lons - target_lon).argmin()

    if verbose:
        closest_lat = lats[x]
        closest_lon = lons[y]
        distance = haversine_distance(target_lat, target_lon, closest_lat, closest_lon)

        logging.info(f"Target coordinates: {target_lat:.6f}°N, {target_lon:.6f}°E")
        logging.info(f"Closest coordinates: {closest_lat:.6f}°N, {closest_lon:.6f}°E @ (x={x}, y={y}) (Δ={distance/1000:.3f} km)")

    return x, y

# def get_times(ds, hours):
#     times = [datetime64(ds.time.data + ds.step.data) for h in range(hours+1)]
#     return array(times)

def get_times(datasets, hours):
    times = []
    for i in range(len(datasets)):
        ds = sample_dataset(datasets[i])
        time = pd.Timestamp(ds.time.data + ds.step.data)
        times.append(time)
    return times

def get_farenheit_time_series(ts):
    return array([K2F(T) for T in ts])

METERS_PER_SECOND_TO_MILES_PER_HOUR = 3600 / (1000 * 1.609344)

def get_wind_speed_time_series(ts):
    u = ts["u_velocity"]
    v = ts["v_velocity"]
    return sqrt(u**2 + v**2) * METERS_PER_SECOND_TO_MILES_PER_HOUR

# Data wrangling helper functions

def sample_dataset(ds):
    if isinstance(ds, Dataset):
        return ds
    elif isinstance(ds, list):
        return sample_dataset(ds[0])
    elif isinstance(ds, dict):
        keys = list(ds.keys())
        sample_key = keys[0]
        return sample_dataset(ds[sample_key])

# Misc.

def find_nearest(array, value):
    idx = (abs(array - value)).argmin()  # Might have to replace with nanargmin?
    return array[idx]

def download_file(url, local_filepath):
    if not os.path.exists(local_filepath):
        run(["wget", "-nc", url, "-O", local_filepath])

