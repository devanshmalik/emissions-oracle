#TODO: Create an interface class to run different steps of model pipeline

from src.d00_utils.utils import setup_env_vars
from src.d01_data.get_raw_data import load_data
from src.d03_processing.create_model_input import process_data
from src.d04_modelling.create_prophet_models import train_models
from src.d06_reporting.create_forecasts import create_forecasts

setup_env_vars()
load_data()
process_data()
train_models()
create_forecasts()