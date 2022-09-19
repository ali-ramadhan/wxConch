from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter

from hrrr import latest_hrrr_forecast_time_series
from gfs import latest_gfs_forecast_time_series
from nam import latest_nam_forecast_time_series
from ecmwf import latest_ecmwf_forecast_time_series
from nws import nws_forecast_time_series

plt.rcParams.update({'font.size': 14})

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

def max_wind_speed(time, wind_speed, t1, t2):
    time = np.array(time)
    wind_speed = np.array(wind_speed)

    inds = time_indices(time, t1, t2)
    t = time[inds]
    s = wind_speed[inds]

    i_max = np.argmax(s)
    t_max = t[i_max]
    s_max = s[i_max]

    return t_max, s_max

def temperature_label(model, time, temperature, t1, t2):
    if time_indices(time, t1, t2).size == 0:
        return f"{model}"
    else:
        t_min, T_min, t_max, T_max = min_and_max_temperature(time, temperature, t1, t2)
        t_min_txt = t_min.strftime("%m/%d %H:%M")
        t_max_txt = t_max.strftime("%m/%d %H:%M")
        return f"{model} (min: {T_min:.1f}°F @ {t_min_txt}, max: {T_max:.1f}°F @ {t_max_txt})"

def wind_speed_label(model, time, wind_speed, t1, t2):
    if time_indices(time, t1, t2).size == 0:
        return f"{model}"
    else:
        t_max, s_max = max_wind_speed(time, wind_speed, t1, t2)
        t_max_txt = t_max.strftime("%m/%d %H:%M")
        return f"{model} (max: {s_max:.1f} mph @ {t_max_txt})"

if __name__ == "__main__":
    # Testing @ Boston
    lat, lon = 42.362389, 288.908917

    ts_hrrr = latest_hrrr_forecast_time_series(lat, lon)
    ts_nam = latest_nam_forecast_time_series(lat, lon)
    ts_gfs = latest_gfs_forecast_time_series(lat, lon)
    ts_ecmwf = latest_ecmwf_forecast_time_series(lat, lon)
    ts_nws = nws_forecast_time_series(lat, lon)

    # Calculate position of tomorrow's 6Z and after tomorrow's 6Z.
    utcnow = datetime.utcnow()
    utc_today = pd.Timestamp(datetime(utcnow.year, utcnow.month, utcnow.day))
    first_6Z = utc_today + pd.Timedelta(days=1, hours=6)
    second_6Z = utc_today + pd.Timedelta(days=2, hours=6)

    # Temperature

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    label_hrrr = temperature_label("HRRR", ts_hrrr["time"], ts_hrrr["temperature_F"], first_6Z, second_6Z)
    label_nam = temperature_label("NAM 5km", ts_nam["time"], ts_nam["temperature_F"], first_6Z, second_6Z)
    label_gfs = temperature_label("GFS 0.25°", ts_gfs["time"], ts_gfs["temperature_F"], first_6Z, second_6Z)
    label_ecmwf = temperature_label("ECMWF 0.4°", ts_ecmwf["time"], ts_ecmwf["temperature_F"], first_6Z, second_6Z)
    label_nws = temperature_label("NWS", ts_nws["time"], ts_nws["temperature_F"], first_6Z, second_6Z)

    ax.plot(ts_hrrr["time"], ts_hrrr["temperature_F"], marker="o", label=label_hrrr)
    ax.plot(ts_nam["time"], ts_nam["temperature_F"], marker="o", label=label_nam)
    ax.plot(ts_gfs["time"], ts_gfs["temperature_F"], marker="o", label=label_gfs)
    ax.plot(ts_ecmwf["time"], ts_ecmwf["temperature_F"], marker="o", label=label_ecmwf)
    ax.plot(ts_nws["time"], ts_nws["temperature_F"], marker="o", label=label_nws)

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.xlabel("Time (UTC)")
    plt.ylabel("Temperature (°F)")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.1), frameon=False)
    plt.grid(which="both")

    plt.show()

    # Wind speed

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    label_hrrr = wind_speed_label("HRRR", ts_hrrr["time"], ts_hrrr["wind_speed"], first_6Z, second_6Z)
    label_nam = wind_speed_label("NAM 5km", ts_nam["time"], ts_nam["wind_speed"], first_6Z, second_6Z)
    label_gfs = wind_speed_label("GFS 0.25°", ts_gfs["time"], ts_gfs["wind_speed"], first_6Z, second_6Z)
    label_ecmwf = wind_speed_label("ECMWF 0.4°", ts_ecmwf["time"], ts_ecmwf["wind_speed"], first_6Z, second_6Z)
    label_nws = wind_speed_label("NWS", ts_nws["time"], ts_nws["wind_speed"], first_6Z, second_6Z)

    ax.plot(ts_hrrr["time"], ts_hrrr["wind_speed"], marker="o", label=label_hrrr)
    ax.plot(ts_nam["time"], ts_nam["wind_speed"], marker="o", label=label_nam)
    ax.plot(ts_gfs["time"], ts_gfs["wind_speed"], marker="o", label=label_gfs)
    ax.plot(ts_ecmwf["time"], ts_ecmwf["wind_speed"], marker="o", label=label_ecmwf)
    ax.plot(ts_nws["time"], ts_nws["wind_speed"], marker="o", label=label_nws)

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.xlabel("Time (UTC)")
    plt.ylabel("Wind speed (mph)")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.1), frameon=False)
    plt.grid(which="both")

    plt.show()

    # Precip

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    # label_hrrr = wind_speed_label("HRRR", ts_hrrr["time"], ts_hrrr["wind_speed"], first_6Z, second_6Z)
    # label_nam = wind_speed_label("NAM 5km", ts_nam["time"], ts_nam["wind_speed"], first_6Z, second_6Z)

    ax.plot(ts_hrrr["time"], ts_hrrr["precipitation"], marker="o", label="HRRR")
    ax.plot(ts_nam["time"], ts_nam["precipitation"], marker="o", label="NAM 5km")
    ax.plot(ts_ecmwf["time"], ts_ecmwf["precipitation"], marker="o", label="ECMWF 0.4°")

    # plot cumsum of precip.

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.xlabel("Time (UTC)")
    plt.ylabel("Precipitation")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.1), frameon=False)
    plt.grid(which="both")

    plt.show()
