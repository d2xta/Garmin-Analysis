from src.database.database import *
from src.loading import get_all_activities, merge_json_files, load_fitness_trends
from pathlib import Path

from src.cleaning.sleep_cleaning import clean_sleep
from src.cleaning.daily_cleaning import clean_UDS

con = get_connection(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\garmin.db')

initialise_database(con, schema_path=r'C:\Users\Dexta\Learning\Garmin-Analysis\src\database\schema.sql')

#--------------------------#
# For inserting activities !

# folder = r'C:\Users\Dexta\Learning\Garmin-Analysis\inital_import\DI_CONNECT\DI-Connect-Uploaded-Files\useful'
# activity_summary = r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\ActivityStatsSummary.json'
# activities = get_all_activities(folder,activity_summary)
# insert_activities(con,activities)

#------------------------------------------#
# For inserting daiy stats

# aggregator_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Aggregator')
# UDS_files = list(aggregator_folder.glob("UDS*"))

# merged_UDS_df = merge_json_files(UDS_files)
# clean_UDS_df = clean_UDS(merged_UDS_df)

# insert_daily_summary(con, clean_UDS_df)

#------------------------------------------#
# For inserting fitness trends
metrics_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Metrics')
maxMet_files = list(metrics_folder.glob("MetricsMaxMet*"))
racePrediction_files = list(metrics_folder.glob("RunRacePredictions*"))
trainingHistory_files = list(metrics_folder.glob("TrainingHistory*"))


#-----------------------------------------------------------------------------------------------------------
# For inserting sleep files !

# # raw sleep files are stored in the wellness folder
# wellness_folder = Path(r'C:\Users\Dexta\Learning\Garmin-Analysis\data\raw\DI-Connect-Wellness')
# sleep_files = list(wellness_folder.glob("*sleepData.json"))

# # a list of the merged sleep files
# merged_sleep_df = merge_json_files(sleep_files)

# # data cleaning to flatten jsons and only keep features we care for
# clean_sleep_df = clean_sleep(merged_sleep_df)

# insert_sleep(con, clean_sleep_df)

con.close()