import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from nam import nam_forecast_time_series
from utils import compute_6Z_times

def metar_timeseries(filepath):
    df = pd.read_csv(filepath)

    inds_T = df["tmpf"] != "M"  # Exclude missing temperatures
    time_T = [pd.Timestamp(t) for t in df["valid"][inds_T]]
    temperature = df["tmpf"][inds_T].astype("float")

    time_ws = [pd.Timestamp(t) for t in df["valid"]]
    wind_speed = df["sknt"]

    inds_P = (df["p01i"] != "M") & (df["p01i"] != "T")  # Exclude missing ("M") and trace ("T") observations
    time_P = [pd.Timestamp(t) for t in df["valid"][inds_P]]
    precipitation = df["p01i"][inds_P].astype("float")

    timeseries = {
        "time_temperature": time_T,
        "temperature": temperature,
        "time_wind_speed": time_ws,
        "wind_speed": wind_speed,
        "time_precipitation": time_P,
        "precipitation": precipitation
    }

    return timeseries

ts_metar = metar_timeseries("KBOS_August_2022.csv")

# df = pd.read_csv("KBOS_August_2022.csv")

# inds = df["tmpf"] != "M"  # Exclude missing temperatures
# time_T = [pd.Timestamp(t) for t in df["valid"][inds]]
# temperature = df["tmpf"][inds].astype("float")

# plt.plot(time_T, temperature)
# plt.show()

# time_ws = [pd.Timestamp(t) for t in df["valid"]]
# wind_speed = df["sknt"]

# plt.plot(time_ws, wind_speed)
# plt.show()

# inds = (df["p01i"] != "M") & (df["p01i"] != "T")
# time_P = [pd.Timestamp(t) for t in df["valid"][inds]]
# precipitation = df["p01i"][inds].astype("float")

# plt.plot(time_P, precipitation)
# plt.show()

# Verifying for WxChallenge 2022/08/10 (forecast period 2022/08/10 6Z - 2022/08/11 6Z)
# Need to use model runs from before 2022/08/09 23Z or earlier.
# NAM: will need to use 2022/08/09 18Z.

# Testing @ Boston
lat, lon = 42.362389, 288.908917
station = "KBOS"

forecast_day = pd.Timestamp(year=2022, month=8, day=10)
nam_model_time = (forecast_day - pd.Timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
ts_nam = nam_forecast_time_series(nam_model_time, lat, lon)

# Verify temperature

fig = plt.figure(figsize=(16, 9))
ax = plt.subplot(111)

ax.plot(ts_metar["time_temperature"], ts_metar["temperature"], label="METAR")
ax.plot(ts_nam["time"], ts_nam["temperature_F"], label="NAM 5km")

# Focus on the 6Z-6Z range.
first_6Z, second_6Z = compute_6Z_times(forecast_day - pd.Timedelta(days=1))
plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

# Nicer date formatting.
formatter = DateFormatter('%m/%d %HZ')
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=11)

plt.title(f'{station} temperature verification for {forecast_day.strftime("%Y/%m/%d")}')

plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.15), frameon=False)

plt.show()

#===
import numpy as np

def time_indices(ts, t1, t2):
    times = pd.Series(ts)
    return np.where((t1 <= times) & (times <= t2))[0]

def min_and_max_temperature(time, temperature, t1, t2):
    time = np.array(time)
    temperature = np.array(temperature)

    inds = time_indices(time, t1, t2)
    t = time[inds]
    T = temperature[inds]

    i_min = np.argmin(T)
    i_max = np.argmax(T)
    t_min = t[i_min]
    t_max = t[i_max]
    T_min = T[i_min]
    T_max = T[i_max]

    return t_min, T_min, t_max, T_max
#===

inds_metar = time_indices(ts_metar["time_temperature"], first_6Z, second_6Z)
inds_nam = time_indices(ts_nam["time"], first_6Z, second_6Z)

t_metar_6Z = np.array(ts_metar["time_temperature"])[inds_metar]
T_metar_6Z = ts_metar["temperature"][inds_metar]

t_nam_6Z = np.array(ts_nam["time"])[inds_nam]
T_nam_6Z = ts_nam["temperature_F"][inds_nam]

_, T_min_metar, _, T_max_metar = min_and_max_temperature(t_metar_6Z, T_metar_6Z, first_6Z, second_6Z)
_, T_min_nam, _, T_max_nam = min_and_max_temperature(t_nam_6Z, T_nam_6Z, first_6Z, second_6Z)

print(f"METAR: T_min = {T_min_metar}, T_max = {T_max_metar}")
print(f"NAM: T_min = {T_min_nam}, T_max = {T_max_nam}")
print(f"Bias: dT_min = {T_min_metar - T_min_nam}, dT_max = {T_max_metar - T_max_nam}")

