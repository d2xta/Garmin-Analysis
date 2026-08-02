import pandas as pd


def is_activity_file(dfs):
    # An activity file will almost always have these specific keys
    required_keys = {'record', 'session', 'activity'}
    # Check if the keys in our file contain the required keys
    return required_keys.issubset(dfs.keys())


def is_running_activity(df):
    # Must have the core running fields
    required = {"cadence", "enhanced_speed", "distance"}
    if not required.issubset(df.columns):
        return False

    # Must have some real running cadence
    if (df["cadence"] >= 70).sum() == 0:
        return False

    # Must have some real running speed
    if (df["enhanced_speed"] >= 1.5).sum() == 0:
        return False

    return True


def extract_useful_garmin_fields(summary_file):

    summary_df = pd.read_json(summary_file)

    useful_keys = [
        "avgHr",
        "maxHr",
        "avgRunCadence",
        "maxRunCadence",
        "avgStrideLength",
        "steps",
        "activityTrainingLoad",
        "aerobicTrainingEffect",
        "anaerobicTrainingEffect",
        "trainingEffectLabel",
        "vigorousIntensityMinutes",
        "moderateIntensityMinutes",
        "maxTemperature",
        "minTemperature",
        "calendarDate",
        "startTimeGmt",
    ]

    summary_df = summary_df[useful_keys]
    return summary_df


def datetime_to_garmin_ms(dt):
    return int(dt.timestamp() * 1000)



#  Convert decimal bedtime values back into readable clock times for interpretation.
def decimal_to_time(t):
    t = t % 24
    h = int(t)
    m = int(round((t - h) * 60))
    
    if m == 60:
        h = (h + 1) % 24
        m = 0
        
    return f"{h:02d}:{m:02d}"

