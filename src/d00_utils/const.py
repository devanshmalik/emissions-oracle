import os
import yaml

PREFIX = ".." if os.path.basename(os.getcwd()) == "src" else ""

# API URLs
EIA_URL = "https://api.eia.gov/series/?series_id={}&api_key={}&out=json"

# Data Folder Paths
RAW_DATA_FOLDER = os.path.join(PREFIX, 'data/01_raw/')
INTERMEDIATE_DATA_FOLDER = os.path.join(PREFIX, 'data/02_intermediate/')
PROCESSED_DATA_FOLDER = os.path.join(PREFIX, 'data/03_processed/')
MODELS_FOLDER = os.path.join(PREFIX, 'data/04_models/')
REPORTING_FOLDER = os.path.join(PREFIX, 'data/06_reporting/')


# States of interest
def get_states_yml():
    states_yaml = open(STATES_YML_FILE_PATH)
    return yaml.load(states_yaml, Loader=yaml.FullLoader)


STATES_YML_FILE_PATH = os.path.join(PREFIX, 'conf/base/states.yml')
STATES = get_states_yml()


