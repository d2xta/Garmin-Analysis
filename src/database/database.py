
import sqlite3
import pandas as pd


def get_connection(db_path):
    """Create a database connection and ensure foreign keys are enabled."""
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def initialise_database(con, schema_path="schema.sql"):
    """Reads schema.sql and creates the tables/indexes."""
    with open(schema_path, "r") as f:
        schema_script = f.read()
    
    with con:
        con.executescript(schema_script)
    print("Database schema initialized successfully.")


# Inserting !

def insert_activities(con, activities):
    columns = [
        "startTimeGmt", "calendarDate", "start_time", "activity_type",
        "durationSeconds", "distanceMeters", "ratio_time_max_hr", "ratio_time_avg_hr", 
        "hr_volatility", "hr_derivative", "hr_smoothness", "hr_oscillation", "hr_drift",
        "meters_per_beat", "plateau_seconds", "hr_pace_coupling", "start_hr_offset",
        "cadence_std", "cadence_cv", "cadence_drift", "cadence_derivative",
        "cadence_smoothness", "cadence_speed_coupling", "cadence_hr_coupling",
        "steps_per_meter", "running_start_cadence", "avg_speed", "max_speed", 
        "speed_std", "speed_cv", "speed_drift", "speed_derivative", "speed_smoothness", 
        "speed_oscillation", "speed_hr_coupling", "speed_cadence_coupling", "running_start_speed",
        "stride_std", "stride_cv", "stride_drift", "stride_derivative", "stride_smoothness", 
        "stride_oscillation", "stride_speed_coupling", "stride_hr_coupling", "running_start_stride",
        "avgHr", "maxHr", "avgRunCadence", "maxRunCadence", "avgStrideLength", "steps",
        "activityTrainingLoad", "aerobicTrainingEffect", "anaerobicTrainingEffect", 
        "trainingEffectLabel", "vigorousIntensityMinutes", "moderateIntensityMinutes",
        "maxTemperature", "minTemperature"
    ]

    placeholders = ", ".join(["?"] * len(columns))
    colnames = ", ".join(columns)
    sql = f"INSERT INTO ActivitySummary ({colnames}) VALUES ({placeholders})"

    rows = []
    for act in activities:
        row = []
        for col in columns:
            val = act.get(col)
            if isinstance(val, pd.Timestamp):
                val = val.isoformat()
            row.append(val)
        rows.append(tuple(row))

    with con:
        con.executemany(sql, rows)
    print(f"Inserted {len(rows)} activities into ActivitySummary.")


def insert_daily_summary(con, df):
    """
    Insert a daily summary DataFrame into the DailySummary SQL table.
    """

    # Mapping from DataFrame column names → SQL column names
    column_map = {
        "calendarDate": "calendarDate",
        "activeKilocalories": "activeKilocalories",
        "bmrKilocalories": "bmrKilocalories",
        "totalSteps": "totalSteps",
        "totalDistanceMeters": "totalDistanceMeters",
        "highlyActiveSeconds": "highlyActiveSeconds",
        "activeSeconds": "activeSeconds",
        "moderateIntensityMinutes": "moderateIntensityMinutes",
        "vigorousIntensityMinutes": "vigorousIntensityMinutes",
        "minHeartRate": "minHeartRate",
        "maxHeartRate": "maxHeartRate",
        "currentDayRestingHeartRate": "currentDayRestingHeartRate",
        "minAvgHeartRate": "minAvgHeartRate",
        "maxAvgHeartRate": "maxAvgHeartRate",
        "averageSpo2Value": "averageSpo2Value",
        "lowestSpo2Value": "lowestSpo2Value",

        # hydration
        "hydration.sweatLossInML": "sweatLossInML",

        # respiration
        "respiration.highestRespirationValue": "highestRespirationValue",
        "respiration.lowestRespirationValue": "lowestRespirationValue",
        "respiration.avgWakingRespirationValue": "avgRespirationValue",

        # body battery
        "bodyBattery.chargedValue": "charged",
        "bodyBattery.drainedValue": "drained",
        "bodyBattery.endBattery": "endBattery",
        "bodyBattery.minBattery": "minBattery",
        "bodyBattery.maxBattery": "maxBattery",

        # stress
        "allDayStress.averageStressLevel": "averageStressLevel",
        "allDayStress.maxStressLevel": "maxStressLevel",
        "allDayStress.lowDuration": "lowStressDuration",
        "allDayStress.mediumDuration": "mediumStressDuration",
        "allDayStress.highDuration": "highStressDuration",
    }

    sql_columns = list(column_map.values())
    placeholders = ", ".join(["?"] * len(sql_columns))
    colnames = ", ".join(sql_columns)

    sql = f"INSERT OR REPLACE INTO DailySummary ({colnames}) VALUES ({placeholders})"

    # Build rows in SQL column order
    rows = []
    for _, row in df.iterrows():
        values = []
        for df_key in column_map.keys():
            values.append(row.get(df_key))
        rows.append(tuple(values))

    with con:
        con.executemany(sql, rows)

    print(f"Inserted {len(rows)} daily summary rows.")



def insert_fitness_trends(con, fitness_rows):
    columns = [
        "calendarDate", "vo2MaxValue", "maxMet", "raceTime5K", "raceTime10K", 
        "raceTimeHalf", "raceTimeMarathon", "weeklyTrainingLoadSum", 
        "trainingStatus", "fitnessLevelTrend"
    ]

    placeholders = ", ".join(["?"] * len(columns))
    colnames = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO FitnessTrends ({colnames}) VALUES ({placeholders})"

    rows = []
    for ft in fitness_rows:
        row = [ft.get(col) for col in columns]
        rows.append(tuple(row))

    with con:
        con.executemany(sql, rows)
    print(f"Inserted {len(rows)} fitness trend rows.")


def insert_sleep(con, df):

    sleep_records = df.to_dict("records") 

    query = """
    INSERT OR REPLACE INTO Sleep (
        calendarDate, sleepStartTimestampGMT, sleepEndTimestampGMT,
        deepSleepSeconds, lightSleepSeconds, remSleepSeconds, awakeSleepSeconds,
        averageRespiration, lowestRespiration, highestRespiration,
        awakeCount, avgSleepStress, overallScore, qualityScore, durationScore,
        recoveryScore, deepScore, remScore, lightScore, awakeningsCountScore,
        awakeTimeScore, combinedAwakeScore, restfulnessScore, feedback,
        averageSPO2, averageHR, lowestSPO2, totalSleepSeconds, interruptionsScore
    )
    VALUES (
        :calendarDate, :sleepStartTimestampGMT, :sleepEndTimestampGMT,
        :deepSleepSeconds, :lightSleepSeconds, :remSleepSeconds, :awakeSleepSeconds,
        :averageRespiration, :lowestRespiration, :highestRespiration,
        :awakeCount, :avgSleepStress, :overallScore, :qualityScore, :durationScore,
        :recoveryScore, :deepScore, :remScore, :lightScore, :awakeningsCountScore,
        :awakeTimeScore, :combinedAwakeScore, :restfulnessScore, :feedback,
        :averageSPO2, :averageHR, :lowestSPO2, :totalSleepSeconds, :interruptionsScore
    )
    """
    with con:
        con.executemany(query, sleep_records)
    print(f"Inserted {len(sleep_records)} sleep records.")

