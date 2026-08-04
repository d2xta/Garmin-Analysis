import pandas as pd

from src.utils.fit_loaders import fit_to_df_record


def calculate_heart_metrics(df, summary):

    start_time = summary["activityStartTimestampGMT"]
    length_of_activity = summary['durationSeconds']
    avg_hr = summary['avgHr']
    max_hr = summary["maxHr"]


    # Time to max HR 
    max_idx = df["heart_rate"].idxmax()
    max_hr_time = df.loc[max_idx, "timestamp"]

    ratio_time_max_hr = (max_hr_time - start_time).total_seconds() / length_of_activity

    # Time to avg HR 
    try:
        first_cross = df.loc[df["heart_rate"] >= avg_hr, "timestamp"].iloc[0]
        ratio_time_avg_hr = (first_cross - start_time).total_seconds() / length_of_activity
    except Exception:
        ratio_time_avg_hr = None

    # HR volatility 
    hr_volatility = df["heart_rate"].std()

    # HR derivative 
    df["hr_derivative"] = df["heart_rate"].diff() / df["dt"].replace(0, float("nan"))
    hr_derivative = df["hr_derivative"].abs().mean()

    # HR drift 
    df["cum_time"] = df["dt"].cumsum()
    half_time = df["cum_time"].iloc[-1] / 2

    first_half = df[df["cum_time"] <= half_time]
    second_half = df[df["cum_time"] > half_time]

    if len(first_half) > 0 and len(second_half) > 0:
        hr_drift = (second_half["heart_rate"].mean() - first_half["heart_rate"].mean()) / first_half["heart_rate"].mean()
    else:
        hr_drift = None

    # Total beats (integrated over time) 
    df["beats"] = df["heart_rate"] * df["dt"] / 60
    total_beats = df["beats"].sum()

    mpb = summary['distanceMeters'] / total_beats if total_beats > 0 else None

    # (actual seconds at max HR) 
    plateau_seconds = df.loc[df["heart_rate"] == max_hr, "dt"].sum()

    # HR vs pace coupling
    try:
        hr_pace_coupling = df["heart_rate"].corr(df["enhanced_speed"])
    except Exception:
        hr_pace_coupling = None

    # HR smoothness 
    hr_smoothness = 1 / hr_derivative if hr_derivative and hr_derivative != 0 else None

    # HR oscillation (10-sample rolling) 
    hr_oscillation = df["heart_rate"].diff().abs().rolling(10).mean().mean()

    # Start HR offset 
    start_hr_offset = df["heart_rate"].iloc[0] - avg_hr

    return {
        "start_time": start_time,

        "ratio_time_max_hr": ratio_time_max_hr,
        "ratio_time_avg_hr": ratio_time_avg_hr,

        "hr_volatility": hr_volatility,
        "hr_derivative": hr_derivative,
        "hr_smoothness": hr_smoothness,
        "hr_oscillation": hr_oscillation,

        "hr_drift": hr_drift,

        "meters_per_beat": mpb,

        "plateau_seconds": plateau_seconds,

        "hr_pace_coupling": hr_pace_coupling,

        "start_hr_offset": start_hr_offset,
    }


def calculate_cadence_metrics(df, summary):

    # Basic values
    total_distance = summary['distanceMeters']
    total_strides = summary["steps"]

    # Cadence stability 
    cadence_std = df["cadence_spm"].std()
    cadence_cv = cadence_std / df["cadence_spm"].mean() if df["cadence_spm"].mean() else None

    # Cadence drift (time-aware)
    df["cum_time"] = df["dt"].cumsum()
    half_time = df["cum_time"].iloc[-1] / 2
    first_half = df[df["cum_time"] <= half_time]
    second_half = df[df["cum_time"] > half_time]

    if len(first_half) > 0 and len(second_half) > 0:
        cadence_drift = (second_half["cadence_spm"].mean() - first_half["cadence_spm"].mean()) / first_half["cadence_spm"].mean()
    else:
        cadence_drift = None

    # Cadence derivative (harshness)
    df["cadence_derivative"] = df["cadence_spm"].diff() / df["dt"].replace(0, float("nan"))
    cadence_derivative = df["cadence_derivative"].abs().mean()
    cadence_smoothness = 1 / cadence_derivative if cadence_derivative else None

    # Cadence–speed coupling
    try:
        cadence_speed_coupling = df["cadence_spm"].corr(df["enhanced_speed"])
    except Exception:
        cadence_speed_coupling = None

    # Cadence–HR coupling 
    try:
        cadence_hr_coupling = df["cadence_spm"].corr(df["heart_rate"])
    except Exception:
        cadence_hr_coupling = None

    # Steps per meter (efficiency) 
    if total_distance and total_distance > 0:
        steps_per_meter = (total_strides * 2) / total_distance
    else:
        steps_per_meter = None

    # 1. True running cadence (≥ 140 spm)
    running_mask = df["cadence_spm"] >= 140
    if running_mask.any():
        running_start_idx = running_mask.idxmax()
        running_start_cadence = df["cadence_spm"].loc[running_start_idx]

    # 2. If no running cadence, use first non-zero cadence
    elif (df["cadence_spm"] > 0).any():
        running_start_idx = (df["cadence_spm"] > 0).idxmax()
        running_start_cadence = df["cadence_spm"].loc[running_start_idx]

    # 3. If cadence is always zero → no readiness metric
    else:
        running_start_cadence = None

    return {
        "cadence_std": cadence_std,
        "cadence_cv": cadence_cv,

        "cadence_drift": cadence_drift,

        "cadence_derivative": cadence_derivative,
        "cadence_smoothness": cadence_smoothness,

        "cadence_speed_coupling": cadence_speed_coupling,
        "cadence_hr_coupling": cadence_hr_coupling,

        "steps_per_meter": steps_per_meter,

        "running_start_cadence": running_start_cadence,
    }


def calculate_speed_metrics(df, summary):

    # Basic values
    avg_speed = summary['distanceMeters'] / summary['durationSeconds']
    max_speed = df["enhanced_speed"].max()

    # Speed stability 
    speed_std = df["enhanced_speed"].std()
    speed_cv = speed_std / df["enhanced_speed"].mean() if df["enhanced_speed"].mean() else None

    # Speed drift (time-aware)
    df["cum_time"] = df["dt"].cumsum()
    half_time = df["cum_time"].iloc[-1] / 2
    first_half = df[df["cum_time"] <= half_time]
    second_half = df[df["cum_time"] > half_time]

    if len(first_half) > 0 and len(second_half) > 0:
        speed_drift = (second_half["enhanced_speed"].mean() - first_half["enhanced_speed"].mean()) / first_half["enhanced_speed"].mean()
    else:
        speed_drift = None

    # Speed derivative (harshness)
    df["speed_derivative"] = df["enhanced_speed"].diff() / df["dt"].replace(0, float("nan"))
    speed_derivative = df["speed_derivative"].abs().mean()
    speed_smoothness = 1 / speed_derivative if speed_derivative else None

    # Speed oscillation index 
    speed_oscillation = df["enhanced_speed"].diff().abs().rolling(10).mean().mean()

    # Speed–HR coupling 
    try:
        speed_hr_coupling = df["enhanced_speed"].corr(df["heart_rate"])
    except Exception:
        speed_hr_coupling = None

    # Speed–cadence coupling 
    try:
        speed_cadence_coupling = df["enhanced_speed"].corr(df["cadence_spm"])
    except Exception:
        speed_cadence_coupling = None

    # Running start speed 
    try:
        running_start_idx = df.index[df["enhanced_speed"] >= 1.5][0]
        running_start_speed = df.loc[running_start_idx, "enhanced_speed"]
    except Exception:
        running_start_speed = None

    return {
        "avg_speed": avg_speed,
        "max_speed": max_speed,

        "speed_std": speed_std,
        "speed_cv": speed_cv,

        "speed_drift": speed_drift,

        "speed_derivative": speed_derivative,
        "speed_smoothness": speed_smoothness,

        "speed_oscillation": speed_oscillation,

        "speed_hr_coupling": speed_hr_coupling,
        "speed_cadence_coupling": speed_cadence_coupling,

        "running_start_speed": running_start_speed,
    }


def calculate_stride_metrics(df):

    # Stride length per second (derived) 
    df["distance_diff"] = df["distance"].diff().fillna(0)
    df["stride_length"] = df["distance_diff"] / (df["cadence_spm"] / 60).replace(0, pd.NA)

    stride_series = df["stride_length"].dropna()

    if len(stride_series) == 0:
        return {
            "stride_std": None,
            "stride_cv": None,
            "stride_drift": None,
            "stride_derivative": None,
            "stride_smoothness": None,
            "stride_oscillation": None,
            "stride_speed_coupling": None,
            "stride_hr_coupling": None,
            "running_start_stride": None,
        }

    # Stride stability
    stride_std = stride_series.std()
    stride_cv = stride_std / stride_series.mean() if stride_series.mean() else None

    # Stride drift (time-aware)
    df["cum_time"] = df["dt"].cumsum()
    half_time = df["cum_time"].iloc[-1] / 2
    valid_idx = stride_series.index

    first_half = stride_series[df.loc[valid_idx, "cum_time"] <= half_time]
    second_half = stride_series[df.loc[valid_idx, "cum_time"] > half_time]

    if len(first_half) > 0 and len(second_half) > 0:
        stride_drift = (second_half.mean() - first_half.mean()) / first_half.mean()
    else:
        stride_drift = None

    # Stride derivative (harshness)
    stride_derivative = stride_series.diff().abs().mean()
    stride_smoothness = 1 / stride_derivative if stride_derivative else None

    # Stride oscillation 
    stride_oscillation = stride_series.diff().abs().rolling(10).mean().mean()

    # Stride–speed coupling 
    try:
        stride_speed_coupling = stride_series.corr(df.loc[stride_series.index, "enhanced_speed"])
    except Exception:
        stride_speed_coupling = None

    # Stride–HR coupling
    try:
        stride_hr_coupling = stride_series.corr(df.loc[stride_series.index, "heart_rate"])
    except Exception:
        stride_hr_coupling = None

    # Start stride offset (readiness) 
    try:
        running_start_idx = df.index[df["cadence_spm"] >= 140][0]
        running_start_stride = df.loc[running_start_idx, "stride_length"]
    except Exception:
        running_start_stride = None

    return {
        "stride_std": stride_std,
        "stride_cv": stride_cv,

        "stride_drift": stride_drift,

        "stride_derivative": stride_derivative,
        "stride_smoothness": stride_smoothness,

        "stride_oscillation": stride_oscillation,

        "stride_speed_coupling": stride_speed_coupling,
        "stride_hr_coupling": stride_hr_coupling,

        "running_start_stride": running_start_stride,
    }



def get_metrics(file_name, summary_record):
    # Load data
    df = fit_to_df_record(file_name)

    hr_met = calculate_heart_metrics(df,summary_record)
    cad_met = calculate_cadence_metrics(df,summary_record)
    speed_met = calculate_speed_metrics(df,summary_record)
    stride_met = calculate_stride_metrics(df)

    metric = {**hr_met,**cad_met,**speed_met,**stride_met}

    return metric

