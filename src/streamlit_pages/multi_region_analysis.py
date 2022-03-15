import pandas as pd
import streamlit as st

from src.d00_utils.const import *
from src.d00_utils.utils import load_yml, load_config, get_filepath
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_reporting.calculate_emissions import read_emissions
from src.d06_visualization.plot import plot_multiple_states, plot_combined_data_multiple_states


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Sidebar options
    st.sidebar.write("## Filters")
    chosen_data_type = st.sidebar.radio(
        "Select the type of data to analyze.",
        options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
        help=config["tooltips"]["data_type_choice"]
    )
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    time_units_mapping = {"Quarter": "Q", "Year": "Y"}
    chosen_time_unit = st.sidebar.radio(
        "Select the time unit to view data by.",
        options=["Quarter", "Year"]
    )
    time_unit = time_units_mapping[chosen_time_unit]
    chosen_states_multi = st.sidebar.multiselect('Pick regions to compare.', options=STATES, default=STATES[0])

    # Download Raw Data (through sidebar)
    setup_data_download(config)

    # Chart 1 Options
    st.write("## Electricity Generation & Emissions Across Regions")
    chosen_fuel = st.selectbox("Pick a generation type", options=fuel_options)
    show_emissions = st.checkbox(
        "Show Greenhouse Gas Emissions", value=False, help=config["tooltips"]["show_emissions_multi_region"]
    )

    # Get Data for Chart 1
    emissions_by_states, gen_by_states = get_multi_region_data(chosen_states_multi, data_type, time_unit)

    # Plot Chart 1
    ylabel = "Net Generation (Thousand  MWh)" if data_type == "Net_Gen_By_Fuel_MWh" else "Fuel Consumption (million MMBtu)"
    if show_emissions:
        fig = plot_combined_data_multiple_states(gen_by_states, emissions_by_states, chosen_fuel,
                                                 ylabel=ylabel)
    else:
        fig = plot_multiple_states(gen_by_states, chosen_fuel, ylabel=ylabel)
    st.plotly_chart(fig)

    # Emissions Intensity Section
    plot_emissions_intensity(chosen_states_multi, time_unit, config)


def get_multi_region_data(chosen_states_multi, data_type, time_unit):
    gen_by_states = {}
    emissions_by_states = {}
    for state in chosen_states_multi:
        df_generation = read_forecast(data_type, 'combined', state)
        df_generation = aggregate_by_date(df_generation, time_unit)
        gen_by_states[state] = df_generation

        df_emissions = read_emissions("total", state)
        df_emissions = aggregate_by_date(df_emissions, time_unit)
        emissions_by_states[state] = df_emissions
    return emissions_by_states, gen_by_states


def setup_data_download(config):
    st.sidebar.write("## Download Data")
    chosen_download_type = st.sidebar.radio(
        "Select the type of raw data to download",
        options=["Net Electricity Generation",
                 "Total Emissions By Generation Source", "Emissions Intensity"],
        help=config["tooltips"]["download_type_choice"]
    )
    csv = get_download_data(chosen_download_type)
    st.sidebar.download_button(
        label=f"Download Data as CSV",
        data=csv,
        file_name=f'{chosen_download_type}.csv',
        mime='text/csv',
    )


def plot_emissions_intensity(chosen_states_multi, time_unit, config):
    st.write("## Emissions Intensity Across Regions")
    with st.expander("More info on emissions intensity", expanded=False):
        st.write(config["explanations"]["emissions_intensity"])
    emissions_by_states = {}
    for state in chosen_states_multi:
        emissions = read_emissions("intensity", state)
        emissions['date'] = pd.to_datetime(emissions['date'], format='%Y-%m-%d')
        emissions = emissions.resample(time_unit, on='date').mean().reset_index()
        emissions_by_states[state] = emissions
    ylabel = "Emissions Intensity (kg CO<sub>2</sub>e per MWh)"
    fig = plot_multiple_states(emissions_by_states, "emissions_intensity",
                               ylabel=ylabel)
    st.plotly_chart(fig)


def aggregate_by_date(df, time_unit, date_var="date"):
    df[date_var] = pd.to_datetime(df[date_var], format='%Y-%m-%d')
    df = df.resample(time_unit, on=date_var).sum().reset_index()
    return df


def get_download_data(chosen_download_type):
    if chosen_download_type == "Net Electricity Generation":
        target_folder = 'Combined_Forecasts'
        file_name = 'Combined-Electricity-Generation-All-States.csv'
    elif chosen_download_type == "Total Emissions By Generation Source":
        target_folder = 'Emission_Forecasts'
        file_name = "Combined-CO2e-Total-Emissions.csv"
    else:
        target_folder = 'Emission_Forecasts'
        file_name = "Combined-CO2e-Emissions-Intensity.csv"

    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    df = pd.read_csv(file_path)
    return df.to_csv().encode('utf-8')
