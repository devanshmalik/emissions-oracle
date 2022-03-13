import pandas as pd
import streamlit as st
import json

from prophet.serialize import model_from_json
from prophet.plot import plot_components_plotly


from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_reporting.calculate_emissions import read_emissions
from src.d06_visualization.plot import (
    plot_prophet_forecast,
    plot_multiple_fuels,
    plot_combined_data_multiple_fuels,
)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Set up sidebar options
    st.sidebar.title("Filters")
    chosen_data_type = st.sidebar.radio(
        "Select the type of data to analyze.",
        options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
        help=config["tooltips"]["data_type_choice"]
    )
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    chosen_state = st.sidebar.selectbox('Pick a region to visualize', STATES)
    show_all_sources_toggle = st.sidebar.checkbox(
        "Show Generation Sources Separately", value=False, help=config["tooltips"]["show_all_sources_choice"]
    )
    chosen_fuel = st.sidebar.selectbox(
        "Pick a generation type", options=fuel_options, disabled=show_all_sources_toggle,
    )
    time_units_mapping = {"Quarter": "Q", "Year": "Y"}
    chosen_time_unit = st.sidebar.radio(
        "Select the time unit to view data by.",
        options=["Quarter", "Year"],
        help=config["tooltips"]["time_unit_choice"]
    )
    time_unit = time_units_mapping[chosen_time_unit]

    # Main Chart Options
    # TODO: Add documentation on what this analysis is and guide on how to use it
    chosen_sources_multi = st.multiselect(
        'Pick multiple generation sources to compare.', options=fuel_options, default=fuel_options[0],
        disabled=not show_all_sources_toggle, help=config["tooltips"]["multi_sources_choice"]
    )
    show_emissions = st.checkbox(
        "Show Greenhouse Gas Emissions", value=False,
        disabled=not show_all_sources_toggle, help=config["tooltips"]["show_emissions_choice"]
    )

    # Get Data and Plot
    if show_all_sources_toggle:
        gen_by_fuels = read_forecast(data_type, 'combined', chosen_state, chosen_fuel)
        gen_by_fuels = aggregate_by_date(gen_by_fuels, time_unit)
        if show_emissions:
            emissions_df = read_emissions("total", chosen_state)
            emissions_df = aggregate_by_date(emissions_df, time_unit)

            # Chart Elements
            title = "CO<sub>2</sub> Equivalent Emissions for Specified Generation"
            ylabel = "Net Generation (Thousand  MWh)" if data_type == "Net_Gen_By_Fuel_MWh" else "Fuel Consumption (million MMBtu)"
            fig = plot_combined_data_multiple_fuels(gen_by_fuels, emissions_df, chosen_sources_multi,
                                                    title=title, ylabel=ylabel)
        else:
            title, ylabel = get_chart_labels(chosen_fuel, chosen_state, data_type)
            fig = plot_multiple_fuels(gen_by_fuels,
                                      chosen_sources_multi, title=title, ylabel=ylabel)
    else:
        gen_by_chosen_fuel = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
        gen_by_chosen_fuel = aggregate_by_date(gen_by_chosen_fuel, time_unit, "ds")

        title, ylabel = get_chart_labels(chosen_fuel, chosen_state, data_type)
        title = title + " - {}".format(chosen_fuel.title())
        fig = plot_prophet_forecast(gen_by_chosen_fuel, title=title, ylabel=ylabel)
    st.plotly_chart(fig)

    # Chart 2 Data and Plotting
    st.write("## Impact of Components in Forecast")
    # Get model and forecast
    save_folder = '{}/{}'.format(data_type, chosen_state)
    models_file_name = '{}-{}.{}'.format(data_type, chosen_fuel, 'json')
    models_file_path = get_filepath(MODELS_FOLDER, save_folder, models_file_name)
    with open(models_file_path, 'r') as fin:
        model = model_from_json(json.load(fin))
    forecast = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)

    # Plot components
    forecast['ds'] = pd.to_datetime(forecast['ds'], format='%Y-%m-%d')
    fig = plot_components_plotly(model, forecast)
    st.plotly_chart(fig)


def get_chart_labels(chosen_fuel, chosen_state, data_type):
    if data_type == "Net_Gen_By_Fuel_MWh":
        title = "Net Electricity Generation - {}".format(chosen_state)
        ylabel = "Net Generation (Thousand  MWh)"
    else:
        title = "Total Fuel Consumption - {}".format(chosen_state)
        ylabel = "Fuel Consumption (million MMBtu)"
    return title, ylabel


def aggregate_by_date(df, time_unit, date_var="date"):
    df[date_var] = pd.to_datetime(df[date_var], format='%Y-%m-%d')
    df = df.resample(time_unit, on=date_var).sum().reset_index()
    return df

