import os
import logging
import pandas as pd
import yaml

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class DataPreprocessor:
    """Class to preprocess intermediate data prior to training models"""
    def __init__(self, save_folder, file_name):
        self.save_folder = save_folder
        self.file_name = file_name
        self.states = STATES

    def create_prophet_data(self):
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, self.file_name)
        processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, self.file_name)

        for state in self.states:
            df = pd.read_csv(intermediate_file_path.format(state, 'csv'))
            df['date'] = pd.to_datetime(df['date'])
            df.columns = ['ds', 'y']

            df.to_csv(processed_file_path.format(state, 'csv'), index=False)


def process_data():
    save_folder = 'Net_Gen_By_State'
    file_name = 'net_generation_{}.{}'

    log.info("Creating Processed Data for model inputs...")
    data_process = DataPreprocessor(save_folder=save_folder, file_name=file_name)
    data_process.create_prophet_data()
    log.info("Finished creating processed data.")
