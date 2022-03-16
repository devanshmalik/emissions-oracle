# Python Libraries
import json
import logging

# Package Imports
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json

# First Party Imports
from src.d00_utils.const import MODELS_FOLDER, PROCESSED_DATA_FOLDER, STATES
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class ModelTrainer:
    net_gen_fuels = [
        "all_sources",
        "coal",
        "natural_gas",
        "nuclear",
        "hydro",
        "wind",
        "solar_all",
        "other",
    ]
    total_consumption_fuels = ["coal", "natural_gas"]
    """Class to train Facebook Prophet models"""

    def __init__(self, data_type: str):
        """
        Parameters
        ------------
        data_type: str
            Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
            This string is used when creating folders to save respective data
            and for column names within each dataframe
        """
        self.data_type = data_type
        self.save_folder = ""

    def train_models(self):
        """Train and Save Prophet models for each state and each type of generation source."""
        for state in STATES:
            log.info(f"Training models for State: {state}")
            self.save_folder = "{}/{}".format(self.data_type, state)

            if self.data_type == "Net_Gen_By_Fuel_MWh":
                fuel_types = ModelTrainer.net_gen_fuels
            elif self.data_type == "Fuel_Consumption_BTU":
                fuel_types = ModelTrainer.total_consumption_fuels
            else:
                raise ValueError(f"Unexpected EIA Data Type encountered: {self.data_type}")

            for fuel_type in fuel_types:
                df = self._read_processed_data(fuel_type)
                model = self._fit_model(df)
                self._save_model(model, fuel_type)

    def _read_processed_data(self, fuel_type: str) -> pd.DataFrame:
        """Reads data from processed folder for specific fuel type."""
        processed_file_name = "{}-{}.{}".format(self.data_type, fuel_type, "csv")
        processed_file_path = get_filepath(
            PROCESSED_DATA_FOLDER, self.save_folder, processed_file_name
        )
        return pd.read_csv(processed_file_path)

    @staticmethod
    def _fit_model(df: pd.DataFrame) -> Prophet:
        """Train Prophet model using the input processed dataframe"""
        model = Prophet()
        model.fit(df)
        return model

    def _save_model(self, model: Prophet, fuel_type: str):
        """Save trained Prophet model as a JSON object."""
        models_file_name = "{}-{}.{}".format(self.data_type, fuel_type, "json")
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, models_file_name)

        with open(models_file_path, "w") as fout:
            json.dump(model_to_json(model), fout)
