from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter

from dark_sky import dark_sky_temp_time_series
from open_weather_map import open_weather_map_temp_time_series
from national_weather_service import nws_temp_time_series
from hrrr import hrrr_temp_time_series
from soundings import animate_hrrr_soundings, animate_nam3km_soundings

from utils import send_email

plt.rcParams.update({'font.size': 14})

# Boston data
lat, lon = 42.362389, -71.091083
OWM_CITY_ID = 4930956  # OpenWeatherMap city ID

t_owm, T_owm = open_weather_map_temp_time_series(OWM_CITY_ID)
t_ds, T_ds = dark_sky_temp_time_series(lat, lon)
t_nws, T_nws = nws_temp_time_series(lat, lon)
t_hrrr, T_hrrr = hrrr_temp_time_series(lat, lon)

t_offset = timedelta(hours=4)

fig = plt.figure(figsize=(16, 9))
ax = plt.subplot(111)

ax.plot([t + t_offset for t in t_owm], T_owm, marker='o', label="OpenWeatherMap")
ax.plot([t + t_offset for t in t_ds], T_ds, marker='o', label="Dark Sky")
ax.plot([t + t_offset for t in t_nws], T_nws, marker='o', label="National Weather Service")
ax.plot(t_hrrr, T_hrrr, marker='o', label="HRRR")

# Calculate position of and plot lines for tomorrow's 6Z and after tomorrow's 6Z.
utcnow = datetime.utcnow()
utc_today = datetime(utcnow.year, utcnow.month, utcnow.day)
first_6Z = utc_today + timedelta(days=1, hours=6)
second_6Z = utc_today + timedelta(days=2, hours=6)
ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

# Squeeze plot a little so we can fit the legend on the right.
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Focus on the 6Z-6Z range.
plt.xlim([t_owm[0], second_6Z + timedelta(hours=6)])

# Nicer date formatting.
formatter = DateFormatter('%m/%d %HZ')
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=11)

plt.xlabel("Time (UTC)")
plt.ylabel("Temperature (°F)")

plt.legend(loc="upper left", bbox_to_anchor=(1, 1), frameon=False)
plt.grid()

plt.show()

temp_time_series_filepath = "KBOS06112019.png"
plt.savefig(temp_time_series_filepath, dpi=150, format='png', transparent=False)

hrrr_gif_filepath = animate_hrrr_soundings(datetime(2019, 6, 12, 12), lat, lon)
nam3km_gif_filepath = animate_nam3km_soundings(datetime(2019, 6, 12, 12), lat, lon)

sender_email = "WxConch <wxconch.forecast@gmail.com>"
receiver_email = ["a3ramadhan@gmail.com"]
subject = "WxConch forecast for Boston (06/11/2019)"
text = "Some weather statistics..."
files = [temp_time_series_filepath, hrrr_gif_filepath, nam3km_gif_filepath]

send_email(sender_email, receiver_email, subject, text, files)
