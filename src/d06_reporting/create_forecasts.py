import logging
import pandas as pd
import json
from prophet import Prophet
from prophet.serialize import model_from_json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ModelForecast:
    """Class to create forecasts based on models trained earlier"""
    net_gen_fuels = ['all_sources', 'coal', 'natural_gas', 'nuclear', 'hydro', 'wind', 'solar_all', 'other']
    total_consumption_fuels = ['coal', 'natural_gas']

    def __init__(self, data_type: str):
        """

        Parameters
        ------------
        data_type: str
            Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
            This string is used when creating folders to save respective data and for column names within each dataframe
        """
        self.data_type = data_type
        self.save_folder = ""

    def forecast(self):
        """
        Performs two steps for each state:
        1) Imports each prophet model and creates individual forecasts for time periods till 2025
        2) Combines individual forecasts into a combined dataframe for each state. For example:
            - For Alabama state, it will create two CSVs - Net Elec. Gen and Fuel Consumption
            - Each CSV will have one column for each type of generation i.e Net Elec. Gen will have
            one column for each type of generation source (coal, solar, wind, etc.)
        """
        for state in STATES:
            log.info(f"Forecasting for State: {state}")
            self.save_folder = '{}/{}'.format(self.data_type, state)

            if self.data_type == 'Net_Gen_By_Fuel_MWh':
                fuel_types = ModelForecast.net_gen_fuels
            elif self.data_type == "Fuel_Consumption_BTU":
                fuel_types = ModelForecast.total_consumption_fuels
            else:
                raise ValueError(f"Unexpected EIA Data Type encountered: {self.data_type}")

            self._generate_individual_forecasts(fuel_types, state)
            self._combine_forecasts(fuel_types, state)

    def _generate_individual_forecasts(self, fuel_types: list, state: str):
        """Read in Prophet model, generate predictions and save as CSV."""
        for fuel_type in fuel_types:
            model = self._load_prophet_model(fuel_type)
            forecast = self._predict(model)
            self._save_forecast(forecast, "individual", state, fuel_type)

    def _load_prophet_model(self, fuel_type: str) -> Prophet:
        """Load Prophet model for specific data type, state and fuel type."""
        models_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'json')
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, models_file_name)
        with open(models_file_path, 'r') as fin:
            return model_from_json(json.load(fin))

    @staticmethod
    def _predict(model: Prophet) -> pd.DataFrame:
        """Perform predictions for all time periods including 12 future quarters using Prophet model."""
        future = model.make_future_dataframe(periods=12, freq='Q')
        forecast = model.predict(future)

        # Create column y with historical values for periods in past with future predictions for future periods
        forecast['y'] = model.history['y'].combine_first(forecast['yhat'])
        return forecast

    def _save_forecast(self, forecast: pd.DataFrame, forecast_type: str, state: str, fuel_type: str = None):
        """Save forecast to folder depending on forecast type. """
        target_folder = ""
        file_name = ""
        if forecast_type == 'individual':
            target_folder = 'Individual_Forecasts/{}/{}'.format(self.data_type, state)
            file_name = '{}-{}.csv'.format(self.data_type, fuel_type)
        elif forecast_type == 'combined':
            target_folder = 'Combined_Forecasts/{}'.format(state)
            file_name = '{}-Combined.csv'.format(self.data_type)
        file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
        forecast.to_csv(file_path, index=False)

    def _combine_forecasts(self, fuel_types: list, state: str):
        """For each state and data type, combine individual forecasts into one combined dataframe.
        For Alabama state and Net Elec. Gen data, it will create a CSV with one column for each
        type of generation source (coal, solar, wind, etc.).
        """
        df_combined = pd.DataFrame()
        for fuel in fuel_types:
            forecast = read_forecast(self.data_type, "individual", state, fuel)
            if 'date' not in df_combined.columns:
                df_combined['date'] = forecast['ds']
            df_combined[fuel] = forecast['y']
        self._save_forecast(df_combined, "combined", state)


def combine_all_states_generation():
    """Concatenate and save all state electricity generation CSVs into one"""
    generation_combined = pd.DataFrame()
    for state in STATES:
        df_gen = read_forecast("Net_Gen_By_Fuel_MWh", "combined", state)

        df_gen["state"] = state
        generation_combined = pd.concat([generation_combined, df_gen], ignore_index=True)

    # Save dataframes as CSV
    target_folder = 'Combined_Forecasts'
    file_name = 'Combined-Electricity-Generation-All-States.csv'
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    generation_combined.to_csv(file_path, index=False)


def read_forecast(data_type: str, forecast_type: str, state: str, fuel_type: str = None) -> pd.DataFrame:
    """
    Read forecasts from file for specific forecast type (individual and combined).

    Parameters
    -----------
    data_type: str
        Type of data: one of Net_Gen_By_Fuel_MWh or Fuel_Consumption_BTU
    forecast_type: str
        Type of forecast data to read: one of individual or combined
    state: str
        State of interest
    fuel_type: str
        Type of generation source (coal, wind, etc.)

    Returns
    --------
    pd.DataFrame()
        Forecast dataframe
    """
    target_folder = ""
    file_name = ""
    if forecast_type == 'individual':
        target_folder = 'Individual_Forecasts/{}/{}'.format(data_type, state)
        file_name = '{}-{}.csv'.format(data_type, fuel_type)
    elif forecast_type == 'combined':
        target_folder = 'Combined_Forecasts/{}'.format(state)
        file_name = '{}-Combined.csv'.format(data_type)
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    return pd.read_csv(file_path)
