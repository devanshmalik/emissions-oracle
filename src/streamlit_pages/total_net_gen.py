import streamlit as st
from prophet.serialize import model_from_json
import json
import pandas as pd
from datetime import datetime

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
    plot_multiple_fuels_plus_emissions,
    plot_map
)

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    test = st.sidebar.radio("Select the type of data you want to analyze.",
                                  options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
                                  help="Write about reg and classification", key="test")
    st.write(test)
    # Option to select prediction type
    col1, col2 = st.columns(2)
    chosen_data_type = col1.radio("Select the type of data you want to analyze.",
                         options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
                         help="Write about reg and classification")
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    time_units_mapping = {"Quarter": "Q", "Year": "Y"}
    chosen_time_unit = col2.radio("Select the time units to view data by.", options=["Quarter", "Year"])
    time_unit = time_units_mapping[chosen_time_unit]

    with st.expander("Single Region Analysis", expanded=False):
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
            gen_fcst['date'] = pd.to_datetime(gen_fcst['date'], format='%Y-%m-%d')
            gen_fcst = gen_fcst.resample(time_unit, on='date').sum().reset_index()
            if show_emissions:
                emissions_fcst = read_emissions("total", chosen_state)
                emissions_fcst['date'] = pd.to_datetime(emissions_fcst['date'], format='%Y-%m-%d')
                emissions_fcst = emissions_fcst.resample(time_unit, on='date').sum().reset_index()

                fig = plot_multiple_fuels_plus_emissions(gen_fcst, emissions_fcst, chosen_fuel_multi)
            else:
                fig = plot_plotly_combined(gen_fcst, chosen_fuel_multi)
        else:
            fcst = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
            fcst['ds'] = pd.to_datetime(fcst['ds'], format='%Y-%m-%d')

            # Transform data based on time unit chosen
            fcst = fcst.resample(time_unit, on='ds').sum().reset_index()
            fig = plot_plotly_individual(fcst)

        st.plotly_chart(fig)

    with st.expander("Multi Regions Analysis", expanded=False):
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
            fcst['date'] = pd.to_datetime(fcst['date'], format='%Y-%m-%d')
            fcst = fcst.resample(time_unit, on='date').sum().reset_index()
            combined_fcst[state] = fcst

            emissions = read_emissions("total", state)
            emissions['date'] = pd.to_datetime(emissions['date'], format='%Y-%m-%d')
            emissions = emissions.resample(time_unit, on='date').sum().reset_index()
            combined_emissions[state] = emissions

        if show_emissions:
            fig = combine_plots(combined_fcst, combined_emissions, chosen_fuel)
        else:
            fig = plot_multiple_states(combined_fcst, chosen_fuel)
        st.plotly_chart(fig)

    with st.expander("Multi State Emissions Intensity", expanded=True):
        chosen_states_multi = st.multiselect('Pick regions to compare.', options=STATES,
                                               default=STATES[0], key='multi_2')
        combined_emissions = {}
        for state in chosen_states_multi:
            emissions = read_emissions("intensity", state)
            emissions['date'] = pd.to_datetime(emissions['date'], format='%Y-%m-%d')
            emissions = emissions.resample(time_unit, on='date').mean().reset_index()
            combined_emissions[state] = emissions
        fig = plot_multiple_states(combined_emissions, "emissions_intensity")
        st.plotly_chart(fig)

    with st.expander("Emissions Visualization on USA Map", expanded=False):
        emissions_type = st.radio("Select the type of emissions data.",
                                  options=["Emissions Intensity", "Total Emissions"],
                                  help="Add details here")
        turn_off_widget = emissions_type == "Emissions Intensity"
        col1, col2 = st.columns([4, 1])
        chosen_year = col1.slider(
            "Pick a year in time",
            value=2021,
            min_value=2001,
            max_value=2025,
            key="slider_2"
        )
        chosen_fuel = col2.selectbox("Pick a fuel type",
                                     options=fuel_options, help="Only available for Total Emissions",
                                     key="fuel_3", disabled=turn_off_widget)

        target_folder = 'Emission_Forecasts'
        if emissions_type == "Emissions Intensity":
            file_name = 'Combined-CO2e-Emissions-Intensity.csv'
            file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

            # Aggregate by state and time unit
            df = df.groupby([pd.Grouper(key='date', freq=time_unit), 'state']).mean().reset_index()
            fig = plot_map(df[df['date'].dt.year == chosen_year], "emissions_intensity")
        else:
            file_name = 'Combined-CO2e-Total-Emissions.csv'
            file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

            # Aggregate by state and time unit
            df = df.groupby([pd.Grouper(key='date', freq=time_unit), 'state']).sum().reset_index()
            fig = plot_map(df[df['date'].dt.year == chosen_year], chosen_fuel)
        st.plotly_chart(fig)




# Emissions intensity graphing code
# combined_emissions = {}
# for state in chosen_states_multi:
#     emissions = read_emissions("intensity", state)
#     emissions['date'] = pd.to_datetime(emissions['date'], format='%Y-%m-%d')
#     emissions = emissions.resample(time_unit, on='date').mean().reset_index()
#     combined_emissions[state] = emissions
# fig = plot_multiple_states(combined_emissions, "emissions_intensity")


