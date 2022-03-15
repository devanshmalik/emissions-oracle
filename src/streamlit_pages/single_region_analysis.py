import pandas as pd
import streamlit as st
import json
from typing import Tuple

from prophet.serialize import model_from_json
from prophet.plot import plot_components_plotly


from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_reporting.calculate_emissions import read_emissions
from src.d06_visualization.plot import plot_prophet_forecast, plot_multiple_fuels, plot_combined_data_multiple_fuels


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Basic App Info
    get_started_toggle = st.checkbox(
        "Let's Get Started!", value=False,
    )
    if not get_started_toggle:
        with st.expander("What is this app?", expanded=not get_started_toggle):
            st.write(config["app"]["app_intro"])

    if get_started_toggle:
        # Sidebar options
        st.sidebar.write("## Filters")
        chosen_data_type = st.sidebar.radio(
            "Select the type of data to analyze.",
            options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
            help=config["tooltips"]["data_type_choice"]
        )
        data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
        fuel_options = config["data_types"][data_type]["fuels"]

        chosen_state = st.sidebar.selectbox('Pick a region to visualize', STATES)
        show_all_sources_toggle = st.sidebar.checkbox(
            "Show Elec. Sources Separately", value=False, help=config["tooltips"]["show_all_sources_choice"]
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
        chosen_sources_multi = st.multiselect(
            'Pick multiple generation sources to compare.', options=fuel_options, default=fuel_options[0],
            disabled=not show_all_sources_toggle, help=config["tooltips"]["multi_sources_choice"]
        )
        show_emissions = st.checkbox(
            "Show Greenhouse Gas Emissions", value=False,
            disabled=not show_all_sources_toggle, help=config["tooltips"]["show_emissions_choice"]
        )

        if not show_all_sources_toggle:
            with st.expander("More info on this plot", expanded=not get_started_toggle):
                st.write(config["explanations"]["single_region_prophet"])

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
                title, ylabel = get_chart_labels(chosen_state, data_type)
                fig = plot_multiple_fuels(gen_by_fuels,
                                          chosen_sources_multi, title=title, ylabel=ylabel)
        else:
            gen_by_chosen_fuel = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
            gen_by_chosen_fuel = aggregate_by_date(gen_by_chosen_fuel, time_unit, "ds")

            title, ylabel = get_chart_labels(chosen_state, data_type)
            title = title + " - {}".format(chosen_fuel.title())
            fig = plot_prophet_forecast(gen_by_chosen_fuel, title=title, ylabel=ylabel)
        st.plotly_chart(fig)

        # Prophet Components
        st.write("## Impact of Components in Forecast")
        st.write(config["explanations"]["components"])
        plot_components(chosen_fuel, chosen_state, data_type)


def plot_components(chosen_fuel: str, chosen_state: str, data_type: str):
    """
    Get data for Prophet model components and plot it.

    Parameters
    -----------
    chosen_fuel: str
        Type of fuel
    chosen_state: str
        State of interest
    data_type: str
        Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.
    """
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


def get_chart_labels(chosen_state: str, data_type: str) -> Tuple[str, str]:
    """
    Get strings for chart elements when plotting

    Parameters
    -----------
    chosen_state: str
        State of interest
    data_type: str
        Type of data being extracted such as `Net_Gen_By_Fuel_MWh`, `Fuel_Consumption_BTU`.

    Returns
    --------
    Tuple[str, str]
        Strings for the title and y-axis label
    """
    if data_type == "Net_Gen_By_Fuel_MWh":
        title = "Net Electricity Generation - {}".format(chosen_state)
        ylabel = "Net Generation (Thousand  MWh)"
    else:
        title = "Total Fuel Consumption - {}".format(chosen_state)
        ylabel = "Fuel Consumption (million MMBtu)"
    return title, ylabel


def aggregate_by_date(df: pd.DataFrame, time_unit: str, date_var: str = "date") -> pd.DataFrame:
    """
    Aggregate data by time unit.

    Parameters
    -----------
    df: pd.DataFrame
        Data to aggregate
    time_unit: str
        String signifying time unit to group data by (Q: Quarter, Y: Year)
    date_var: str
        String for the data column name in dataframe

    Returns
    ---------
    pd.DataFrame
        Data grouped by time unit
    """
    df[date_var] = pd.to_datetime(df[date_var], format='%Y-%m-%d')
    df = df.resample(time_unit, on=date_var).sum().reset_index()
    return df

