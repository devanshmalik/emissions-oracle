# TODO: Create an interface class to run different steps of model pipeline
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from src.d00_utils.const import *
from src.d00_utils.utils import setup_env_vars, load_yml
from src.d01_data.get_raw_data import load_all_data
from src.d02_intermediate.clean_raw_data import clean_all_data
from src.d03_processing.create_model_input import process_all_data
from src.d04_modelling.create_prophet_models import train_all_models
from src.d06_reporting.create_forecasts import create_all_forecasts
from src.d06_reporting.calculate_emissions import calculate_emissions


# setup_env_vars()
# eia_api_ids = load_yml(EIA_API_IDS_YML_FILEPATH)
# load_all_data(eia_api_ids)
# clean_all_data(eia_api_ids)
# process_all_data(eia_api_ids)
# train_all_models(eia_api_ids)
# create_all_forecasts(eia_api_ids)

# Emissions Calculation
emission_factors = load_yml(EMISSIONS_FACTORS_YML_FILEPATH)
calculate_emissions(emission_factors)
