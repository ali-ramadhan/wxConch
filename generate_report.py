import matplotlib.pyplot as plt

from dark_sky import dark_sky_temp_time_series
from open_weather_map import open_weather_map_temp_time_series
from national_weather_service import nws_temp_time_series

from utils import send_email

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

