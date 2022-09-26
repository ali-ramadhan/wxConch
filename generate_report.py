import logging.config

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from hrrr import latest_hrrr_forecast_time_series
from gfs import latest_gfs_forecast_time_series
from nam import latest_nam_forecast_time_series
from ecmwf import latest_ecmwf_forecast_time_series
from nws import nws_forecast_time_series

from utils import compute_6Z_times, timeseries_max, timeseries_min_and_max

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def temperature_label(model, temperature, t1, t2):
    ts = temperature[t1:t2]

    if ts.size == 0:
        return f"{model}"
    else:
        t_min, T_min, t_max, T_max = timeseries_min_and_max(ts)
        t_min_txt = t_min.strftime("%m/%d %H:%M")
        t_max_txt = t_max.strftime("%m/%d %H:%M")
        return f"{model} (min: {T_min:.1f}°F @ {t_min_txt}Z, max: {T_max:.1f}°F @ {t_max_txt}Z)"

def wind_speed_label(model, wind_speed, t1, t2):
    ts = wind_speed[t1:t2]

    if ts.size == 0:
        return f"{model}"
    else:
        t_max, s_max = timeseries_max(ts)
        t_max_txt = t_max.strftime("%m/%d %H:%M")
        return f"{model} (max: {s_max:.1f} mph @ {t_max_txt}Z)"

def plot_temperature_forecast(timeseries, station, filepath):
    first_6Z, second_6Z = compute_6Z_times()

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    label_hrrr = temperature_label("HRRR", timeseries["hrrr"]["temperature"], first_6Z, second_6Z)
    label_nam = temperature_label("NAM 5km", timeseries["nam"]["temperature"], first_6Z, second_6Z)
    label_gfs = temperature_label("GFS 0.25°", timeseries["gfs"]["temperature"], first_6Z, second_6Z)
    label_ecmwf = temperature_label("ECMWF 0.4°", timeseries["ecmwf"]["temperature"], first_6Z, second_6Z)
    label_nws = temperature_label("NWS", timeseries["nws"]["temperature"], first_6Z, second_6Z)

    ax.plot(timeseries["hrrr"]["temperature"], marker="o", label=label_hrrr)
    ax.plot(timeseries["nam"]["temperature"], marker="o", label=label_nam)
    ax.plot(timeseries["gfs"]["temperature"], marker="o", label=label_gfs)
    ax.plot(timeseries["ecmwf"]["temperature"], marker="o", label=label_ecmwf)
    ax.plot(timeseries["nws"]["temperature"], marker="o", label=label_nws)

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.title(f"Temperature forecast for {station}")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Temperature (°F)")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.15), frameon=False)
    plt.grid(which="both")

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def plot_wind_speed_forecast(timeseries, station, filepath):
    first_6Z, second_6Z = compute_6Z_times()

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    label_hrrr = wind_speed_label("HRRR", timeseries["hrrr"]["wind_speed"], first_6Z, second_6Z)
    label_nam = wind_speed_label("NAM 5km", timeseries["nam"]["wind_speed"], first_6Z, second_6Z)
    label_gfs = wind_speed_label("GFS 0.25°", timeseries["gfs"]["wind_speed"], first_6Z, second_6Z)
    label_ecmwf = wind_speed_label("ECMWF 0.4°", timeseries["ecmwf"]["wind_speed"], first_6Z, second_6Z)
    label_nws = wind_speed_label("NWS", timeseries["nws"]["wind_speed"], first_6Z, second_6Z)

    ax.plot(timeseries["hrrr"]["wind_speed"], marker="o", label=label_hrrr)
    ax.plot(timeseries["nam"]["wind_speed"], marker="o", label=label_nam)
    ax.plot(timeseries["gfs"]["wind_speed"], marker="o", label=label_gfs)
    ax.plot(timeseries["ecmwf"]["wind_speed"], marker="o", label=label_ecmwf)
    ax.plot(timeseries["nws"]["wind_speed"], marker="o", label=label_nws)

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.title(f"Wind speed forecast for {station}")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Wind speed (mph)")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.1), frameon=False)
    plt.grid(which="both")

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def plot_precipitation_forecast(timeseries, station, filepath):
    first_6Z, second_6Z = compute_6Z_times()

    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    # label_hrrr = wind_speed_label("HRRR", ts_hrrr["time"], ts_hrrr["wind_speed"], first_6Z, second_6Z)
    # label_nam = wind_speed_label("NAM 5km", ts_nam["time"], ts_nam["wind_speed"], first_6Z, second_6Z)

    ax.plot(timeseries["hrrr"]["precipitation"], marker="o", label="HRRR")
    ax.plot(timeseries["nam"]["precipitation"], marker="o", label="NAM 5km")
    ax.plot(timeseries["ecmwf"]["precipitation"], marker="o", label="ECMWF 0.4°")

    # plot cumsum of precip.

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Focus on the 6Z-6Z range.
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.title(f"Precipitation forecast for {station}")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Precipitation")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.1), frameon=False)
    plt.grid(which="both")

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def generate_forecast(station, lat, lon):
    now = pd.Timestamp.now()

    timeseries = {
        "hrrr": latest_hrrr_forecast_time_series(lat, lon),
        "nam": latest_nam_forecast_time_series(lat, lon),
        "gfs": latest_gfs_forecast_time_series(lat, lon),
        "ecmwf": latest_ecmwf_forecast_time_series(lat, lon),
        "nws": nws_forecast_time_series(lat, lon)
    }

    nowstr = now.strftime("%Y-%m-%d_%H%M%S")
    plot_temperature_forecast(timeseries, station, f"temperature_forecast_{station}_{nowstr}.png")
    plot_wind_speed_forecast(timeseries, station, f"wind_speed_forecast_{station}_{nowstr}.png")
    plot_precipitation_forecast(timeseries, station, f"precipitation_forecast_{station}_{nowstr}.png")


if __name__ == "__main__":
    # Testing @ Boston
    # lat, lon = 42.362389, 288.908917
    # station = "KBOS"

    # Fort Myers
    station = "KFMY"
    lat, lon = 26.5866150, 278.1367531
    generate_forecast(station, lat, lon)
