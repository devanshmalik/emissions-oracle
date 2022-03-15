import requests
import json
import logging
from typing import Union, Dict, List, Type

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

from typing import Union, Dict, List, Type
TypeJSON = Union[Dict[str, 'JSON'], List['JSON'], int, str, float, bool, Type[None]]
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class EIADataPull:
    """Class to pull relevant electricity generation data from EIA API"""
    def __init__(self, data_type: str, api_ids_dict: dict):
        """

        Parameters
        ------------
        data_type: str
            Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
            This string is used when creating folders to save respective data and for column names within each dataframe
        api_ids_dict: dict
            Dictionary of API IDs where key is a string descriptor of type of data and
            value is the EIA API Series ID to access the specific data.
            For data_type `Net_Gen_By_Fuel_MWh`, examples of api_ids_dict key values include fuel names (coal, natural_gas, etc.)
        """
        self.api_ids_dict = api_ids_dict
        self.data_type = data_type
        self.save_folder = ""

    def load_data(self):
        """Loads and saves response data from EIA API for each state and each type of generation."""
        states = load_yml(STATES_YML_FILEPATH)
        for state_name, state_code in states.items():
            log.info(f"Loading raw data for {state_name}")
            self.save_folder = '{}/{}'.format(self.data_type, state_name)

            for fuel_type, api_id in self.api_ids_dict.items():
                # Pull and save JSON raw data using EIA API
                file_name = '{}-{}.json'.format(self.data_type, fuel_type)
                response = self._request_data(api_id, state_code)
                self._save_data(response, file_name)

    @staticmethod
    def _request_data(api_series_id: str, state: str) -> TypeJSON:
        """Perform REST get request from EIA API for specific data."""
        custom_series_id = api_series_id.format(state)
        return requests.get(
            EIA_API_URL.format(custom_series_id, os.environ.get("EIA_ACCESS_KEY"))
        )

    def _save_data(self, response, file_name):
        """Save get request response as JSON file."""
        file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)


