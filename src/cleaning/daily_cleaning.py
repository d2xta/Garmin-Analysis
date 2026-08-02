
import pandas as pd

def clean_UDS(df):

    df = get_stress(df)
    df = extract_body_battery(df)

    columns_to_keep = [
        "calendarDate","activeKilocalories","bmrKilocalories",
        "totalSteps","totalDistanceMeters","highlyActiveSeconds",
        "activeSeconds","moderateIntensityMinutes","vigorousIntensityMinutes",
        "minHeartRate","maxHeartRate","currentDayRestingHeartRate",
        "minAvgHeartRate","maxAvgHeartRate","averageSpo2Value",
        "lowestSpo2Value","hydration.sweatLossInML","respiration.highestRespirationValue",
        "respiration.lowestRespirationValue","respiration.avgWakingRespirationValue",
        "bodyBattery.chargedValue","bodyBattery.drainedValue","bodyBattery.endBattery","bodyBattery.minBattery",
        "bodyBattery.maxBattery","allDayStress.averageStressLevel","allDayStress.maxStressLevel",
        "allDayStress.lowDuration","allDayStress.mediumDuration","allDayStress.highDuration"]

    df = df[columns_to_keep]

    return df


def get_stress(df):
    # Extract the AWAKE dict
    df["allDayStress"] = [
        next((d for d in lst if d.get("type") == "AWAKE"), None)
        if isinstance(lst, list) else None
        for lst in df["allDayStress.aggregatorList"]
    ]

    # Expand dict into columns
    stress_expanded = df["allDayStress"].apply(pd.Series).add_prefix("allDayStress.")

    # Merge back into df
    df = pd.concat([df, stress_expanded], axis=1)

    return df



def extract_body_battery(df):

    bodyBatteryLowest = [
        next((d for d in lst if d.get("bodyBatteryStatType") == "LOWEST"), None)
        if isinstance(lst, list) else None
        for lst in df["bodyBattery.bodyBatteryStatList"]
    ]

    df["bodyBattery.minBattery"] = [d.get("statsValue") if d is not None else None for d in bodyBatteryLowest]

    bodyBatteryMax = [
        next((d for d in lst if d.get("bodyBatteryStatType") == "HIGHEST"), None)
        if isinstance(lst, list) else None
        for lst in df["bodyBattery.bodyBatteryStatList"]
    ]

    df["bodyBattery.maxBattery"] = [d.get("statsValue") if d is not None else None for d in bodyBatteryMax]

    bodyBatteryEnd = [
        next((d for d in lst if d.get("bodyBatteryStatType") == "SLEEPSTART"), None)
        if isinstance(lst, list) else None
        for lst in df["bodyBattery.bodyBatteryStatList"]
    ]

    df["bodyBattery.endBattery"] = [d.get("statsValue") if d is not None else None for d in bodyBatteryEnd]

    return df
