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
    def __init__(self, api_ids_dict, data_type):
        self.api_ids_dict = api_ids_dict
        self.data_type = data_type
        self.save_folder = ""

    def process_data(self):
        for state in STATES:
            self.save_folder = '{}/{}'.format(self.data_type, state)

            for fuel_type, api_id in self.api_ids_dict.items():
                self.create_features(fuel_type)

    def create_features(self, fuel_type):
        """
        Performs two imputations on each CSV file in 02_intermediate data folder:
        1) Impute 0 for all rows with missing y value (eg: Net_Gen_By_Fuel_MWh)
        2) For any missing quarters between 2001 and 2021, create a new row for the
        missing date with a y value of zero. This ensures the time-series training
        algorithm has data points for all time periods without any missing periods.

        :param fuel_type:
        :return:
        """
        intermediate_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        processed_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, intermediate_file_name)
        processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, processed_file_name)

        df = pd.read_csv(intermediate_file_path)
        # Do feature engineering here to create model training data
        df.to_csv(processed_file_path, index=False)


def process_all_data(eia_api_ids):
    for data_type, api_ids_dict in eia_api_ids.items():
        data_process = DataPreprocessor(api_ids_dict=api_ids_dict, data_type=data_type)
        data_process.process_data()


    # def create_prophet_data_old(self):
    #     intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, self.file_name)
    #     processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, self.file_name)
    #
    #     for state in self.states:
    #         df = pd.read_csv(intermediate_file_path.format(state, 'csv'))
    #         df['date'] = pd.to_datetime(df['date'])
    #         df.columns = ['ds', 'y']
    #
    #         df.to_csv(processed_file_path.format(state, 'csv'), index=False)
