import os
import logging
import pandas as pd
import yaml
from prophet import Prophet
import json
from prophet.serialize import model_from_json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ModelForecast:
    """Class to create forecasts based on models trained earlier"""
    net_gen_fuels = ['all_fuels', 'coal', 'natural_gas', 'nuclear',
                     'hydro', 'wind', 'solar_all', 'other']
    total_consumption_fuels = ['coal', 'natural_gas']
    """Class to train Facebook Prophet models"""
    def __init__(self, data_type):
        self.data_type = data_type
        self.save_folder = ""

    def forecast(self):
        for state in STATES:
            log.info(f"Forecasting for State: {state}")
            self.save_folder = '{}/{}'.format(self.data_type, state)

            if self.data_type == 'Net_Gen_By_Fuel_MWh':
                fuel_types = ModelForecast.net_gen_fuels
            elif self.data_type == "Fuel_Consumption_BTU":
                fuel_types = ModelForecast.total_consumption_fuels
            else:
                raise ValueError(f"Unexpected EIA Data Type encountered: {self.data_type}")

            self.generate_individual_forecasts(fuel_types, state)
            self.combine_forecasts(fuel_types, state)
            log.info(f"Completed forecasting for State: {state}")

    def generate_individual_forecasts(self, fuel_types, state):
        for fuel_type in fuel_types:
            model = self.read_prophet_model(fuel_type)
            forecast = self.predict(model)
            self.save_individual_forecast(forecast, fuel_type)
        log.info(f"Finished individual forecasting for {self.data_type}")

    def read_prophet_model(self, fuel_type):
        models_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'json')
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, models_file_name)
        with open(models_file_path, 'r') as fin:
            return model_from_json(json.load(fin))

    @staticmethod
    def predict(model):
        future = model.make_future_dataframe(periods=16, freq='Q')
        forecast = model.predict(future)

        # Create column y with historical values for periods in past with future predictions for future periods
        forecast['y'] = model.history['y'].combine_first(forecast['yhat'])
        return forecast

    def save_individual_forecast(self, forecast, fuel_type):
        # Create new parent folder for all individual forecasts
        reporting_folder = 'Individual_Forecasts/{}'.format(self.save_folder)
        reporting_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        reporting_file_path = get_filepath(REPORTING_FOLDER, reporting_folder, reporting_file_name)

        # Saving to CSV loses the datetime format causing errors when plotting
        forecast.to_csv(reporting_file_path, index=False)

    def combine_forecasts(self, fuel_types, state):
        log.info(f"Combining individual forecasts for {self.data_type}")
        df_combined = pd.DataFrame()
        # TODO: Do not add all_fuels to dataframe
        for fuel in fuel_types:
            forecast = self.read_forecast(fuel)
            if 'date' not in df_combined.columns:
                df_combined['date'] = forecast['ds']
            df_combined[fuel] = forecast['y']
        self.save_combined_forecast(df_combined, state)

    def read_forecast(self, fuel_type):
        # Create new parent folder for all individual forecasts
        reporting_folder = 'Individual_Forecasts/{}'.format(self.save_folder)
        reporting_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        reporting_file_path = get_filepath(REPORTING_FOLDER, reporting_folder, reporting_file_name)

        return pd.read_csv(reporting_file_path)

    def save_combined_forecast(self, df_combined, state):
        # Create new parent folder for all combined forecasts
        reporting_folder = 'Combined_Forecasts/{}'.format(state)
        reporting_file_name = '{}-Combined.{}'.format(self.data_type, 'csv')
        reporting_file_path = get_filepath(REPORTING_FOLDER, reporting_folder, reporting_file_name)

        # Saving to CSV loses the datetime format causing errors when plotting
        df_combined.to_csv(reporting_file_path, index=False)


def create_all_forecasts(eia_api_ids):
    log.info("Creating forecasts for all Prophet Models...")
    for data_type in eia_api_ids.keys():
        model_forecaster = ModelForecast(data_type=data_type)
        model_forecaster.forecast()
    log.info("Finished all forecasting")


def read_forecast(data_type, forecast_type, state, fuel_type=None):
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




# Non-interactive plots
# fig1 = m.plot(forecast)
# fig2 = m.plot_components(forecast)

# Interative Plots
# from prophet.plot import plot_plotly, plot_components_plotly
# plot_plotly(m, forecast)
# plot_components_plotly(m, forecast)
