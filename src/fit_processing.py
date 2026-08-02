from fitparse import FitFile
import fitparse
import pandas as pd

from src.helper import *


def get_fit_file_summary(file_path):
    fitfile = fitparse.FitFile(file_path)
    
    summary = {}
    
    # Iterate through every message in the file
    for message in fitfile:
        message_name = message.name
        
        # Initialize entry for this message type if not exists
        if message_name not in summary:
            summary[message_name] = set()
            
        # Collect all field names available in this message type
        for data_field in message:
            summary[message_name].add(data_field.name)
            
    # Convert sets to lists for readable output
    for key in summary:
        summary[key] = list(summary[key])
        
    return summary


def extract_all_to_dataframes(file_path):

    fitfile = fitparse.FitFile(file_path)
    
    # 2. Create a container (dictionary) to store lists of rows for each message type
    # { 'message_type': [ {field1: val, field2: val}, {field1: val, field2: val} ] }
    data_store = {}
    
    # 3. The "Translator" Loop
    for message in fitfile:
        m_name = message.name
        
        # If this is the first time we see this message type, create a new list for it
        if m_name not in data_store:
            data_store[m_name] = []
            
        # Extract fields from this specific message
        row = {}
        for field in message:
            row[field.name] = field.value
        
        # Add the row to our container
        data_store[m_name].append(row)
        
    # 4. Convert all lists into DataFrames
    dataframes = {}
    for m_name, data in data_store.items():
        dataframes[m_name] = pd.DataFrame(data)
        
    return dataframes


def fit_to_df_record(file_name):

    fit = FitFile(str(file_name))

    records = []

    for record in fit.get_messages("record"):
        data = {}
        for field in record:
            data[field.name] = field.value
        records.append(data)


    df = pd.DataFrame(records)

    useful_cols = [
        "timestamp",
        "heart_rate",
        "cadence",
        "enhanced_speed",
        "distance",
    ]
    df = df[useful_cols]
    return df


def extract_session_summary(file_name):

    fit = FitFile(str(file_name))

    # Extract raw session fields
    session_raw = {}
    for msg in fit.get_messages("session"):
        for field in msg:
            session_raw[field.name] = field.value

    # Keep only useful running fields
    useful_fields = {
        # Metadata
        "start_time": session_raw.get("start_time"),
        "end_time": session_raw.get("timestamp"),

        # Heart metrics
        "avg_heart_rate": session_raw.get("avg_heart_rate"),
        "max_heart_rate": session_raw.get("max_heart_rate"),

        # Cadence metrics
        "avg_running_cadence": session_raw.get("avg_running_cadence"),
        "max_running_cadence": session_raw.get("max_running_cadence"),
        "avg_fractional_cadence": session_raw.get("avg_fractional_cadence"),
        "max_fractional_cadence": session_raw.get("max_fractional_cadence"),

        # Distance / time
        "total_distance": session_raw.get("total_distance"),
        "total_elapsed_time": session_raw.get("total_elapsed_time"),
        "total_timer_time": session_raw.get("total_timer_time"),
        "total_strides": session_raw.get("total_strides"),

        # Elevation
        "total_ascent": session_raw.get("total_ascent"),
        "total_descent": session_raw.get("total_descent"),

        # Training effect
        "total_training_effect": session_raw.get("total_training_effect"),
        "total_anaerobic_training_effect": session_raw.get("total_anaerobic_training_effect"),
    }

    return useful_fields


def fit_to_df_record_raw(file_name):
    fit = FitFile(str(file_name))
    records = []

    for record in fit.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        records.append(row)

    return pd.DataFrame(records)


def extract_sleep_relevant_fields(activity: dict) -> dict:
    """
    Extract only the fields relevant for sleep-performance analysis.
    Removes splits, samples, GPS, corrupted summary fields, etc.
    """

    SLEEP_RELEVANT_FIELDS = {
    # Heart rate + training load
    'avgHr', 'maxHr', 'minHr',
    'hrTimeInZone_0', 'hrTimeInZone_1', 'hrTimeInZone_2',
    'hrTimeInZone_3', 'hrTimeInZone_4', 'hrTimeInZone_5', 'hrTimeInZone_6',
    'aerobicTrainingEffect', 'anaerobicTrainingEffect',
    'trainingEffectLabel', 'activityTrainingLoad',

    # Cadence + stride (neuromuscular readiness)
    'avgRunCadence', 'maxRunCadence',
    'avgDoubleCadence', 'maxDoubleCadence',
    'avgFractionalCadence', 'maxFractionalCadence',
    'avgStrideLength',

    # Effort / intensity markers
    'vigorousIntensityMinutes', 'moderateIntensityMinutes',
    'steps',

    # Environmental factors
    'minTemperature', 'maxTemperature',

    # Metadata for grouping
    'sportType', 'activityType', 'name', 'locationName',
    'startTimeGmt'
}
    
    out = {}
    for key in SLEEP_RELEVANT_FIELDS:
        out[key] = activity.get(key)
    return out
