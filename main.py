from pathlib import Path
import pandas as pd
import json

from src.database.database import *
from src.cleaning.sleep_cleaning import clean_sleep
from src.cleaning.daily_cleaning import clean_UDS
from src.cleaning.activity_cleaning import clean_activity_summary, combine_activities

con = get_connection(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\garmin.db')

initialise_database(con, schema_path=r'C:\Users\Dexta\Learning\Garmin-Analysis\src\database\schema.sql')

#-----------------------------------------------------------------------------------------------------------
# For inserting activities 

activities_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\Activity_FITS')

summary_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Fitness')
summary_files = list(summary_folder.glob("*Activities.json"))

clean_summary_df = clean_activity_summary(summary_files)

activities = combine_activities(list(activities_folder.glob("*.fit")), clean_summary_df)
insert_activities(con,activities)

#-----------------------------------------------------------------------------------------------------------
# For inserting daiy stats

aggregator_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Aggregator')
UDS_files = list(aggregator_folder.glob("UDS*"))

records = []

for file in UDS_files:
    with open(file, "r") as f:
        data = json.load(f)
        if isinstance(data, list):
            records.extend(data)

merged_UDS_df = pd.json_normalize(records)
clean_UDS_df = clean_UDS(merged_UDS_df)

insert_daily_summary(con, clean_UDS_df)

#-----------------------------------------------------------------------------------------------------------
# For inserting sleep files 

# raw sleep files are stored in the wellness folder
wellness_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Wellness')
sleep_files = list(wellness_folder.glob("*sleepData.json"))

records = []

for file in sleep_files:
    with open(file, "r") as f:
        data = json.load(f)
        if isinstance(data, list):
            records.extend(data)

merged_sleep_df = pd.json_normalize(records)
clean_sleep_df = clean_sleep(merged_sleep_df)

insert_sleep(con, clean_sleep_df)

con.close()