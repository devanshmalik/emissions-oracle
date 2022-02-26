import os
import logging
import pandas as pd
import yaml
from prophet import Prophet
import json
from prophet.serialize import model_to_json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ProphetModel:
    """Class to train Facebook Prophet models"""
    def __init__(self, save_folder, file_name):
        self.save_folder = save_folder
        self.file_name = file_name
        self.states = STATES

    def train(self):
        processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, self.file_name)
        models_file_path = get_filepath(MODELS_FOLDER, self.save_folder, self.file_name)

        for state in self.states:
            df = pd.read_csv(processed_file_path.format(state, 'csv'))
            model = Prophet()
            model.fit(df)

            # Save Model
            with open(models_file_path.format(state, 'json'), 'w') as fout:
                json.dump(model_to_json(model), fout)


def train_models():
    save_folder = 'Net_Gen_By_State'
    file_name = 'net_generation_{}.{}'

    log.info("Training and Saving Prophet Models...")
    data_process = ProphetModel(save_folder=save_folder, file_name=file_name)
    data_process.train()
    log.info("Finished training Prophet models.")


