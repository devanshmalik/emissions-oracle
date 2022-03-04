import logging
import pandas as pd
from prophet import Prophet
import json
from prophet.serialize import model_to_json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ModelTrainer:
    net_gen_fuels = ['all_fuels', 'coal', 'natural_gas', 'nuclear',
                     'hydro', 'wind', 'solar_all', 'other']
    total_consumption_fuels = ['coal', 'natural_gas']
    """Class to train Facebook Prophet models"""
    def __init__(self, data_type):
        self.data_type = data_type
        self.save_folder = ""

    def train_models(self):
        for state in STATES:
            log.info(f"Training models for State: {state}")
            self.save_folder = '{}/{}'.format(self.data_type, state)

            if self.data_type == 'Net_Gen_By_Fuel_MWh':
                fuel_types = ModelTrainer.net_gen_fuels
            elif self.data_type == "Fuel_Consumption_BTU":
                fuel_types = ModelTrainer.total_consumption_fuels
            else:
                raise ValueError(f"Unexpected EIA Data Type encountered: {self.data_type}")

            log.info(f"Training models for Category: {self.data_type}")
            for fuel_type in fuel_types:
                df = self.read_processed_data(fuel_type)
                model = self.fit_model(df)
                self.save_model(model, fuel_type)
            log.info(f"Finished models for State: {state}")

    def read_processed_data(self, fuel_type):
        """
        Reads data from processed folder for specific fuel type
        :param fuel_type:
        :return:
        """
        processed_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, processed_file_name)
        return pd.read_csv(processed_file_path)

    @staticmethod
    def fit_model(df):
        """Train Prophet model using the input processed dataframe"""
        model = Prophet()
        model.fit(df)
        return model

    def save_model(self, model, fuel_type):
        """Save trained Prophet model as a json."""
        models_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'json')
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, models_file_name)

        with open(models_file_path, 'w') as fout:
            json.dump(model_to_json(model), fout)


def train_all_models(eia_api_ids):
    log.info("Training and Saving Prophet Models...")
    for data_type in eia_api_ids.keys():
        model_trainer = ModelTrainer(data_type=data_type)
        model_trainer.train_models()
    log.info("Finished training Prophet models.")
