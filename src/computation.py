import pandas as pd

from src.fit_processing import fit_to_df_record, extract_session_summary


def calculate_heart_metrics(df,summary):

    # Convert timestamps
    start_time = pd.to_datetime(summary["start_time"])

    # Basic values
    length_of_activity = summary["total_timer_time"]
    avg_hr = summary["avg_heart_rate"]
    max_hr = summary["max_heart_rate"]

    # Time to max HR 
    max_hr_idx = df["heart_rate"].idxmax()
    max_hr_time = df.loc[max_hr_idx, "timestamp"]
    time_to_max_hr = (max_hr_time - start_time).total_seconds()
    ratio_time_max_hr = time_to_max_hr / length_of_activity

    # Time to avg HR 
    try:
        first_cross = df.loc[df["heart_rate"] >= avg_hr, "timestamp"].iloc[0]
        time_to_avg_hr = (first_cross - start_time).total_seconds()
        ratio_time_avg_hr = time_to_avg_hr / length_of_activity
    except IndexError:
        time_to_avg_hr = None
        ratio_time_avg_hr = None

    # HR volatility (std) 
    hr_volatility = df["heart_rate"].std()

    # HR derivative (harshness of change)
    hr_derivative = df["heart_rate"].diff().abs().mean()

    # HR drift 
    n = len(df)
    first_half_mean = df["heart_rate"][:n//2].mean()
    second_half_mean = df["heart_rate"][n//2:].mean()
    hr_drift = (second_half_mean - first_half_mean) / first_half_mean

    # HR efficiency 
    total_beats = df["heart_rate"].sum() / 60
    mpb = summary["total_distance"] / total_beats if total_beats > 0 else None

    # HR plateau duration 
    plateau_seconds = (df["heart_rate"] == max_hr).sum()

    #  HR vs pace coupling 
    try:
        coupling = df["heart_rate"].corr(df["enhanced_speed"])
    except Exception:
        coupling = None

    # HR smoothness 
    hr_smoothness = 1 / hr_derivative if hr_derivative != 0 else None

    #  HR oscillation index 
    hr_oscillation = df["heart_rate"].diff().abs().rolling(10).mean().mean()

    # Start HR offset 
    start_hr_offset = df["heart_rate"].iloc[0] - avg_hr

    # Return all metrics
    return {
        "start_time" : start_time,

        "ratio_time_max_hr": ratio_time_max_hr,
        "ratio_time_avg_hr": ratio_time_avg_hr,

        "hr_volatility": hr_volatility,
        "hr_derivative": hr_derivative,
        "hr_smoothness": hr_smoothness,
        "hr_oscillation": hr_oscillation,

        "hr_drift": hr_drift,

        "meters_per_beat": mpb,

        "plateau_seconds": plateau_seconds,

        "hr_pace_coupling": coupling,

        "start_hr_offset": start_hr_offset,
    }


def calculate_cadence_metrics(df,summary):

    # Basic values
    total_distance = summary["total_distance"]
    total_strides = summary["total_strides"]

    # Cadence stability 
    cadence_std = df["cadence"].std()
    cadence_cv = cadence_std / df["cadence"].mean() if df["cadence"].mean() else None

    # Cadence drift 
    n = len(df)
    first_half_mean = df["cadence"][:n//2].mean()
    second_half_mean = df["cadence"][n//2:].mean()
    cadence_drift = (second_half_mean - first_half_mean) / first_half_mean if first_half_mean else None

    #  Cadence derivative (harshness) 
    cadence_derivative = df["cadence"].diff().abs().mean()
    cadence_smoothness = 1 / cadence_derivative if cadence_derivative != 0 else None

    # Cadence–speed coupling
    try:
        cadence_speed_coupling = df["cadence"].corr(df["enhanced_speed"])
    except Exception:
        cadence_speed_coupling = None

    #  Cadence–HR coupling 
    try:
        cadence_hr_coupling = df["cadence"].corr(df["heart_rate"])
    except Exception:
        cadence_hr_coupling = None

    # Steps per meter (efficiency) 
    if total_distance and total_distance > 0:
        steps_per_meter = total_strides / total_distance
    else:
        steps_per_meter = None

    # 1. True running cadence (≥ 70)
    running_mask = df["cadence"] >= 70
    if running_mask.any():
        running_start_idx = running_mask.idxmax()
        running_start_cadence = df["cadence"].loc[running_start_idx]

    # 2. If no running cadence, use first non-zero cadence
    elif (df["cadence"] > 0).any():
        running_start_idx = (df["cadence"] > 0).idxmax()
        running_start_cadence = df["cadence"].loc[running_start_idx]

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

        "running_start_cadence" : running_start_cadence,

    }


def calculate_speed_metrics(df,summary):

    # Basic values
    avg_speed = summary["total_distance"] / summary["total_timer_time"]
    max_speed = df["enhanced_speed"].max()

    # Speed stability 
    speed_std = df["enhanced_speed"].std()
    speed_cv = speed_std / df["enhanced_speed"].mean() if df["enhanced_speed"].mean() else None

    # Speed drift
    n = len(df)
    first_half_mean = df["enhanced_speed"][:n//2].mean()
    second_half_mean = df["enhanced_speed"][n//2:].mean()
    speed_drift = (second_half_mean - first_half_mean) / first_half_mean if first_half_mean else None

    # Speed derivative (harshness) 
    speed_derivative = df["enhanced_speed"].diff().abs().mean()
    speed_smoothness = 1 / speed_derivative if speed_derivative != 0 else None

    # Speed oscillation index 
    speed_oscillation = df["enhanced_speed"].diff().abs().rolling(10).mean().mean()

    # Speed–HR coupling 
    try:
        speed_hr_coupling = df["enhanced_speed"].corr(df["heart_rate"])
    except Exception:
        speed_hr_coupling = None

    # Speed–cadence coupling 
    try:
        speed_cadence_coupling = df["enhanced_speed"].corr(df["cadence"])
    except Exception:
        speed_cadence_coupling = None

    try:
        running_start_idx = df.index[df["enhanced_speed"] >= 1.5][0]
        running_start_speed = df.loc[running_start_idx, "enhanced_speed"]
    except Exception:
        running_start_speed = None


    return {
        "durationSeconds" : summary["total_timer_time"],
        "distanceMeters" : summary["total_distance"],

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
    df["stride_length"] = df["distance_diff"] / (df["cadence"] / 60).replace(0, pd.NA)

    # Drop invalid stride lengths
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
            "start_stride_offset": None,
        }

    # Stride stability
    stride_std = stride_series.std()
    stride_cv = stride_std / stride_series.mean() if stride_series.mean() else None

    # Stride drift 
    n = len(stride_series)
    first_half_mean = stride_series.iloc[:n//2].mean()
    second_half_mean = stride_series.iloc[n//2:].mean()
    stride_drift = (second_half_mean - first_half_mean) / first_half_mean if first_half_mean else None

    # Stride derivative (harshness)
    stride_derivative = stride_series.diff().abs().mean()
    stride_smoothness = 1 / stride_derivative if stride_derivative != 0 else None

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

    #  Start stride offset (readiness) 
    try:
        running_start_idx = df.index[df["cadence"] >= 70][0]
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


def get_metrics(file_name):
    # Load data
    df = fit_to_df_record(file_name)
    summary = extract_session_summary(file_name)

    hr_met = calculate_heart_metrics(df,summary)
    cad_met = calculate_cadence_metrics(df,summary)
    speed_met = calculate_speed_metrics(df,summary)
    stride_met = calculate_stride_metrics(df)

    metric = {**hr_met,**cad_met,**speed_met,**stride_met}

    return metric
