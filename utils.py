import os
import logging.config
from subprocess import run
from numpy import deg2rad, sin, cos, sqrt, arctan2, abs, maximum, min, where

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def K2F(K):
    return (K - 273.15) * (9/5) + 32

def haversine_distance(lat1, lon1, lat2, lon2, R=6371.228e3):
    # Calculate the distance between two points on the Earth (lat1, lon1) and (lat2, lon2) using the haversine formula.
    # See: http://www.movable-type.co.uk/scripts/latlong.html

    lat1, lon1, lat2, lon2 = deg2rad([lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon/2)**2
    c = 2 * arctan2(sqrt(a), sqrt(1-a))
    return R*c

def closest_xy_coordinates(ds, target_lat, target_lon, verbose=True):
    lats = ds.latitude
    lons = ds.longitude

    abs_lat = abs(lats - target_lat)
    abs_lon = abs(lons - target_lon)
    abs_distance = maximum(abs_lon, abs_lat)

    x, y = where(abs_distance == min(abs_distance))
    x, y = x[0], y[0]

    closest_lat = lats.data[x, y]
    closest_lon = lons.data[x, y]

    distance = haversine_distance(target_lat, target_lon, closest_lat, closest_lon)

    if verbose:
        logging.info(f"Target coordinates: {target_lat:.6f}°N, {target_lon:.6f}°E")
        logging.info(f"Closest coordinates: {closest_lat:.6f}°N, {closest_lon:.6f}°E @ (x={x}, y={y}) (Δ={distance/1000:.3f} km)")

    return x, y

def download_file(url, local_filepath):
    if not os.path.exists(local_filepath):
        run(["wget", "-nc", url, "-O", local_filepath])

