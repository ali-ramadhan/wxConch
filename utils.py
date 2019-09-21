import os
import time
import math
import logging.config
from datetime import datetime
from subprocess import run
from urllib.parse import urlparse, urljoin

import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from bs4 import BeautifulSoup
from tqdm import tqdm

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


HEADERS = {
    "User-Agent": "wxConch (Python3.7) https://github.com/ali-ramadhan/wxConch",
    "From": "alir@mit.edu"
}


def K2F(K):
    return (K - 273.15) * (9/5) + 32

def download_file(url, local_filepath):
    run(["wget", "-nc", url, "-O", local_filepath])

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, features="lxml")


def download_images(url, filename=None):
    soup = make_soup(url)

    # Make a list of bs4 element tags.
    images = [img for img in soup.findAll("img")]
    logger.debug("{:s}: {:d} images found.".format(url, len(images)))

    # Compile our unicode list of image links.
    image_links = [img.get("src") for img in images]

    for img_url in image_links:
        if filename is None:
            filename = img_url.split('/')[-1]

        url_parts = urlparse(url)
        real_img_url = url_parts.scheme + "://" + url_parts.netloc + img_url

        logger.debug("Downloading image: {:s} -> {:s}".format(real_img_url, filename))
        # urlretrieve(real_img_url, filename)
        download_file(real_img_url, filename)

    return image_links


def send_email(send_from, send_to, subject, text, files=None, gmail="wxconch.forecast@gmail.com"):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"] = COMMASPACE.join(send_to)
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=basename(f))

        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    port = 465  # For SSL
    password = input("Gmail password for {:s}: ".format(gmail))

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(gmail, password)
        server.sendmail(send_from, send_to, msg.as_string())
