import os

from src.d00_utils.utils import load_yml


PREFIX = ".." if os.path.basename(os.getcwd()) == "src" else ""
# For Jupyter notebook testing
if os.path.basename(os.getcwd()) == "notebooks":
    PREFIX = ".."

# API URLs
EIA_URL = "https://api.eia.gov/series/?series_id={}&api_key={}&out=json"

# Data Folder Paths
RAW_DATA_FOLDER = os.path.join(PREFIX, 'data/01_raw/')
INTERMEDIATE_DATA_FOLDER = os.path.join(PREFIX, 'data/02_intermediate/')
PROCESSED_DATA_FOLDER = os.path.join(PREFIX, 'data/03_processed/')
MODELS_FOLDER = os.path.join(PREFIX, 'data/04_models/')
REPORTING_FOLDER = os.path.join(PREFIX, 'data/06_reporting/')

# Documentation Path
APPENDIX_FILEPATH = os.path.join(PREFIX, 'docs/source/appendix.md')

# YML File Paths
EIA_API_IDS_YML_FILEPATH = os.path.join(PREFIX, 'conf/base/eia_api_ids.yml')
EMISSIONS_FACTORS_YML_FILEPATH = os.path.join(PREFIX, 'conf/base/emissions_factors.yml')
STATES_YML_FILEPATH = os.path.join(PREFIX, 'conf/base/states.yml')
STREAMLIT_CONFIG_FILEPATH = os.path.join(PREFIX, 'conf/base/config_streamlit.toml')

# Only send full names of states to functions
STATES = list(load_yml(STATES_YML_FILEPATH).keys())




