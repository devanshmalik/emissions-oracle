import os
import logging
import pandas as pd
import yaml
from prophet import Prophet
import json
from prophet.serialize import model_from_json

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

YML_FILE_PATH = os.path.join(os.getcwd(), '../conf/base/', 'states.yml')
MODELS_FOLDER = os.path.join(os.getcwd(), '../data/04_models/')
REPORTING_FOLDER = os.path.join(os.getcwd(), '../data/06_reporting/')


class ModelForecast:
    """Class to create forecasts based on models trained earlier"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.states = self.get_states_yml()

    @staticmethod
    def get_states_yml():
        states_yaml = open(YML_FILE_PATH)
        return yaml.load(states_yaml, Loader=yaml.FullLoader)

    def forecast(self):
        models_file_path = os.path.join(MODELS_FOLDER, self.file_path)
        reporting_file_path = os.path.join(REPORTING_FOLDER, self.file_path)

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
    file_path = 'Net_Gen_By_State/net_generation_{}.{}'

    log.info("Creating forecasts using trained Prophet models...")
    data_process = ModelForecast(file_path=file_path)
    data_process.forecast()
    log.info("Finished creating and saving forecasts.")


# Non-interactive plots
# fig1 = m.plot(forecast)
# fig2 = m.plot_components(forecast)

# Interative Plots
# from prophet.plot import plot_plotly, plot_components_plotly
# plot_plotly(m, forecast)
# plot_components_plotly(m, forecast)
