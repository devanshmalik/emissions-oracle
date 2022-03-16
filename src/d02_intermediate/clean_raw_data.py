# Python Libraries
import json
import logging

# Package Imports
import pandas as pd

# First Party Imports
from src.d00_utils.const import INTERMEDIATE_DATA_FOLDER, RAW_DATA_FOLDER, STATES
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class DataCleaner:
    """Class to clean raw data prior to feature engineering."""

    def __init__(self, data_type: str, api_ids_dict: dict):
        """

        Parameters
        ------------
        data_type: str
            Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
            This string is used when creating folders to save respective data
            and for column names within each dataframe
        api_ids_dict: dict
            Dictionary of API IDs where key is a string descriptor of type of data and
            value is the EIA API Series ID to access the specific data.
            For data_type `Net_Gen_By_Fuel_MWh`, examples of api_ids_dict
            key values include fuel names (coal, natural_gas, etc.)
        """
        self.api_ids_dict = api_ids_dict
        self.data_type = data_type
        self.save_folder = ""
        self.fuel_type = ""

    def clean_data(self):
        """Clean and save raw data in two steps for each state and each data type:
        1) Convert raw data from JSON to CSV format (for failed API requests, create empty CSV)
        2) Impute missing data for time periods with no entry (implies no generation in that period)
        """
        for state in STATES:
            log.info(f"Cleaning raw data for {state}")
            # Folder for each state's data
            self.save_folder = "{}/{}".format(self.data_type, state)

            for fuel_type, api_id in self.api_ids_dict.items():
                self.fuel_type = fuel_type
                df = self._convert_raw_data()
                df = self._impute_missing_data(df)
                self._save_intermediate_data(df)

    def _convert_raw_data(self) -> pd.DataFrame:
        """Read raw JSON data and convert to dataframe including handling invalid responses"""
        raw_file_name = "{}-{}.{}".format(self.data_type, self.fuel_type, "json")
        raw_file_path = get_filepath(RAW_DATA_FOLDER, self.save_folder, raw_file_name)

        with open(raw_file_path, "r") as f:
            json_data = json.load(f)
            if self._is_response_valid(json_data):
                return self._create_valid_df(json_data)
            else:
                return self._create_empty_df()

    @staticmethod
    def _is_response_valid(json_data) -> bool:
        """Checks if the EIA JSON response is valid."""
        if "data" in json_data and "error" in json_data["data"]:
            log.info(
                f"Invalid response for EIA Series ID: {json_data['request']['series_id']}"
                f" with error message: {json_data['data']['error']}"
            )
            return False
        return True

    def _create_valid_df(self, json_data) -> pd.DataFrame:
        """Creates a dataframe from JSON response and converts quarter string to datetime format"""
        df = pd.DataFrame(json_data["series"][0]["data"])
        df.columns = ["date", self.data_type]

        # Convert year_quarter (2021Q3) into date ('2021-09-30') format
        qs = df["date"].str.replace(r"(\d+)(Q\d)", r"\1-\2", regex=True)
        df["date"] = pd.PeriodIndex(qs, freq="Q").to_timestamp()
        df["date"] = df["date"] + pd.offsets.QuarterEnd(0)
        return df

    def _create_empty_df(self) -> pd.DataFrame:
        """Creates an empty df when the JSON response from EIA is invalid
        which means there is no data for that attribute for the state specified."""
        start_date = "2001-01-01"
        end_date = "2021-12-31"
        dt_range = pd.date_range(start_date, end_date, freq="Q")
        return pd.DataFrame({"date": dt_range, self.data_type: 0.0})

    def _impute_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs two imputations on each CSV file in 02_intermediate data folder:
        1) Impute 0 for all rows with missing y value (eg: Net_Gen_By_Fuel_MWh)
        2) For any missing quarters between 2001 and 2021, create a new row for the
        missing date with a y value of zero. This ensures the time-series training
        algorithm has data points for all time periods without any missing periods.
        """
        df[self.data_type].fillna(0, inplace=True)

        # Convert to pd.Series prior to imputing missing dates
        pd_series = df.set_index("date")[self.data_type]
        pd_series.index = pd.DatetimeIndex(pd_series.index)

        # Create new index with all possible dates in interval and reindex
        dt_range_idx = pd.date_range("2001-01-01", "2021-12-31", freq="Q")
        pd_series = pd_series.reindex(dt_range_idx, fill_value=0)

        # Create dataframe from pd.Series
        return pd.DataFrame({"date": pd_series.index, self.data_type: pd_series.values})

    def _save_intermediate_data(self, df: pd.DataFrame):
        """Save cleaned raw data in intermediate data folder."""
        intermediate_file_name = "{}-{}.{}".format(self.data_type, self.fuel_type, "csv")
        intermediate_file_path = get_filepath(
            INTERMEDIATE_DATA_FOLDER, self.save_folder, intermediate_file_name
        )
        df.to_csv(intermediate_file_path, index=False)
