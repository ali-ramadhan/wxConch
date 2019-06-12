import logging.config
from datetime import datetime

import ffmpeg

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
        sounding_filepath = "hrrr_sounding_fh" + str(fh).zfill(2) + ".png"

        logger.info("Downloading sounding: {:s} -> {:s}".format(sounding_url, sounding_filepath))
        download_images(sounding_url, filename=sounding_filepath)


def animate_hrrr_soundings(run, lat, lon):
    download_hrrr_soundings(run, lat, lon)
    sounding_gif_filepath = "hrrr_sounding.gif"
    (
        ffmpeg
        .input("hrrr_sounding_fh%02d.png", framerate=5)
        .output(sounding_gif_filepath)
        .run()
    )
    return sounding_gif_filepath

