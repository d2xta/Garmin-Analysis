import pandas as pd


def assign_bedtime_bins(
    df,
    bedtime_bins=[20, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, 29],
    bedtime_labels=[
        "Before 21:00", "21:00-21:30", "21:30-22:00", "22:00-22:30",
        "22:30-23:00", "23:00-23:30", "23:30-00:00", "00:00-00:30",
        "00:30-01:00", "After 01:00"
    ]
):
    """
    Assign bedtime bins based on decimalStartTime.
    Adds a new column 'bedtime_bin'.
    """
    df["bedtime_bin"] = pd.cut(
        df["decimalStartTime"],
        bins=bedtime_bins,
        labels=bedtime_labels,
        right=False
    )
    return df


def assign_sleep_bins(
    df,
    sleep_bins=[0, 7, 8, 9, 12],
    sleep_labels=["<7h", "7-8h", "8-9h", "9h+"]
):
    """
    Assign sleep duration bins based on sleep_hours.
    Adds a new column 'sleep_bin'.
    """
    df["sleep_bin"] = pd.cut(
        df["sleep_hours"],
        bins=sleep_bins,
        labels=sleep_labels,
        right=False
    )
    return df
