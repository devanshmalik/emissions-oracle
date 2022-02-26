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
    def __init__(self, series_id, save_folder, file_name):
        self.series_id = series_id
        self.save_folder = save_folder
        self.file_name = file_name
        self.states = STATES
        self.responses = []

    # TODO: Add error handling for failed requests
    def request_data(self):
        for state in self.states:
            custom_series_id = self.series_id.format(state)
            response = requests.get(EIA_URL.format(custom_series_id, os.environ.get("EIA_ACCESS_KEY")))
            self.responses.append(response)
        return self.responses

    def save_data(self):
        file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, self.file_name)
        for idx, state in enumerate(self.states):
            with open(file_path.format(state, 'json'), 'w', encoding='utf-8') as f:
                json.dump(self.responses[idx].json(), f, ensure_ascii=False, indent=4)
        return

    def create_intermediate_data(self):
        raw_file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, self.file_name)
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, self.file_name)

        for state in self.states:
            with open(raw_file_path.format(state, 'json'), 'r') as f:
                json_data = json.load(f)
                df = pd.DataFrame(json_data['series'][0]['data'])
                df.columns = ["date", "net_generation"]

                # Convert year_quarter (2021Q3) into date ('2021-09-30') format
                qs = df['date'].str.replace(r'(\d+)(Q\d)', r'\1-\2', regex=True)
                df['date'] = pd.PeriodIndex(qs, freq='Q').to_timestamp()
                df['date'] = df['date'] + pd.offsets.QuarterEnd(0)

                df.to_csv(intermediate_file_path.format(state, 'csv'), index=False)


def load_data():
    net_gen_id = 'ELEC.GEN.ALL-{}-99.Q'
    save_folder = 'Net_Gen_By_State'
    file_name = 'net_generation_{}.{}'

    log.info("Starting Raw Data Pull using EIA API...")
    eia_data_pull = EIADataPull(series_id=net_gen_id, save_folder=save_folder, file_name=file_name)
    eia_data_pull.request_data()
    eia_data_pull.save_data()
    log.info("Finished Raw Data Pull as JSON files.")

    log.info("Creating Intermediate Data...")
    eia_data_pull.create_intermediate_data()
    log.info("Finished Creating Intermediate Data CSVs.")

