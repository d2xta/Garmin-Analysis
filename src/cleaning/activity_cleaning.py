
import pandas as pd

from src.utils.feature_engineering.activity_metrics import get_metrics
from src.utils.fit_loaders import get_start_time



def clean_activity_summary(summary_files: list):

    # Load both JSON files
    df1 = pd.read_json(summary_files[0])
    df2 = pd.read_json(summary_files[1])

    # Combine activity lists
    activities = df1["summarizedActivitiesExport"][0] + df2["summarizedActivitiesExport"][0]

    # Columns we want to keep
    columns_to_keep = {'startTimeGmt','elevationGain','durationSeconds','distanceMeters',
        'avgSpeed', 'maxSpeed', 'avgHr', 'maxHr', 'minHr', 'avgRunCadence','activityName',
        'maxRunCadence', 'steps', 'aerobicTrainingEffect', 'avgStrideLength',
        'anaerobicTrainingEffect', 'minTemperature', 'maxTemperature', 'trainingEffectLabel',
        'activityTrainingLoad','aerobicTrainingEffectMessage', 'anaerobicTrainingEffectMessage', 'moderateIntensityMinutes',
        'vigorousIntensityMinutes', 'hrTimeInZone_0', 'hrTimeInZone_1', 'hrTimeInZone_2',
        'hrTimeInZone_3', 'hrTimeInZone_4', 'hrTimeInZone_5', 'hrTimeInZone_6'
    }

    cleaned_records = []

    for idx, activity in enumerate(activities):

        # Filter only running
        if activity.get("sportType") != "RUNNING" or activity.get('locationName') is None:
            print(f"Skipping {idx + 1}/{len(activities)}: {activity.get('name')} ({activity.get('sportType')})")
            continue

        print(f"Processing {idx + 1}/{len(activities)}: {activity.get('name')}")

        if activity['avgStrideLength'] is not None:
            activity['avgStrideLength'] = float(activity['avgStrideLength']) / 100
        if activity['elevationGain'] is not None:
             activity['elevationGain'] = float(activity['elevationGain']) / 100
        try:
            activity['durationSeconds'] = activity['movingDuration'] / 1000 # Convert to seconds
            activity['distanceMeters'] = activity['distance'] / 100 # Convert cm to meters
        except:
             continue
        activity['avgSpeed'] = activity['avgSpeed'] * 10 # weird Garmin quirk, avgSpeed is in decimeters per second
        activity["activityName"] = activity["name"]

                # Build a clean dict directly 
        record = {col: activity.get(col) for col in columns_to_keep}

        cleaned_records.append(record)

    # Build final DataFrame
    return pd.DataFrame(cleaned_records)



def combine_activities(fit_files, summaries):

    all_activities = []

    for i, file in enumerate(fit_files, start=1):
            print(f"Processing {i}/{len(fit_files)}: {file.name}")

            # get the start time of activity - this is like a primary key to scync summary and fit
            start_time = get_start_time(file)
            activity_start = start_time.timestamp() * 1000

            # Get the matching record from the summary based off start time
            
            matching = summaries[summaries["startTimeGmt"].astype("int64") == int(activity_start)]

            if len(matching) == 0:
                print("No matching summary row for:", file)
                file.unlink()
                continue

            record = matching.iloc[0].copy()
            record["activityStartTimestampGMT"] = start_time

            # Get all calculated metrics for this file (uses file data to calculate other useful stats)
            metrics = get_metrics(file, record)
            

            record_dict = record.to_dict()

            combined = {**metrics, **record_dict}

            combined["calendarDate"] = pd.to_datetime(combined["start_time"]).strftime("%Y-%m-%d")
            combined["activityStartTimestampGMT"] = combined["activityStartTimestampGMT"].isoformat()
            all_activities.append(combined)

    return all_activities






