import logging
from datetime import datetime

import xarray as xr
from numpy import abs, maximum, min, where

from utils import download_file

logging.basicConfig(format="[%(asctime)s.%(msecs)03d] %(funcName)s:%(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def hrrr_file_url(date, CC, FF):
    """
    HRRR 2D surface data file names are hrrr.tCCz.wrfsubhfFF.grib2 where CC is the model cycle runtime (i.e. 00, 01,
    02, 03) and FF is the forecast hour (i.e. 00, 03, 06, 12, 15).
    """

    date_str = str(date.year) + str(date.month) + str(date.day)
    filename = "hrrr.t" + str(CC) + "z.wrfsubhf" + str(FF) + ".grib2"
    url = "https://ftp.ncep.noaa.gov/data/nccf/com/hrrr/prod/hrrr." + date_str + "/conus/" + filename
    return url, filename


hrrr_url, hrrr_filename = hrrr_file_url(datetime.now(), 10, 1)
download_file(hrrr_url, hrrr_filename)

ds = xr.open_dataset(hrrr_filename, engine="pynio")

lats = ds["gridlat_0"].data
lons = ds["gridlon_0"].data

slat, slon = 42.362389, -71.091083

abslat = abs(lats - slat)
abslon = abs(lons - slon)
c = maximum(abslon, abslat)

x_idx, y_idx = where(c == min(c))
x_idx, y_idx = x_idx[0], y_idx[0]

clat, clon = lats[x_idx, y_idx], lons[x_idx, y_idx]

logging.info("Station (lat, lon) = ({:.6f}, {:.6f})".format(slat, slon))
logging.info("Closest (lat, lon) = ({:.6f}, {:.6f})".format(clat, clon))
