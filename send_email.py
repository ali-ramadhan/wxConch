import logging.config
import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "wxConch (Python3) https://github.com/ali-ramadhan/wxConch",
    "From": "alir@mit.edu"
}

def send_email(send_from, send_to, subject, text, files=None, server_address="smtp.gmail.com", port=465, login="wxconch.forecast@gmail.com"):
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

        part["Content-Disposition"] = f'attachment; filename="{basename(f)}"'
        msg.attach(part)

    password = input(f"Password for {login}: ")

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(server_address, port, context=context) as server:
        server.login(login, password)
        server.sendmail(send_from, send_to, msg.as_string())
