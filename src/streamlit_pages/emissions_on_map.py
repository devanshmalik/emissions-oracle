import streamlit as st
import pandas as pd

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_visualization.plot import plot_map

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Set up sidebar options
    emissions_type = st.sidebar.radio("Select the type of emissions data.",
                              options=["Emissions Intensity", "Total Emissions"],
                              help="Add details here")

    # Main Chart Options
    fuel_options = config["data_types"]["Net_Gen_By_Fuel_MWh"]["fuels"]
    turn_off_widget = emissions_type == "Emissions Intensity"
    col1, col2 = st.columns([4, 1])
    chosen_year = col1.slider(
        "Pick a year in time",
        value=2021,
        min_value=2001,
        max_value=2025,
    )
    chosen_fuel = col2.selectbox("Pick a fuel type",
                                 options=fuel_options, help="Only available for Total Emissions",
                                 disabled=turn_off_widget)

    # Get Data and Plot Chart
    if emissions_type == "Emissions Intensity":
        file_name = 'Combined-CO2e-Emissions-Intensity.csv'
        df = get_emissions_data(file_name)

        # Aggregate by state and time unit (mean aggregation for emissions intensity)
        df = df.groupby([pd.Grouper(key='date', freq="Y"), 'state']).mean().reset_index()
        fig = plot_map(df[df['date'].dt.year == chosen_year], "emissions_intensity")
    else:
        file_name = 'Combined-CO2e-Total-Emissions.csv'
        df = get_emissions_data(file_name)

        # Aggregate by state and time unit (sum aggregation for total emissions)
        df = df.groupby([pd.Grouper(key='date', freq="Y"), 'state']).sum().reset_index()
        fig = plot_map(df[df['date'].dt.year == chosen_year], chosen_fuel)
    st.plotly_chart(fig)


def get_emissions_data(file_name):
    target_folder = 'Emission_Forecasts'
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df

