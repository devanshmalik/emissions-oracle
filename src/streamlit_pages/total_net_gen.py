import streamlit as st
from prophet.serialize import model_from_json
import json

# from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_reporting.calculate_emissions import read_emissions
from src.d06_visualization.plot import (
    plot,
    plot_plotly_individual,
    plot_plotly_combined,
    plot_multiple_states,
    combine_plots,
    plot_multiple_fuels_plus_emissions
)

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Option to select prediction type
    chosen_data_type = st.radio("Select the type of data you want to analyze.",
                         options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
                         help="Write about reg and classification")
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    with st.expander("Single Region Analysis", expanded=True):
        # Columns to select state, individual vs combined chart
        col1, col2, col3 = st.columns([1, 1, 1])
        chosen_state = col1.selectbox('Pick a region to visualize', STATES)
        is_combined_chart = col3.checkbox(
            "Show All Fuels on Chart", value=False, help="Add a help message here."
        )
        chosen_fuel = col2.selectbox(
            "Pick a fuel type", options=fuel_options, disabled=is_combined_chart, key="fuel_1"
        )
        # TODO: Change the order of checkbox and multi drop down
        col1, col2 = st.columns([2, 1])
        chosen_fuel_multi = col1.multiselect(
            'Pick multiple fuels to compare.', options=fuel_options, default=fuel_options[0],
            disabled=not is_combined_chart, help="Only available when 'Show All Fuels on Chart' is checked"
        )
        show_emissions = col2.checkbox(
            "Show CO2e Emissions", value=False,
            help="Only available when 'Show All Fuels on Chart' is checked", disabled=not is_combined_chart
        )

        # Display figure for type of chart
        if is_combined_chart:
            gen_fcst = read_forecast(data_type, 'combined', chosen_state)
            if show_emissions:
                emissions_fcst = read_emissions(chosen_state)
                fig = plot_multiple_fuels_plus_emissions(gen_fcst, emissions_fcst, chosen_fuel_multi)
            else:
                fig = plot_plotly_combined(gen_fcst, chosen_fuel_multi)
        else:
            fcst = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
            fig = plot_plotly_individual(fcst)

        st.plotly_chart(fig)


    with st.expander("Multi Regions Analysis", expanded=True):
        # Columns to select state, individual vs combined chart
        col1, col2, col3 = st.columns([3, 2, 2])
        chosen_states_multi = col1.multiselect('Pick regions to compare.', options=STATES, default=STATES[0])
        chosen_fuel = col2.selectbox("Pick a fuel type", options=fuel_options, key="fuel_2")

        show_emissions = col3.checkbox(
            "Show CO2e Emissions", value=True, key="show_emissions_2",
        )
        combined_fcst = {}
        combined_emissions = {}
        for state in chosen_states_multi:
            fcst = read_forecast(data_type, 'combined', state)
            combined_fcst[state] = fcst

            emissions = read_emissions(state)
            combined_emissions[state] = emissions

        if show_emissions:
            fig = combine_plots(combined_fcst, combined_emissions, chosen_fuel)
        else:
            fig = plot_multiple_states(combined_fcst, chosen_fuel)
        st.plotly_chart(fig)





