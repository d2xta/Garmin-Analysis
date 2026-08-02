
# removes unecessary columns and adds a total sleep column
def clean_sleep(sleep_df):

    columns_to_remove = [
        'sleepWindowConfirmationType', 'unmeasurableSeconds', 'retro',
        'spo2SleepSummary.userProfilePk', 'spo2SleepSummary.deviceId',
        'spo2SleepSummary.sleepMeasurementStartGMT',
        'spo2SleepSummary.sleepMeasurementEndGMT',
        'sleepScores.insight'
    ]

    sleep_df = sleep_df.drop(columns=columns_to_remove, errors="ignore")

        # Fixes problem from flattening json
    sleep_df.columns = sleep_df.columns.str.replace(r"^sleepScores\.", "", regex=True)
    sleep_df.columns = sleep_df.columns.str.replace(r"^spo2SleepSummary\.", "", regex=True)

    # garmin records 0 rem as Null - we want 0 for the calculation.
    sleep_df["remSleepSeconds"] = sleep_df["remSleepSeconds"].fillna(0)

    sleep_df["totalSleepSeconds"] = sleep_df["remSleepSeconds"] + sleep_df["deepSleepSeconds"] + sleep_df["lightSleepSeconds"]


    return sleep_df
