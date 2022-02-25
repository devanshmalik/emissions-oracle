import os
import logging
import pandas as pd
import yaml
from prophet import Prophet
import json
from prophet.serialize import model_to_json

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

YML_FILE_PATH = os.path.join(os.getcwd(), '../conf/base/', 'states.yml')
PROCESSED_DATA_FOLDER = os.path.join(os.getcwd(), '../data/03_processed/')
MODELS_FOLDER = os.path.join(os.getcwd(), '../data/04_models/')


class ProphetModel:
    """Class to train Facebook Prophet models"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.states = self.get_states_yml()

    @staticmethod
    def get_states_yml():
        states_yaml = open(YML_FILE_PATH)
        return yaml.load(states_yaml, Loader=yaml.FullLoader)

    def train(self):
        processed_file_path = os.path.join(PROCESSED_DATA_FOLDER, self.file_path)
        models_file_path = os.path.join(MODELS_FOLDER, self.file_path)

        for state in self.states:
            df = pd.read_csv(processed_file_path.format(state, 'csv'))
            model = Prophet()
            model.fit(df)

            # Save Model
            with open(models_file_path.format(state, 'json'), 'w') as fout:
                json.dump(model_to_json(model), fout)


def train_models():
    file_path = 'Net_Gen_By_State/net_generation_{}.{}'

    log.info("Training and Saving Prophet Models...")
    data_process = ProphetModel(file_path=file_path)
    data_process.train()
    log.info("Finished training Prophet models.")


