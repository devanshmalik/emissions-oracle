import yaml
import os 
import requests
import json
import logging
import pandas as pd

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class EIADataPull:
    """Class to pull relevant electricity generation data from EIA API"""
    def __init__(self, save_folder, file_name):
        self.save_folder = save_folder
        self.file_name = file_name

    def request_data(self, api_series_id, state):
        custom_series_id = api_series_id.format(state)
        return requests.get(
            EIA_URL.format(custom_series_id, os.environ.get("EIA_ACCESS_KEY"))
        )

    def save_data(self, response, file_name):
        file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)

    # TODO: Add error handling for failed requests
    def create_intermediate_data(self, state):
        raw_file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, self.file_name)
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, self.file_name)

        with open(raw_file_path.format(state, 'json'), 'r') as f:
            json_data = json.load(f)
            df = pd.DataFrame(json_data['series'][0]['data'])
            df.columns = ["date", "net_generation"]

            # Convert year_quarter (2021Q3) into date ('2021-09-30') format
            qs = df['date'].str.replace(r'(\d+)(Q\d)', r'\1-\2', regex=True)
            df['date'] = pd.PeriodIndex(qs, freq='Q').to_timestamp()
            df['date'] = df['date'] + pd.offsets.QuarterEnd(0)

            df.to_csv(intermediate_file_path.format(state, 'csv'), index=False)


def load_data(data_type, api_ids_dict):
    for state in STATES:
        save_folder = '{}/{}'.format(data_type, state)
        eia_data_pull = EIADataPull(save_folder=save_folder, file_name='blah')

        for fuel_type, api_id in api_ids_dict.items():
            file_name = '{}-{}.json'.format(data_type, fuel_type)
            response = eia_data_pull.request_data(api_id, state)
            eia_data_pull.save_data(response, file_name)


def load_all_data(eia_api_ids):
    for data_type, api_ids_dict in eia_api_ids.items():
        load_data(data_type, api_ids_dict)

