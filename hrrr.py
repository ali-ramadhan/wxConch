from datetime import datetime

import xarray as xr
from numpy import abs, maximum, min, where

from utils import download_file

# Configure logger first before importing any sub-module that depend on the logger being already configured.
import logging.config
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def hrrr_file_url(date, CC, FF):
    """
    HRRR 2D surface data file names are hrrr.tCCz.wrfsubhfFF.grib2 where CC is the model cycle runtime (i.e. 00, 01,
    02, 03) and FF is the forecast hour (i.e. 00, 03, 06, 12, 15).
    """

    date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    filename = "hrrr.t" + str(CC).zfill(2) + "z.wrfsubhf" + str(FF).zfill(2) + ".grib2"
    url = "https://ftp.ncep.noaa.gov/data/nccf/com/hrrr/prod/hrrr." + date_str + "/conus/" + filename
    return url, filename


def hrrr_temp_time_series(slat, slon):
    hrrr_url, hrrr_filename = hrrr_file_url(datetime.now(), 10, 1)
    download_file(hrrr_url, hrrr_filename)

    ds = xr.open_dataset(hrrr_filename, engine="pynio")

    lats = ds["gridlat_0"].data
    lons = ds["gridlon_0"].data

    abslat = abs(lats - slat)
    abslon = abs(lons - slon)
    c = maximum(abslon, abslat)

    x_idx, y_idx = where(c == min(c))
    x_idx, y_idx = x_idx[0], y_idx[0]

    clat, clon = lats[x_idx, y_idx], lons[x_idx, y_idx]

    logger.info("Station (lat, lon) = ({:.6f}, {:.6f})".format(slat, slon))
    logger.info("Closest (lat, lon) = ({:.6f}, {:.6f})".format(clat, clon))


if __name__ == "__main__":
    hrrr_temp_time_series(42.362389, -71.091083)
