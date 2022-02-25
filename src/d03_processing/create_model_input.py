import os
import logging
import pandas as pd
import yaml

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

YML_FILE_PATH = os.path.join(os.getcwd(), '../conf/base/', 'states.yml')
INTERMEDIATE_DATA_FOLDER = os.path.join(os.getcwd(), '../data/02_intermediate/')
PROCESSED_DATA_FOLDER = os.path.join(os.getcwd(), '../data/03_processed/')


class DataPreprocessor:
    """Class to preprocess intermediate data prior to training models"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.states = self.get_states_yml()

    @staticmethod
    def get_states_yml():
        states_yaml = open(YML_FILE_PATH)
        return yaml.load(states_yaml, Loader=yaml.FullLoader)

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
