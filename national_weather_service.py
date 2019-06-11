import json
import requests

import matplotlib.pyplot as plt

stations = requests.get("https://api.weather.gov/stations")

tmp = json.loads(stations.content)
for s in tmp['features']:
    if s['properties']['stationIdentifier'] == "KBOS":
        print(s)

point = requests.get("https://api.weather.gov/points/42.362389,-71.091083")  # 42.362389, -71.091083
pointj = json.loads(point.content)

wfo = pointj['properties']['cwa']
X = pointj['properties']['gridX']
Y = pointj['properties']['gridY']
forecast_url = pointj['properties']['forecast']
hourly_forecast_url = pointj['properties']['forecastHourly']
print("WFO:{:s}, (X,Y)=({:d},{:d})".format(wfo, X, Y))
print("GET {:s}".format(hourly_forecast_url))

hourly = requests.get(hourly_forecast_url)
hourlyj = json.loads(hourly.content)

ts = []
Ts = []

for i, fe in enumerate(hourlyj['properties']['periods']):
    time = fe['startTime']
    T = fe['temperature']
    wind_speed = fe['windSpeed']
    wind_dir = fe['windDirection']
    description = fe['shortForecast']
    print("{:s} {:d}F {:s} {:s} ({:s})".format(time, T, wind_speed, wind_dir, description))

    ts.append(time)
    Ts.append(T)

plt.plot(ts, Ts)
plt.show()

