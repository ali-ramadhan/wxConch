import logging.config
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from hrrr import hrrr_forecast_time_series
from gfs import gfs_forecast_time_series
from nam import nam_forecast_time_series
from ecmwf import ecmwf_forecast_time_series
from metar import metar_timeseries
from utils import compute_6Z_times

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def plot_temperature_verification(timeseries, verification_date, station, filepath):
    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    ax.plot(timeseries["metar"]["temperature"], label="METAR")
    ax.plot(timeseries["hrrr"]["temperature"], label="HRRR")
    ax.plot(timeseries["nam"]["temperature"], label="NAM 5km")
    ax.plot(timeseries["gfs"]["temperature"], label="GFS")
    ax.plot(timeseries["ecmwf"]["temperature"], label="ECMWF")

    # Focus on the 6Z-6Z range.
    first_6Z, second_6Z = compute_6Z_times(verification_date - pd.Timedelta(days=1))
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.title(f'{station} temperature verification for {verification_date.strftime("%Y/%m/%d")}')

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.15), frameon=False)
    plt.xlabel("Time (UTC)")
    plt.ylabel("Temperature (°F)")

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def plot_wind_speed_verification(timeseries, verification_date, station, filepath):
    fig = plt.figure(figsize=(16, 9))
    ax = plt.subplot(111)

    ax.plot(timeseries["metar"]["wind_speed"], label="METAR")
    ax.plot(timeseries["hrrr"]["wind_speed"], label="HRRR")
    ax.plot(timeseries["nam"]["wind_speed"], label="NAM 5km")
    ax.plot(timeseries["gfs"]["wind_speed"], label="GFS")
    ax.plot(timeseries["ecmwf"]["wind_speed"], label="ECMWF")

    # Focus on the 6Z-6Z range.
    first_6Z, second_6Z = compute_6Z_times(verification_date - pd.Timedelta(days=1))
    plt.xlim([first_6Z - pd.Timedelta(hours=6), second_6Z + pd.Timedelta(hours=6)])

    ax.axvline(x=first_6Z, ymin=0, ymax=1, color="red", linestyle="--")
    ax.axvline(x=second_6Z, ymin=0, ymax=1, color="red", linestyle="--")

    # Nicer date formatting.
    formatter = DateFormatter('%m/%d %HZ')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=11)

    plt.title(f'{station} Wind speed verification for {verification_date.strftime("%Y/%m/%d")}')
    plt.xlabel("Time (UTC)")
    plt.ylabel("Wind speed (knots)")

    plt.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.15), frameon=False)

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def min_and_max_temperature(ts):
    t = ts.index
    T = ts.values

    i_min = np.argmin(T)
    i_max = np.argmax(T)
    t_min = t[i_min]
    t_max = t[i_max]
    T_min = T[i_min]
    T_max = T[i_max]

    return t_min, T_min, t_max, T_max

def max_wind_speed(ts):
    t = ts.index
    s = ts.values

    i_max = np.argmax(s)
    t_max = t[i_max]
    s_max = s[i_max]

    return t_max, s_max

def compute_biases(timeseries, verification_date):
    first_6Z, second_6Z = compute_6Z_times(verification_date - pd.Timedelta(days=1))
    logging.info(f"Computing biases for {first_6Z} to {second_6Z}...")

    T_metar_6Z = timeseries["metar"]["temperature"][first_6Z:second_6Z]
    s_metar_6Z = timeseries["metar"]["wind_speed"][first_6Z:second_6Z]

    t_min, T_min, t_max, T_max = min_and_max_temperature(T_metar_6Z)
    t_max_wind, wind_max = max_wind_speed(s_metar_6Z)

    logging.info(f"METAR: T_min = {T_min:.1f}°F @ {t_min}, T_max = {T_max:.1f}°F @ {t_max}, wind_max = {wind_max:.1f} knots @ {t_max_wind}")

    biases = {}

    for model in ("nam", "gfs", "ecmwf"):
        T_model_6Z = timeseries[model]["temperature"][first_6Z:second_6Z]
        s_model_6Z = timeseries[model]["wind_speed"][first_6Z:second_6Z]

        t_min_model, T_min_model, t_max_model, T_max_model = min_and_max_temperature(T_model_6Z)
        t_max_wind_model, wind_max_model = max_wind_speed(s_model_6Z)

        logging.info(f"{model}: T_min = {T_min_model:.1f}°F @ {t_min_model}, T_max = {T_max_model:.1f}°F @ {t_max_model}, wind_max = {wind_max_model:.1f} knots @ {t_max_wind_model}")
        logging.info(f"{model} bias: T_min = {T_min_model - T_min:.1f}°F, T_max = {T_max_model - T_max:.1f}°F, wind: {wind_max_model - wind_max:.1f} knots")

        biases[model] = {
            "T_min": T_min_model - T_min,
            "T_max": T_max_model - T_max,
            "wind_speed": wind_max_model - wind_max
        }

    return biases

def biases_dataframe(biases):
    dates = list(biases.keys())

    models = ("nam", "gfs", "ecmwf")
    vars = ("T_min", "T_max", "wind_speed")
    biases_df = pd.DataFrame({
        f"{model}_{var}": [biases[t][model][var] for t in dates] for model in models for var in vars
    }, index=dates)

    return biases_df

def plot_biases(df, station, filepath):
    fig = plt.figure(figsize=(16, 9))

    ax1 = plt.subplot(311)
    ax2 = plt.subplot(312, sharex=ax1)
    ax3 = plt.subplot(313, sharex=ax1)

    models = ("nam", "gfs", "ecmwf")
    vars = ("T_min", "T_max", "wind_speed")
    colors = ("green", "red", "blue")
    markers = ("v", "^", "s")

    for ax in (ax1, ax2, ax3):
        ax.axhline(y=0, color="black", linestyle="--")

    for m, model in enumerate(models):
            ax1.plot(df[f"{model}_T_min"], color=colors[m], marker="v", label=model)
            ax2.plot(df[f"{model}_T_max"], color=colors[m], marker="^", label=model)
            ax3.plot(df[f"{model}_wind_speed"], color=colors[m], marker="s", label=model)

    ax1.set_ylabel("T_min bias (°F)")
    ax2.set_ylabel("T_max bias (°F)")
    ax3.set_ylabel("wind speed bias (knots)")
    ax3.set_xlabel("Time (UTC)")

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)

    ax1.set_title(f"Bias verification for {station}")
    ax1.legend(loc="upper left", ncol=3, bbox_to_anchor=(0, 1.2), frameon=False)

    logging.info(f"Saving {filepath}...")
    plt.savefig(filepath)

def compute_model_biases(lat, lon, station, metar_filepath, verification_dates):
    storage = {}
    biases = {}

    for verification_date in verification_dates:
        # 23Z run might not be available right at 23Z when we run WxConch so let's use 22Z model run for HRRR.
        hrrr_model_time = (verification_date - pd.Timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        nam_model_time = (verification_date - pd.Timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        gfs_model_time = (verification_date - pd.Timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        ecmwf_model_time = (verification_date - pd.Timedelta(hours=12)).strftime("%Y-%m-%d %H:%M")

        timeseries = {
            "metar": metar_timeseries(metar_filepath),
            "hrrr": hrrr_forecast_time_series(hrrr_model_time, lat, lon),
            "nam": nam_forecast_time_series(nam_model_time, lat, lon),
            "gfs": gfs_forecast_time_series(gfs_model_time, lat, lon),
            "ecmwf": ecmwf_forecast_time_series(ecmwf_model_time, lat, lon)
        }

        storage[verification_date] = timeseries

        logging.info(f"Computing biases for {verification_date}...")
        biases[verification_date] = compute_biases(timeseries, verification_date)

        temperature_filepath = f'temperature_verification_{station}_{verification_date.strftime("%Y-%m-%d")}.png'
        wind_speed_filepath = f'wind_speed_verification_{station}_{verification_date.strftime("%Y-%m-%d")}.png'

        plot_temperature_verification(timeseries, verification_date, station, temperature_filepath)
        plot_wind_speed_verification(timeseries, verification_date, station, wind_speed_filepath)


    with open(f"storage_{station}.pickle", "wb") as handle:
        pickle.dump(storage, handle)

    biases_df = biases_dataframe(biases)
    start_date = verification_dates[0].strftime("%Y-%m-%d")
    end_date = verification_dates[-1].strftime("%Y-%m-%d")
    biases_filepath = f"bias_verification_{station}_{start_date}_{end_date}.png"
    plot_biases(biases_df, station, biases_filepath)

    with open(f"biases_{station}.pickle", "wb") as handle:
        pickle.dump(biases_df, handle)

if __name__ == "__main__":
    # Testing @ Boston
    # lat, lon = 42.362389, 288.908917
    # station = "KBOS"
    # verification_dates = pd.date_range(pd.Timestamp("2022-08-15"), pd.Timestamp("2022-08-22"))
    # metar_filepath = "KBOS_August_2022.csv"
    # compute_model_biases(lat, lon, station, metar_filepath, verification_dates)

    # Fort Myers
    station = "KFMY"
    lat, lon = 26.5866150, 278.1367531
    verification_dates = pd.date_range(pd.Timestamp("2022-09-10"), pd.Timestamp("2022-09-24"))
    metar_filepath = "KFMY_2022_09.csv"
    compute_model_biases(lat, lon, station, metar_filepath, verification_dates)
