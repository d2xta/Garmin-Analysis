
from pathlib import Path
import pandas as pd

import json

from src.helper import extract_useful_garmin_fields, datetime_to_garmin_ms
from src.computation import get_metrics


def get_all_activities(folder_path, summary_file):

    folder = Path(folder_path)
    fitfiles = list(folder.iterdir())

    summary_json = extract_useful_garmin_fields(summary_file)

    all_activities = []

    for i, file in enumerate(fitfiles, start=1):
        print(f"Processing {i}/{len(fitfiles)}: {file.name}")

        # Get all calculated metrics for this file (uses file data to calculate other useful stats)
        metrics = get_metrics(file)

        activity_start = metrics["start_time"]
        start_ms = datetime_to_garmin_ms(activity_start)

        # Get the matching record from the summary based off start time
        record = summary_json[summary_json["startTimeGmt"].astype("int64") == int(start_ms)]

        if len(record) == 0:
            print("No matching summary row for:", file)
            file.unlink()
            continue

        record_dict = record.iloc[0].to_dict()

        all_activities.append({
            **metrics,
            **record_dict,
        })
    
    return all_activities


def load_fitness_trends(predictions_file,
                        training_file,
                        maxmet_file):
    
    predictions_df = pd.read_json(predictions_file)
    training_df = pd.read_json(training_file)
    maxmet_df = pd.read_json(maxmet_file)

    # Merge them together  using 'calendarDate'
    merged_df = pd.merge(predictions_df, training_df, on="calendarDate", how="outer")
    merged_df = pd.merge(merged_df, maxmet_df, on="calendarDate", how="outer")

    return merged_df


# takes raw json files and returns merged df
def merge_json_files(file_list) -> pd.DataFrame:

    merged = []

    for file in file_list:
        with open(file, "r") as f:
            data = json.load(f)

            if isinstance(data, list):
                print(f"Adding {len(data)} records from: {file.name}")
                merged.extend(data)
            else:
                print(f"Skipping {file.name}: Not a list of records")

    print(f"Total merged records: {len(merged)}")

    # Flatten nested dictionaries
    df = pd.json_normalize(merged)

    return df


