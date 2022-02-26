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
    def __init__(self, save_folder, file_name):
        self.save_folder = save_folder
        self.file_name = file_name
        self.states = STATES

    def forecast(self):
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, self.file_name)
        reporting_file_path = get_filepath(REPORTING_FOLDER, self.save_folder, self.file_name)

        for state in self.states:
            # Load Model
            with open(models_file_path.format(state, 'json'), 'r') as fin:
                model = model_from_json(json.load(fin))

                # Makes a dataframe with both historical dates and
                # append future dates for number of periods specified
                future = model.make_future_dataframe(periods=16, freq='Q')
                forecast = model.predict(future)

                # Saving to CSV loses the datetime format causing errors when plotting
                forecast.to_csv(reporting_file_path.format(state, 'csv'), index=False)


def create_forecasts():
    save_folder = 'Net_Gen_By_State'
    file_name = 'net_generation_{}.{}'

    log.info("Creating forecasts using trained Prophet models...")
    data_process = ModelForecast(save_folder=save_folder, file_name=file_name)
    data_process.forecast()
    log.info("Finished creating and saving forecasts.")


# Non-interactive plots
# fig1 = m.plot(forecast)
# fig2 = m.plot_components(forecast)

# Interative Plots
# from prophet.plot import plot_plotly, plot_components_plotly
# plot_plotly(m, forecast)
# plot_components_plotly(m, forecast)
