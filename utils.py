import logging.config
import numpy as np
import pandas as pd

from datetime import datetime
from subprocess import run
from numpy import deg2rad, sin, cos, sqrt, arctan2, abs, maximum, min, where, array, datetime64
from xarray import Dataset
from herbie import Herbie
from herbie.tools import Herbie_latest

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

METERS_PER_SECOND_TO_KNOTS = 1.943844  # See https://en.wikipedia.org/wiki/Knot_(unit)#Definitions

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

# Time wrangling

def compute_6Z_times(forecast_time=datetime.utcnow()):
    utc_today = pd.Timestamp(datetime(forecast_time.year, forecast_time.month, forecast_time.day))
    first_6Z = utc_today + pd.Timedelta(days=1, hours=6)
    second_6Z = utc_today + pd.Timedelta(days=2, hours=6)
    return first_6Z, second_6Z

# Physics and unit conversions

def K2F(K):
    return (K - 273.15) * (9/5) + 32

def uv2knots(u, v):
    return sqrt(u**2 + v**2) * METERS_PER_SECOND_TO_KNOTS

# Location and distance wrangling

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

# Time series wrangling

def timeseries_max(ts):
    t = ts.index
    S = ts.values

    i_max = np.argmax(S)
    t_max = t[i_max]
    S_max = S[i_max]

    return t_max, S_max

def timeseries_min_and_max(ts):
    t = ts.index
    S = ts.values

    i_min = np.argmin(S)
    i_max = np.argmax(S)
    t_min = t[i_min]
    t_max = t[i_max]
    S_min = S[i_min]
    S_max = S[i_max]

    return t_min, S_min, t_max, S_max
