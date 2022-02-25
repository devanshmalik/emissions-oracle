import os
import logging
import pandas as pd
import yaml

from src.d00_utils.const import *


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class DataPreprocessor:
    """Class to preprocess intermediate data prior to training models"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.states = STATES

    def create_prophet_data(self):
        intermediate_file_path = os.path.join(INTERMEDIATE_DATA_FOLDER, self.file_path)
        processed_file_path = os.path.join(PROCESSED_DATA_FOLDER, self.file_path)

        for state in self.states:
            df = pd.read_csv(intermediate_file_path.format(state, 'csv'))
            df['date'] = pd.to_datetime(df['date'])
            df.columns = ['ds', 'y']

            df.to_csv(processed_file_path.format(state, 'csv'), index=False)


def process_data():
    file_path = 'Net_Gen_By_State/net_generation_{}.{}'

    log.info("Creating Processed Data for model inputs...")
    data_process = DataPreprocessor(file_path=file_path)
    data_process.create_prophet_data()
    log.info("Finished creating processed data.")
