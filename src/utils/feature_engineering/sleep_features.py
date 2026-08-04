import pandas as pd



def add_sleep_features(df):
    sleep_df = df.copy()

    sleep_df["sleepStartTimestampGMT"] = pd.to_datetime(sleep_df["sleepStartTimestampGMT"])
    sleep_df["sleepEndTimestampGMT"] = pd.to_datetime(sleep_df["sleepEndTimestampGMT"])

    # Get sleep start time as a decimal value (9:15PM -> 21.25)
    sleep_df["decimalStartTime"] = (
        sleep_df["sleepStartTimestampGMT"].dt.hour
        + sleep_df["sleepStartTimestampGMT"].dt.minute / 60
        + sleep_df["sleepStartTimestampGMT"].dt.second / 3600
    )

    sleep_df["decimalEndTime"] = (
        sleep_df["sleepEndTimestampGMT"].dt.hour
        + sleep_df["sleepEndTimestampGMT"].dt.minute / 60
        + sleep_df["sleepEndTimestampGMT"].dt.second / 3600
    )


    # Deal with sleeps after midnight
    sleep_df.loc[sleep_df["decimalStartTime"] < 12, "decimalStartTime"] += 24

    # Numbers of hours slept for
    sleep_df["sleep_hours"] = sleep_df["totalSleepSeconds"] / 3600

    # Number of hours in bed total
    sleep_df["hours_in_bed"] = (
        sleep_df["sleepEndTimestampGMT"] - sleep_df["sleepStartTimestampGMT"]
    ).dt.total_seconds() / 3600

    # how efficient sleep is - based on awake time
    sleep_df["sleep_efficiency"] = sleep_df["sleep_hours"] / sleep_df["hours_in_bed"]


    sleep_df["calendarDate"] = pd.to_datetime(sleep_df["calendarDate"])
    # Subtract 1 day for bedtimes past midnight (>= 24.0)
    logical_date = sleep_df["calendarDate"].where(
        sleep_df["decimalStartTime"] < 24.0,
        sleep_df["calendarDate"] - pd.Timedelta(days=1)
    )

    # Day of Week based on adjusted logical date
    sleep_df["day_of_week"] = logical_date.dt.day_name()

    # centers sleep/bedtime - the means are at 0
    sleep_df["centered_sleep_hours"] = (
    sleep_df["sleep_hours"] - sleep_df["sleep_hours"].mean()
)
    sleep_df["centered_bed_time"] = (
    sleep_df["decimalStartTime"] - sleep_df["decimalStartTime"].mean()
)

    return sleep_df

