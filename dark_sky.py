from datetime import datetime
import requests
import json

import matplotlib.pyplot as plt

# City data
lat, lon = 42.362389, -71.091083

# Dark Sky API
secret_key = "81c07948c439765d630c4c60fc56634e"
ds_forecast_url = "https://api.darksky.net/forecast/" + secret_key + "/" + str(lat) + "," + str(lon)

ds_response = requests.get(ds_forecast_url)
ds_forecast = json.loads(ds_response.content)

city_lat = ds_forecast['latitude']
city_lon = ds_forecast['longitude']
city_tz = ds_forecast['timezone']

ds_currently = ds_forecast['currently']
current_time = ds_currently['time']
summary = ds_currently['summary']
nearest_storm_distance = ds_currently['nearestStormDistance']
precip_intensity = ds_currently['precipIntensity']
precip_prob = ds_currently['precipProbability']
T = ds_currently['temperature']
T_apparent = ds_currently['apparentTemperature']
dew_point = ds_currently['dewPoint']
humidity = ds_currently['humidity']
pressure = ds_currently['pressure']
wind_speed = ds_currently['windSpeed']
wind_gust = ds_currently['windGust']
wind_bearing = ds_currently['windBearing']
cloud_cover = ds_currently['cloudCover']
uv_index = ds_currently['uvIndex']
visibility = ds_currently['visibility']

ts = []
Ts = []

ds_hourly_forecast = ds_forecast['hourly']['data']
for i, forecast in enumerate(ds_hourly_forecast):
    time = datetime.utcfromtimestamp(forecast['time']).strftime('%Y-%m-%d %H:%M:%S')
    summary = forecast['summary']
    precip_intensity = forecast['precipIntensity']
    precip_prob = forecast['precipProbability']
    T = forecast['temperature']
    T_apparent = forecast['apparentTemperature']
    dew_point = forecast['dewPoint']
    humidity = forecast['humidity']
    pressure = forecast['pressure']
    wind_speed = forecast['windSpeed']
    wind_gust = forecast['windGust']
    wind_bearing = forecast['windBearing']
    cloud_cover = forecast['cloudCover']
    uv_index = forecast['uvIndex']
    visibility = forecast['visibility']
    print("{:s} T={:.1f}°F".format(time, T))

    ts.append(time)
    Ts.append(T)

plt.plot(ts, Ts)
plt.show()
