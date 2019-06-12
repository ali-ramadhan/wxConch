import logging.config
from datetime import datetime, timedelta

import xarray as xr
from numpy import abs, maximum, min, where

from utils import download_file, K2F


logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

FORECAST_HOURS = 18
SUBHOURLY = 4


def hrrr_file_url(date, CC, FF):
    """
    HRRR 2D surface data file names are hrrr.tCCz.wrfsubhfFF.grib2 where CC is the model cycle runtime (i.e. 00, 01,
    02, 03) and FF is the forecast hour (i.e. 00, 03, 06, 12, 15).
    """

    date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    filename = "hrrr.t" + str(CC).zfill(2) + "z.wrfsubhf" + str(FF).zfill(2) + ".grib2"
    url = "https://ftp.ncep.noaa.gov/data/nccf/com/hrrr/prod/hrrr." + date_str + "/conus/" + filename
    return url, filename


def hrrr_temp_time_series(slat, slon, CC=10):
    today = datetime.utcnow().date()
    today_dt = datetime.combine(today, datetime.min.time())

    for FF in range(FORECAST_HOURS+1):
        hrrr_url, hrrr_filename = hrrr_file_url(today, CC, FF)
        download_file(hrrr_url, hrrr_filename)

    # Get lat, lon index from first forecast hour file.
    _, FF0_filename = hrrr_file_url(datetime.now(), CC, 0)
    logger.info("Reading data from {:s}...".format(FF0_filename))
    ds0 = xr.open_dataset(FF0_filename, engine="pynio")

    lats = ds0["gridlat_0"].data
    lons = ds0["gridlon_0"].data

    abslat = abs(lats - slat)
    abslon = abs(lons - slon)
    c = maximum(abslon, abslat)

    x_idx, y_idx = where(c == min(c))
    x_idx, y_idx = x_idx[0], y_idx[0]

    clat, clon = lats[x_idx, y_idx], lons[x_idx, y_idx]

    logger.info("Station (lat, lon) = ({:.6f}, {:.6f})".format(slat, slon))
    logger.info("Closest (lat, lon) = ({:.6f}, {:.6f})".format(clat, clon))

    times = []
    temps = []

    # Get first temperature data point.
    T = K2F(ds0["TMP_P0_L103_GLC0"].data[x_idx, y_idx])
    temps.append(T)
    times.append(today_dt + timedelta(hours=CC))  # UTC time

    # Get temperature time series.
    for FF in range(1, FORECAST_HOURS+1):
        _, FF_filename = hrrr_file_url(datetime.now(), CC, FF)
        logger.info("Reading data from {:s}...".format(FF_filename))
        ds = xr.open_dataset(FF_filename, engine="pynio")

        for subhourly_idx in range(SUBHOURLY):
            T = K2F(ds["TMP_P0_L103_GLC0"].data[subhourly_idx, x_idx, y_idx])
            temps.append(T)
            times.append(times[-1] + timedelta(minutes=15))

    return times, temps
