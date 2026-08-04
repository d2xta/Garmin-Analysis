from fitparse import FitFile
import pandas as pd


def fit_to_df_record(file_name):
    fit = FitFile(str(file_name), check_crc=False)

    # Extract ONLY the 5 target fields directly per record
    records = []
    for record in fit.get_messages("record"):
        records.append({
            "timestamp": record.get_value("timestamp"),
            "heart_rate": record.get_value("heart_rate"),
            "cadence": record.get_value("cadence"),
            "enhanced_speed": record.get_value("enhanced_speed"),
            "distance": record.get_value("distance"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "heart_rate", "cadence_spm", "enhanced_speed", "distance", "dt"])

    df["dt"] = df["timestamp"].diff().dt.total_seconds().fillna(0)
    df["cadence_spm"] = df["cadence"] * 2

    return df[["timestamp", "heart_rate", "cadence_spm", "enhanced_speed", "distance", "dt"]]


def get_start_time(file_name):
    fit = FitFile(str(file_name), check_crc=False)

    for msg in fit.get_messages("session"):
        start_time = msg.get_value("start_time")
        if start_time is not None:
            return pd.to_datetime(start_time)

    

