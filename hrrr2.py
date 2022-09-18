import logging.config
import numpy as np
from herbie import Herbie
from herbie.tools import Herbie_latest
from utils import closest_xy_coordinates

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


FORECAST_HOURS = 18
SUBHOURLY_OUTPUTS = 4

field2key = {
    ":TMP:2 m": "t2m",
    ":UGRD:10 m": "u10",
    ":VGRD:10 m": "v10",
    ":APCP:" : "tp"
}

def hrrr_forecast_time_series(forecast_time, target_lat, target_lon, fields=[":TMP:2 m", ":UGRD:10 m", ":VGRD:10 m", ":APCP:"]):
    products = [Herbie(forecast_time, model="hrrr", product="sfc", fxx=h) for h in range(FORECAST_HOURS+1)]
    [product.download(field, verbose=True) for field in fields for product in products]
    datasets = [{field: product.xarray(field) for field in fields} for product in products]

    sample_ds = datasets[0][fields[0]]  # We can use any dataset to find the closest x, y.
    x, y = closest_xy_coordinates(sample_ds, target_lat, target_lon, verbose=True)

    timeseries = {field: np.array([datasets[h][field][field2key[field]].data[x, y] for h in range(FORECAST_HOURS+1)]) for field in fields}
    timeseries["time"] = np.array([np.datetime64(datasets[h][fields[0]].time.data) for h in range(FORECAST_HOURS+1)])

    return timeseries

if __name__ == "__main__":
    # Testing @ Boston
    lat_Boston, lon_Boston = 42.362389, 288.908917
    timeseries = hrrr_forecast_time_series("2022-09-16 16:00", lat_Boston, lon_Boston)
    print(timeseries)
