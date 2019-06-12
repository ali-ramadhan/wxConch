import os
import time
import math
import requests
import logging.config
from datetime import datetime

import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from tqdm import tqdm

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


HEADERS = {
    "User-Agent": "wxConch (Python3.7) https://github.com/ali-ramadhan/wxConch",
    "From": "alir@mit.edu"
}


def send_email(send_from, send_to, subject, text, files=None):
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
    password = input("Gmail password for {:s}: ".format(send_from))

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(send_from, password)
        server.sendmail(send_from, send_to, msg.as_string())


def download_file(url, local_filepath, max_retries=1, retry_timeout=60):
    # Removing illegal characters
    # local_filepath = local_filepath.replace('?', '')
    # local_filepath = local_filepath.replace('\"', '')
    #
    # basename = os.path.basename(local_filepath)
    # basename = basename.replace(':', '')
    # local_filepath = os.path.join(os.path.dirname(local_filepath), basename)

    chunk_size = 1024  # [bytes]
    wrote = 0  # [bytes]

    response = requests.get(url, stream=True, headers=HEADERS)

    if response.status_code != 200:
        response.raise_for_status()

    file_size = int(response.headers.get("content-length"))  # [bytes]
    tqdm_total = math.ceil(file_size // chunk_size)

    if os.path.isfile(local_filepath):
        if os.path.getsize(local_filepath) == file_size:
            logger.info("{:s} ({:,d} bytes) already downloaded. Skipping.".format(local_filepath, file_size))
            return

    while True:
        try:
            with open(local_filepath, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size=chunk_size),
                                  desc=local_filepath, leave=True, total=tqdm_total,
                                  unit='KiB', unit_divisor=1024, unit_scale=True):
                    wrote = wrote + len(chunk)
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            break
        except Exception as ex:
            logger.error(ex)
            logger.info("[{:}] Sleeping for {:s} seconds before retry...\n".format(str(datetime.now()), retry_timeout))
            time.sleep(retry_timeout)

    if file_size != 0 and wrote != file_size:
        logger.error("Total file size does not match bytes written!")

    return
