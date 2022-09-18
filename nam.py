import logging.config
import numpy as np
from herbie import Herbie
from numpy import abs, maximum, min, where
from utils import closest_xy_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

FORECAST_HOURS = 36  # NAM 5km goes up to 60 hours but we only need 36 hours max to cover the WxChallenge forecast period.

def get_times(datasets, sample_field=":TMP:2 m"):
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

def get_P_timeseries(datasets, x, y):
    ts = [datasets[h][":APCP:"].tp.data[x, y] for h in range(FORECAST_HOURS+1)]
    return np.array(ts)

def nam_forecast_time_series(forecast_time, target_lat, target_lon, fields=[":TMP:2 m", ":VGRD:10 m", ":APCP:"]):
    products = [Herbie(forecast_time, model="nam", product="conusnest.hiresf", fxx=h) for h in range(FORECAST_HOURS+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    sample_ds = datasets[0][fields[0]]  # We can use any dataset to find the closest x, y.
    x, y = closest_xy_coordinates(sample_ds, target_lat, target_lon, verbose=True)

    timeseries = {}
    timeseries["time"] = get_times(datasets)
    timeseries["T"] = get_T_timeseries(datasets, x, y)
    timeseries["u"] = get_u_timeseries(datasets, x, y)
    timeseries["v"] = get_v_timeseries(datasets, x, y)
    timeseries["P"] = get_P_timeseries(datasets, x, y)

    return timeseries

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = nam_forecast_time_series("2022-09-16 18:00", lat_Boston, lon_Boston)
    print(timeseries)
