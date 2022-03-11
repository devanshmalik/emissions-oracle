import pandas as pd
import streamlit as st

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_reporting.calculate_emissions import read_emissions
from src.d06_visualization.plot import (
    plot_prophet_forecast,
    plot_multiple_fuels,
    plot_combined_data_multiple_fuels,
    plot_multiple_states,
    plot_combined_data_multiple_states,
)

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Set up sidebar options
    st.sidebar.title("1. Filters")
    chosen_data_type = st.sidebar.radio(
        "Select the type of data to analyze.",
        options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
        help="Add details here."
    )
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    time_units_mapping = {"Quarter": "Q", "Year": "Y"}
    chosen_time_unit = st.sidebar.radio(
        "Select the time unit to view data by.",
        options=["Quarter", "Year"],
        help="Suggest a time frame depending on model (probably quarterly)"
    )
    time_unit = time_units_mapping[chosen_time_unit]

    chosen_states_multi = st.sidebar.multiselect('Pick regions to compare.', options=STATES, default=STATES[0])

    # Chart 1 Options
    st.write("## Generation & Emissions Across Regions")
    chosen_fuel = st.selectbox("Pick a fuel type", options=fuel_options)
    show_emissions = st.checkbox(
        "Show CO2e Emissions", value=False
    )

    # Get Data for Chart 1
    gen_by_states = {}
    emissions_by_states = {}
    for state in chosen_states_multi:
        df_generation = read_forecast(data_type, 'combined', state)
        df_generation = aggregate_by_date(df_generation, time_unit)
        gen_by_states[state] = df_generation

        df_emissions = read_emissions("total", state)
        df_emissions = aggregate_by_date(df_emissions, time_unit)
        emissions_by_states[state] = df_emissions

    # Plot Chart
    if show_emissions:
        fig = plot_combined_data_multiple_states(gen_by_states, emissions_by_states, chosen_fuel)
    else:
        fig = plot_multiple_states(gen_by_states, chosen_fuel)
    st.plotly_chart(fig)

    # Chart 2 Data and Plotting
    st.write("## Emissions Intensity Across Regions")
    emissions_by_states = {}
    for state in chosen_states_multi:
        emissions = read_emissions("intensity", state)
        emissions['date'] = pd.to_datetime(emissions['date'], format='%Y-%m-%d')
        emissions = emissions.resample(time_unit, on='date').mean().reset_index()
        emissions_by_states[state] = emissions
    fig = plot_multiple_states(emissions_by_states, "emissions_intensity")
    st.plotly_chart(fig)


def aggregate_by_date(df, time_unit, date_var="date"):
    df[date_var] = pd.to_datetime(df[date_var], format='%Y-%m-%d')
    df = df.resample(time_unit, on=date_var).sum().reset_index()
    return df

