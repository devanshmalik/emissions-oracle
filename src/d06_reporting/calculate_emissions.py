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

    def calculate_total_emissions(self):
        log.info("Calculating Total Emissions for all states")
        for state in STATES:
            df = self.create_empty_dataframe(state)
            for data_type, emissions_dict in self.emission_factors.items():
                fcst = read_forecast(data_type, 'combined', state)

                # For each fuel, multiply amount created by emissions factor
                for col in fcst.columns:
                    if col in emissions_dict:
                        # Divide Net_Gen_By_Fuel_MWh emissions by 1000 to get
                        # emissions in thousand metrics tons CO2
                        if data_type == 'Net_Gen_By_Fuel_MWh':
                            df[col] += (emissions_dict[col] * fcst[col] / 1e3)
                        else:
                            df[col] += emissions_dict[col] * fcst[col]

            # Sum all columns except first which is date to calculate total emissions
            df["all_fuels"] = df.iloc[:, 1:].sum(axis=1)
            self.save_emissions(df, "total", state)
        log.info("Completed calculating total emissions for all states.")

    def create_empty_dataframe(self, state):
        df = pd.DataFrame()
        fcst = read_forecast("Net_Gen_By_Fuel_MWh", 'combined', state)
        df['date'] = fcst['date']

        # Initialize empty columns for each type of generation source
        for fuel in EmissionsCalculator.net_gen_fuels:
            df[fuel] = 0
        return df

    def calculate_emissions_intensity(self):
        log.info("Calculating Emissions Intensity for all states")
        for state in STATES:
            generation_fcst = read_forecast("Net_Gen_By_Fuel_MWh", 'combined', state)
            emissions_fcst = read_emissions("total", state)

            # Create emissions intensity dataframe
            df = pd.DataFrame()
            df['date'] = generation_fcst['date']
            df['emissions_intensity'] = emissions_fcst["all_fuels"] / generation_fcst["all_fuels"]

            self.save_emissions(df, "intensity", state)
        log.info("Completed calculating emissions intensity for all states.")

    def save_emissions(self, df, emissions_type, state):
        target_folder = ""
        file_name = ""
        if emissions_type == 'total':
            target_folder = 'Emission_Forecasts/Total_Emissions'
            file_name = '{}-CO2e-Emissions.csv'.format(state)
        elif emissions_type == 'intensity':
            target_folder = 'Emission_Forecasts/Emissions_Intensity'
            file_name = '{}-CO2e-Emissions-Intensity.csv'.format(state)
        file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
        df.to_csv(file_path, index=False)

    def combine_state_emissions(self):
        """Concatenate all individual state emissions CSVs into one for
        both Total Emissions and Emissions Intensity"""
        total_emissions_combined = pd.DataFrame()
        emissions_intensity_combined = pd.DataFrame()
        for state in STATES:
            df_total = read_emissions("total", state)
            df_intensity = read_emissions("intensity", state)

            df_total["state"] = state
            df_intensity["state"] = state
            total_emissions_combined = pd.concat([total_emissions_combined, df_total], ignore_index=True)
            emissions_intensity_combined = pd.concat([emissions_intensity_combined, df_intensity], ignore_index=True)

        # Save both dataframes as CSV
        target_folder = 'Emission_Forecasts'
        intensity_file_name = 'Combined-CO2e-Emissions-Intensity.csv'
        total_file_name = 'Combined-CO2e-Total-Emissions.csv'

        file_path_intensity = get_filepath(REPORTING_FOLDER, target_folder, intensity_file_name)
        file_path_total = get_filepath(REPORTING_FOLDER, target_folder, total_file_name)
        emissions_intensity_combined.to_csv(file_path_intensity, index=False)
        total_emissions_combined.to_csv(file_path_total, index=False)


def calculate_emissions(emission_factors):
    log.info("Calculating emissions for all regions...")
    emissions_calculator = EmissionsCalculator(emission_factors=emission_factors)
    emissions_calculator.calculate_total_emissions()
    emissions_calculator.calculate_emissions_intensity()
    emissions_calculator.combine_state_emissions()
    log.info("Finished all emission calculations")


def read_emissions(emissions_type, state):
    target_folder = ""
    file_name = ""
    if emissions_type == 'total':
        target_folder = 'Emission_Forecasts/Total_Emissions'
        file_name = '{}-CO2e-Emissions.csv'.format(state)
    elif emissions_type == 'intensity':
        target_folder = 'Emission_Forecasts/Emissions_Intensity'
        file_name = '{}-CO2e-Emissions-Intensity.csv'.format(state)
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    return pd.read_csv(file_path)
