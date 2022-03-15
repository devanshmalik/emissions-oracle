import warnings
import logging

from src.d00_utils.const import *
from src.d00_utils.utils import setup_env_vars, load_yml
from src.d01_data.get_raw_data import EIADataPull
from src.d02_intermediate.clean_raw_data import DataCleaner
from src.d03_processing.create_model_input import DataPreprocessor
from src.d04_modelling.create_prophet_models import ModelTrainer
from src.d06_reporting.create_forecasts import ModelForecast, combine_all_states_generation
from src.d06_reporting.calculate_emissions import EmissionsCalculator

# Suppress Future Warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class PipelineInterface:
    """Interface class to access and run modular components of the data pipeline."""

    def __init__(self, eia_api_ids_yml_filepath: str, emissions_factors_yml_filepath: str):
        """
        Load EIA API IDs and Emissions Factors from respective YAML filepaths.
        Set up environment variables which contain API Access keys.

        :param eia_api_ids_yml_filepath:
            Filepath to YAML containing all IDs for data to be pulled from EIA API
        :param emissions_factors_yml_filepath:
            Filepath to YAML containing emissions factors for all types of generation
        """
        self.eia_api_ids = load_yml(eia_api_ids_yml_filepath)
        self.emissions_factors = load_yml(emissions_factors_yml_filepath)
        setup_env_vars()

    def pull_data(self):
        """Use the EIA API to pull data for all data type IDs in the yml for each state in states yml."""
        for data_type, api_ids_dict in self.eia_api_ids.items():
            log.info(f"Loading raw data for {data_type}")
            eia_data_pull = EIADataPull(api_ids_dict=api_ids_dict, data_type=data_type)
            eia_data_pull.load_data()
        log.info("Finished loading all raw data.")

    def clean_data(self):
        """Clean pulled raw data in two steps:
        1) Convert raw data from JSON to CSV format (for failed API requests, create empty CSV)
        2) Impute missing data for time periods with no entry (implies no generation in that period)
        """
        for data_type, api_ids_dict in self.eia_api_ids.items():
            log.info(f"Cleaning raw data for {data_type}")
            data_cleaner = DataCleaner(api_ids_dict=api_ids_dict, data_type=data_type)
            data_cleaner.clean_data()

    def process_data(self):
        """
        Process each type of data (net generation and fuel consumption) and perform
        required feature engineering to finalize datasets as input to training models.
        """
        for data_type, api_ids_dict in self.eia_api_ids.items():
            log.info(f"Processing intermediate data for {data_type}")
            data_process = DataPreprocessor(api_ids_dict=api_ids_dict, data_type=data_type)
            data_process.process_data()
        log.info("Finished processing intermediate data.")

    def train_models(self):
        """Train and Save time-forecasting Prophet models"""
        for data_type in self.eia_api_ids.keys():
            log.info(f"Training and Saving Prophet Models for Category: {data_type}")
            model_trainer = ModelTrainer(data_type=data_type)
            model_trainer.train_models()
        log.info("Finished training Prophet models.")

    def create_forecasts(self):
        """
        Performs two steps:
        1) Imports each prophet model and creates individual forecasts for time periods till 2025
        2) Combines individual forecasts into a combined dataframe for each state. For example:
            - For Alabama state, it will create two CSVs - Net Elec. Gen and Fuel Consumption
            - Each CSV will have one column for each type of generation i.e Net Elec. Gen will have
            one column for each type of generation source (coal, solar, wind, etc.)
        """
        log.info("Creating forecasts for all Prophet Models...")
        for data_type in self.eia_api_ids.keys():
            log.info(f"Creating forecasts for Category: {data_type}")
            model_forecaster = ModelForecast(data_type=data_type)
            model_forecaster.forecast()
        log.info("Finished all forecasting")
        combine_all_states_generation()

    def calculate_emissions(self):
        """
        Performs three types of emissions calculations:
        1) Total Emissions Calculation: For each state, calculates emissions for each generation type
        2) Emissions Intensity: Calculates emissions intensity for each state using total generation and total emissions
        3) Combine State Emissions: Saves a combined CSV of all states for both total emissions and emissions intensity
        """
        log.info("Calculating emissions for all regions...")
        emissions_calculator = EmissionsCalculator(emission_factors=self.emissions_factors)
        emissions_calculator.calculate_total_emissions()
        emissions_calculator.calculate_emissions_intensity()
        emissions_calculator.combine_state_emissions()
        log.info("Finished all emission calculations")


# Sample code to run all pipeline steps
interface = PipelineInterface(EIA_API_IDS_YML_FILEPATH, EMISSIONS_FACTORS_YML_FILEPATH)
interface.pull_data()
interface.clean_data()
interface.process_data()
interface.train_models()
interface.create_forecasts()
interface.calculate_emissions()
