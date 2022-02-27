import requests
import json
import logging
import pandas as pd

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def is_response_valid(json_data):
    """Checks if the EIA JSON response is valid."""
    if 'data' in json_data and 'error' in json_data['data']:
        log.info(f"Invalid response for EIA Series ID: {json_data['request']['series_id']}"
                 f" with error message: {json_data['data']['error']}")
        return False
    return True


class EIADataPull:
    """Class to pull relevant electricity generation data from EIA API"""
    def __init__(self, data_type: str, api_ids_dict: dict):
        """
        :param data_type:
            Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
            This string is used when creating folders to save respective data
            and for column names within each dataframe
        :param api_ids_dict:
            Dictionary of API IDs where key is a string descriptor of type of data and
            value is the EIA API Series ID to access the specific data.
            For data_type `Net_Gen_By_Fuel_MWh`, examples of api_ids_dict key values include
            fuel names (coal, natural_gas, etc.)
        :param save_folder:
            Folder path to store data for each data_type and state. This folder path is updated
            for each unique state.
            Example: `Net_Gen_By_Fuel_MWh/AL` to store data for given type and Alabama state
        """
        self.api_ids_dict = api_ids_dict
        self.data_type = data_type
        self.save_folder = ""

    @staticmethod
    def request_data(api_series_id, state):
        custom_series_id = api_series_id.format(state)
        return requests.get(
            EIA_URL.format(custom_series_id, os.environ.get("EIA_ACCESS_KEY"))
        )

    def save_data(self, response, file_name):
        file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)

    # TODO: Handle nulls and missing dates
    def create_intermediate_data(self, fuel_type):
        """
        Save raw data as CSVs including handling of invalid API responses.

        :param fuel_type:
        :return:
        """
        raw_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'json')
        intermediate_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        raw_file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, raw_file_name)
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, intermediate_file_name)

        with open(raw_file_path, 'r') as f:
            json_data = json.load(f)
            
            if is_response_valid(json_data):          
                df = self.create_valid_df(json_data)
            else: 
                df = self.create_empty_df()
            df.to_csv(intermediate_file_path, index=False)

    def create_valid_df(self, json_data):
        """Creates a dataframe from JSON response and converts quarter string to
        datetime format"""
        df = pd.DataFrame(json_data['series'][0]['data'])
        df.columns = ["date", self.data_type]

        # Convert year_quarter (2021Q3) into date ('2021-09-30') format
        qs = df['date'].str.replace(r'(\d+)(Q\d)', r'\1-\2', regex=True)
        df['date'] = pd.PeriodIndex(qs, freq='Q').to_timestamp()
        df['date'] = df['date'] + pd.offsets.QuarterEnd(0)
        return df

    def create_empty_df(self):
        """Creates an empty df when the JSON response from EIA is invalid
        which means there is no data for that attritute for the state specified."""
        start_date = "2001-01-01"
        end_date = "2021-12-31"
        dt_range = pd.date_range(start_date, end_date, freq='Q')
        return pd.DataFrame({'date': dt_range, self.data_type: 0})

    def load_data(self):
        for state in STATES:
            self.save_folder = '{}/{}'.format(self.data_type, state)

            for fuel_type, api_id in self.api_ids_dict.items():
                # Pull and save JSON raw data using EIA API
                file_name = '{}-{}.json'.format(self.data_type, fuel_type)
                response = self.request_data(api_id, state)
                self.save_data(response, file_name)

                self.create_intermediate_data(fuel_type)


def load_all_data(eia_api_ids):
    for data_type, api_ids_dict in eia_api_ids.items():
        eia_data_pull = EIADataPull(api_ids_dict=api_ids_dict, data_type=data_type)
        eia_data_pull.load_data()

