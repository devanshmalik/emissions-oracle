import yaml
import os 
import requests
import json
import logging

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


EIA_URL = "https://api.eia.gov/series/?series_id={}&api_key={}&out=json"
# DATA_FOLDER = os.path.join(os.getcwd(), '../../data/01_raw/')
# YML_FILE_PATH = os.path.join(os.getcwd(), '../../conf/base/', 'states.yml')

# Only for jupyter notebook testing
YML_FILE_PATH = os.path.join(os.getcwd(), '../conf/base/', 'states.yml')
DATA_FOLDER = os.path.join(os.getcwd(), '../data/01_raw/')


class EIADataPull:
    """Class to pull relevant electricity generation data from EIA API"""
    def __init__(self, series_id, file_path):
        self.series_id = series_id
        self.file_path = file_path
        self.states = self.get_states_yml()
        self.responses = []

    @staticmethod
    def get_states_yml():
        states_yaml = open(YML_FILE_PATH)
        return yaml.load(states_yaml, Loader=yaml.FullLoader)

    # TODO: Add error handling for failed requests
    def request_data(self):
        for state in self.states:
            custom_series_id = self.series_id.format(state)
            response = requests.get(EIA_URL.format(custom_series_id, os.environ.get("EIA_ACCESS_KEY")))
            self.responses.append(response)
        return self.responses

    def save_data(self):
        file_path = os.path.join(DATA_FOLDER, self.file_path)

        for idx, state in enumerate(self.states):
            with open(file_path.format(state), 'w', encoding='utf-8') as f:
                json.dump(self.responses[idx].json(), f, ensure_ascii=False, indent=4)
        return

    def pull_data(self):
        self.request_data()
        self.save_data()


def get_raw_data():
    log.info("Starting Raw Data Pull using EIA API...")
    net_gen_ID = 'ELEC.GEN.ALL-{}-99.Q'
    file_save_path = 'Net_Gen_By_State/net_generation_{}.json'
    eia_data_pull = EIADataPull(series_id=net_gen_ID, file_path=file_save_path)
    eia_data_pull.pull_data()
    log.info("Finished Raw Data Pull.")
