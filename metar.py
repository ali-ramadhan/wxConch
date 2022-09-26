import pandas as pd

def metar_timeseries(filepath):
    df = pd.read_csv(filepath)

    inds_T = df["tmpf"] != "M"  # Exclude missing temperatures
    time_T = [pd.Timestamp(t) for t in df["valid"][inds_T]]
    temperature = df["tmpf"][inds_T].astype("float")

    inds_ws = df["sknt"] != "M"  # Exclude missing wind speeds
    time_ws = [pd.Timestamp(t) for t in df["valid"][inds_ws]]
    wind_speed = df["sknt"][inds_ws].astype("float")

    inds_P = (df["p01i"] != "M") & (df["p01i"] != "T")  # Exclude missing ("M") and trace ("T") observations
    time_P = [pd.Timestamp(t) for t in df["valid"][inds_P]]
    precipitation = df["p01i"][inds_P].astype("float")

    timeseries = pd.DataFrame({
        "temperature": pd.Series(temperature.values, index=time_T),
        "wind_speed": pd.Series(wind_speed.values, index=time_ws),
        "precipitation": pd.Series(precipitation.values, index=time_P)
    })

    return timeseries

if __name__ == "__main__":
    # Testing @ Boston
    timeseries = metar_timeseries("KBOS_August_2022.csv")
    print(timeseries)
    print(timeseries["wind_speed"])

    timeseries = metar_timeseries("KFMY_2022_09.csv")
    print(timeseries)
    print(timeseries["wind_speed"])
