import logging.config
import numpy as np
from herbie import Herbie
from numpy import abs, maximum, min, where

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

FORECAST_HOURS = 36  # NAM 5km goes up to 60 hours but we only need 36 hours max to cover the WxChallenge forecast period.

field2key = {
    ":TMP:2 m": "t2m",
    ":UGRD:10 m": "u10",
    ":VGRD:10 m": "v10",
    ":APCP:" : "tp"
}

def K2F(K):
    return (K - 273.15) * (9/5) + 32

def haversine_distance(lat1, lon1, lat2, lon2, R=6371.228e3):
    # Calculate the distance between two points on the Earth (lat1, lon1) and (lat2, lon2) using the haversine formula.
    # See: http://www.movable-type.co.uk/scripts/latlong.html

    lat1, lon1, lat2, lon2 = np.deg2rad([lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = np.sin(delta_lat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R*c

def closest_hrrr_xy_coordinates(ds, target_lat, target_lon, verbose=True):
    lats = ds.latitude
    lons = ds.longitude

    abs_lat = abs(lats - target_lat)
    abs_lon = abs(lons - target_lon)
    abs_distance = maximum(abs_lon, abs_lat)

    x_idx, y_idx = where(abs_distance == min(abs_distance))
    x_idx, y_idx = x_idx[0], y_idx[0]

    closest_lat = lats.data[x_idx, y_idx]
    closest_lon = lons.data[x_idx, y_idx]

    distance = haversine_distance(target_lat, target_lon, closest_lat, closest_lon)

    logging.info(f"Target coordinates: {target_lat:.6f}°N, {target_lon:.6f}°E")
    logging.info(f"Closest coordinates: {closest_lat:.6f}°N, {closest_lon:.6f}°E @ (x={x_idx}, y={y_idx}) (Δ={distance/1000:.3f} km)")

    return x_idx, y_idx

def get_times(datasets):
    sample_field = fields[0]  # We can use any dataset to find the times.
    times = [np.datetime64(datasets[h][sample_field].time.data + datasets[h][sample_field].step.data) for h in range(FORECAST_HOURS+1)]
    return np.array(times)

def get_T_timeseries(datasets, x, y):
    ts = [datasets[h][":TMP:2 m"].t2m.data[x, y] for h in range(FORECAST_HOURS+1)]
    return np.array(ts)

def get_u_timeseries(datasets, x, y):
    ts = [datasets[h][":VGRD:10 m"][0].u10.data[x, y] for h in range(FORECAST_HOURS+1)]
    return np.array(ts)

def get_v_timeseries(datasets, x, y):
    ts = [datasets[h][":VGRD:10 m"][0].v10.data[x, y] for h in range(FORECAST_HOURS+1)]
    return np.array(ts)

def nam_forecast_time_series(forecast_time, target_lat, target_lon, fields=[":TMP:2 m", ":VGRD:10 m"]):
    products = [Herbie(forecast_time, model="nam", product="conusnest.hiresf", fxx=h) for h in range(FORECAST_HOURS+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    sample_ds = datasets[0][fields[0]]  # We can use any dataset to find the closest x, y.
    x_hrrr, y_hrrr = closest_hrrr_xy_coordinates(sample_ds, target_lat, target_lon, verbose=True)

    timeseries = {}
    timeseries["time"] = get_times(datasets)
    timeseries["T"] = get_T_timeseries(datasets, x_hrrr, y_hrrr)
    timeseries["u"] = get_u_timeseries(datasets, x_hrrr, y_hrrr)
    timeseries["v"] = get_v_timeseries(datasets, x_hrrr, y_hrrr)

    return timeseries

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = nam_forecast_time_series("2022-09-16 18:00", lat_Boston, lon_Boston)
    print(timeseries)
