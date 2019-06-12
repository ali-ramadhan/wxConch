import logging.config
from datetime import datetime

from utils import download_images

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

HRRR_SOUNDING_HOURS = 12


def hrrr_sounding_img_url(run, fh, lat, lon):
    runtime_str = str(run.year) + str(run.month).zfill(2) + str(run.day).zfill(2) + str(run.hour).zfill(2)
    return "https://www.tropicaltidbits.com/analysis/models/sounding/?model=hrrr" \
           + "&runtime=" + runtime_str \
           + "&fh=" + str(fh) \
           + "&lat=" + str(lat) \
           + "&lon=" + str(lon) \
           + "&stationID=&tc=&mode=regular"


def download_hrrr_soundings(run, lat, lon):
    for fh in range(HRRR_SOUNDING_HOURS):
        sounding_url = hrrr_sounding_img_url(run, fh, lat, lon)

        logger.info("Downloading sounding: {:s}".format(sounding_url))
        download_images(sounding_url, filename="hrrr_sounding_fh" + str(fh).zfill(2) + ".png")


if __name__ == "__main__":
    lat, lon = 42.362389, -71.091083
    download_hrrr_soundings(datetime(2019, 6, 12, 12), lat, lon)
