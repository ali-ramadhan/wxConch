from datetime import datetime
import requests
import json

import matplotlib.pyplot as plt

# Request headers
headers = {
    'User-Agent': 'wxConch (Python3.7)',
    'From': 'alir@mit.edu'
}

# OpenWeatherMap API
owm_forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
owm_params = {
    'APPID': "c7f3d1b2657114c4c2ba33b64b8fa3a7",
    'id': 4930956,  # City ID for Boston
    'units': "imperial"
}

owm_response = requests.get(owm_forecast_url, params=owm_params)
print(owm_response)

owm_forecast = json.loads(owm_response.content)

city_id = owm_forecast['city']['id']
city_name = owm_forecast['city']['name']
city_lat = owm_forecast['city']['coord']['lat']
city_lon = owm_forecast['city']['coord']['lon']
city_country = owm_forecast['city']['country']

print("{:s}, {:s} ({:.4f}°N, {:.4f}°E) [ID: {:d}] ".format(city_name, city_country, city_lat, city_lon, city_id))

ts = []
Ts = []
Ts_min = []
Ts_max = []

for i, forecast_entry in enumerate(owm_forecast['list']):
    t_txt = forecast_entry['dt_txt']
    T = forecast_entry['main']['temp']
    T_min = forecast_entry['main']['temp_min']
    T_max = forecast_entry['main']['temp_max']

    ts.append(datetime.strptime(t_txt, "%Y-%m-%d %H:%M:%S"))
    Ts.append(T)
    Ts_min.append(T_min)
    Ts_max.append(T_max)

    print("{:s} T={:.1f}°F, T_min={:.1f}°F, T_max={:.1f}°F".format(t_txt, T, T_min, T_max))

plt.plot(ts, Ts)
plt.show()
