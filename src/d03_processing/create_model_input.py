import logging
import pandas as pd

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class DataPreprocessor:
    """Class to preprocess intermediate data prior to training models"""
    def __init__(self, data_type, api_ids_dict):
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

    def process_data(self):
        """
        Process each type of data (net generation and fuel consumption) and perform
        required feature engineering to finalize datasets as input to training models.
        """
        for state in STATES:
            log.info(f"Processing intermediate data for {state}")
            self.save_folder = '{}/{}'.format(self.data_type, state)

            if self.data_type == 'Net_Gen_By_Fuel_MWh':
                self._process_net_gen_data()
            elif self.data_type == "Fuel_Consumption_BTU":
                self._process_fuel_cons_data()
            else:
                raise ValueError(f"Unexpected EIA Data Type encountered: {self.data_type}")

    def _process_net_gen_data(self):
        """Performs feature engineering and saving for all Net Electricity Generation sources"""
        # No processing needed for most fuels
        no_processing_fuels = ['all_sources', 'coal', 'natural_gas', 'nuclear',
                               'hydro', 'wind', 'solar_all']
        for fuel_type in no_processing_fuels:
            df = self._read_input_data(fuel_type)
            self._save_feature(df, fuel_type)

        # Compute feature for "Other" generation
        # Note: The calculated version is different from the "Other" imported from EIA directly
        df_other_rw = self._read_input_data("other_renewables")
        df_wind = self._read_input_data("wind")
        df_solar_utility = self._read_input_data("solar_utility")
        df_eia_other = self._read_input_data("other")

        # Calculate 'Other' gen
        df_other = pd.DataFrame()
        df_other['date'] = df_other_rw['date']
        df_other[self.data_type] = df_other_rw[self.data_type] - df_wind[self.data_type] \
                                   - df_solar_utility[self.data_type] + df_eia_other[self.data_type]
        self._save_feature(df_other, "other")

    def _process_fuel_cons_data(self):
        """Performs feature engineering and saving for all Fuel Consumption types (coal, natural gas)."""
        for fuel_type in self.api_ids_dict.keys():
            df = self._read_input_data(fuel_type)
            self._save_feature(df, fuel_type)

    def _read_input_data(self, fuel_type):
        """Reads data from intermediate folder for specific fuel type."""
        intermediate_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        intermediate_file_path = get_filepath(INTERMEDIATE_DATA_FOLDER, self.save_folder, intermediate_file_name)
        return pd.read_csv(intermediate_file_path)

    def _save_feature(self, df, fuel_type):
        """Saves the final engineered feature ready for model training in Processed Data folder."""
        processed_file_name = '{}-{}.{}'.format(self.data_type, fuel_type, 'csv')
        processed_file_path = get_filepath(PROCESSED_DATA_FOLDER, self.save_folder, processed_file_name)

        # Prophet expects column names to be 'ds' and 'y'
        df.columns = ['ds', 'y']
        df.to_csv(processed_file_path, index=False)

