import logging
import pandas as pd

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath
from src.d06_reporting.create_forecasts import read_forecast


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class EmissionsCalculator:
    """Class to create forecasts based on models trained earlier"""
    # TODO: Pull directly from config instead of hard coding in script
    net_gen_fuels = ['coal', 'natural_gas', 'nuclear',
                     'hydro', 'wind', 'solar_all', 'other']
    """Class to calculate emissions for all regions."""
    def __init__(self, emission_factors):
        self.emission_factors = emission_factors
        self.save_folder = ""

    def calculate_emissions(self):
        for state in STATES:
            log.info(f"Calculating Emissions for State: {state}")
            df = self.create_empty_dataframe(state)
            for data_type, emissions_dict in self.emission_factors.items():
                fcst = read_forecast(data_type, 'combined', state)

                # For each fuel, multiply amount created by emissions factor
                for col in fcst.columns:
                    if col in emissions_dict:
                        df[col] += emissions_dict[col] * fcst[col]

            # Sum all columns except first which is date to calculate total emissions
            df["all_fuels"] = df.iloc[:, 1:].sum(axis=1)
            self.save_emissions(df, state)
            log.info(f"Completed calculating emissions for State: {state}")

    def create_empty_dataframe(self, state):
        df = pd.DataFrame()
        fcst = read_forecast("Net_Gen_By_Fuel_MWh", 'combined', state)
        df['date'] = fcst['date']

        # Initialize empty columns for each type of generation source
        for fuel in EmissionsCalculator.net_gen_fuels:
            df[fuel] = 0
        return df

    def save_emissions(self, df, state):
        # Create new parent folder for all emission forecasts
        reporting_folder = 'Emission_Forecasts'
        reporting_file_name = '{}-CO2e-Emissions.csv'.format(state)
        reporting_file_path = get_filepath(REPORTING_FOLDER, reporting_folder, reporting_file_name)

        # Saving to CSV loses the datetime format causing errors when plotting
        df.to_csv(reporting_file_path, index=False)


def calculate_emissions(emission_factors):
    log.info("Calculating emissions for all regions...")
    emissions_calculator = EmissionsCalculator(emission_factors=emission_factors)
    emissions_calculator.calculate_emissions()
    log.info("Finished all emission calculations")


def read_emissions(state):
    reporting_folder = 'Emission_Forecasts'
    reporting_file_name = '{}-CO2e-Emissions.csv'.format(state)
    reporting_file_path = get_filepath(REPORTING_FOLDER, reporting_folder, reporting_file_name)

    return pd.read_csv(reporting_file_path)