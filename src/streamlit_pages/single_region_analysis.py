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

    chosen_state = st.sidebar.selectbox('Pick a region to visualize', STATES)
    show_all_fuels_toggle = st.sidebar.checkbox(
        "Show All Fuels on Chart", value=False, help="Add a help message here."
    )
    chosen_fuel = st.sidebar.selectbox(
        "Pick a fuel type", options=fuel_options, disabled=show_all_fuels_toggle
    )
    time_units_mapping = {"Quarter": "Q", "Year": "Y"}
    chosen_time_unit = st.sidebar.radio(
        "Select the time unit to view data by.",
        options=["Quarter", "Year"],
        help="Suggest a time frame depending on model (probably quarterly)"
    )
    time_unit = time_units_mapping[chosen_time_unit]

    # Main Chart Options
    # TODO: Add documentation on what this analysis is and guide on how to use it
    chosen_fuel_multi = st.multiselect(
        'Pick multiple fuels to compare.', options=fuel_options, default=fuel_options[0],
        disabled=not show_all_fuels_toggle, help="Only available when 'Show All Fuels on Chart' is checked"
    )
    show_emissions = st.checkbox(
        "Show CO2e Emissions", value=False,
        help="Only available when 'Show All Fuels on Chart' is checked", disabled=not show_all_fuels_toggle
    )

    # Get Data and Plot
    if show_all_fuels_toggle:
        gen_by_fuels = read_forecast(data_type, 'combined', chosen_state, chosen_fuel)
        gen_by_fuels = aggregate_by_date(gen_by_fuels, time_unit)
        if show_emissions:
            emissions_df = read_emissions("total", chosen_state)
            emissions_df = aggregate_by_date(emissions_df, time_unit)
            fig = plot_combined_data_multiple_fuels(gen_by_fuels, emissions_df, chosen_fuel_multi)
        else:
            fig = plot_multiple_fuels(gen_by_fuels, chosen_fuel_multi)
    else:
        gen_by_chosen_fuel = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
        gen_by_chosen_fuel = aggregate_by_date(gen_by_chosen_fuel, time_unit, "ds")
        fig = plot_prophet_forecast(gen_by_chosen_fuel)
    st.plotly_chart(fig)


def aggregate_by_date(df, time_unit, date_var="date"):
    df[date_var] = pd.to_datetime(df[date_var], format='%Y-%m-%d')
    df = df.resample(time_unit, on=date_var).sum().reset_index()
    return df

