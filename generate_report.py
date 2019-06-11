import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import matplotlib.pyplot as plt

from dark_sky import dark_sky_temp_time_series
from open_weather_map import open_weather_map_temp_time_series
from national_weather_service import nws_temp_time_series


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
    password = input("Gmail password: ")

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("wxconch.forecast@gmail.com", password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


# Boston data
lat, lon = 42.362389, -71.091083
OWM_CITY_ID = 4930956  # OpenWeatherMap city ID

t_owm, T_owm = open_weather_map_temp_time_series(OWM_CITY_ID)
t_ds, T_ds = dark_sky_temp_time_series(lat, lon)
t_nws, T_nws = nws_temp_time_series(lat, lon)

plt.plot(t_owm, T_owm, label="OpenWeatherMap")
plt.plot(t_ds, T_ds, label="Dark Sky")
plt.plot(t_nws, T_nws, label="National Weather Service")

plt.xlabel("Time")
plt.ylabel("Temperature (°F)")
plt.legend()

png_filepath = "KBOS06112019.png"
plt.savefig(png_filepath, dpi=150, format='png', transparent=False)

sender_email = "WxConch <wxconch.forecast@gmail.com>"
receiver_email = ["a3ramadhan@gmail.com"]
subject = "WxConch forecast for Boston (06/11/2019)"
text = "Some weather statistics..."
files = [png_filepath]

send_email(sender_email, receiver_email, subject, text, files)

