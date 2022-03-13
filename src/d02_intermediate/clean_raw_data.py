import os
import logging
import pandas as pd
import yaml
import json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class DataCleaner:
    """Class to clean raw data prior to feature engineering"""
    def __init__(self, api_ids_dict, data_type):
        self.api_ids_dict = api_ids_dict
        self.data_type = data_type
        self.save_folder = ""
        self.fuel_type = ""

    @staticmethod
    def is_response_valid(json_data):
        """Checks if the EIA JSON response is valid."""
        if 'data' in json_data and 'error' in json_data['data']:
            log.info(f"Invalid response for EIA Series ID: {json_data['request']['series_id']}"
                     f" with error message: {json_data['data']['error']}")
            return False
        return True

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
        which means there is no data for that attribute for the state specified."""
        start_date = "2001-01-01"
        end_date = "2021-12-31"
        dt_range = pd.date_range(start_date, end_date, freq='Q')
        return pd.DataFrame({'date': dt_range, self.data_type: 0.0})

    def convert_raw_data(self):
        """
        Read raw JSON data and convert to Pandas dataframe including handling invalid responses

        :return:
        """
        raw_file_name = '{}-{}.{}'.format(self.data_type, self.fuel_type, 'json')
        raw_file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, raw_file_name)

        with open(raw_file_path, 'r') as f:
            json_data = json.load(f)
            if self.is_response_valid(json_data):
                return self.create_valid_df(json_data)
            else:
                return self.create_empty_df()

    def impute_missing_data(self, df):
        """
        Performs two imputations on each CSV file in 02_intermediate data folder:
        1) Impute 0 for all rows with missing y value (eg: Net_Gen_By_Fuel_MWh)
        2) For any missing quarters between 2001 and 2021, create a new row for the
        missing date with a y value of zero. This ensures the time-series training
        algorithm has data points for all time periods without any missing periods.

        :param df:
        :return:
        """
        df[self.data_type].fillna(0, inplace=True)

        # Convert to pd.Series prior to imputing missing dates
        pd_series = df.set_index('date')[self.data_type]
        pd_series.index = pd.DatetimeIndex(pd_series.index)

        # Create new index with all possible dates in interval and reindex
        dt_range_idx = pd.date_range("2001-01-01", "2021-12-31", freq='Q')
        pd_series = pd_series.reindex(dt_range_idx, fill_value=0)

        # Create dataframe from pd.Series
        return pd.DataFrame({'date': pd_series.index, self.data_type: pd_series.values})

    def save_intermediate_data(self, df):
        intermediate_file_name = '{}-{}.{}'.format(self.data_type, self.fuel_type, 'csv')
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, intermediate_file_name)
        df.to_csv(intermediate_file_path, index=False)

    def clean_data(self):
        for state in STATES:
            log.info(f"Cleaning raw data for {state}")
            # Folder for each state's data
            self.save_folder = '{}/{}'.format(self.data_type, state)

            for fuel_type, api_id in self.api_ids_dict.items():
                self.fuel_type = fuel_type
                df = self.convert_raw_data()
                df = self.impute_missing_data(df)
                self.save_intermediate_data(df)


def clean_all_data(eia_api_ids):
    for data_type, api_ids_dict in eia_api_ids.items():
        log.info(f"Cleaning raw data for {data_type}")
        data_cleaner = DataCleaner(api_ids_dict=api_ids_dict, data_type=data_type)
        data_cleaner.clean_data()

