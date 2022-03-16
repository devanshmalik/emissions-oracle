# Package Imports
import pandas as pd
import streamlit as st

# First Party Imports
from src.d00_utils.const import REPORTING_FOLDER, STATES_YML_FILEPATH, STREAMLIT_CONFIG_FILEPATH
from src.d00_utils.utils import get_filepath, load_config, load_yml
from src.d06_visualization.plot import plot_map


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    st.write("## Emissions Across All States")
    with st.expander("More info on this section", expanded=False):
        st.write(config["explanations"]["emissions_on_map"])

    # Set up sidebar options
    emissions_type = st.sidebar.radio(
        "Select the type of emissions data.",
        options=["Emissions Intensity", "Total Emissions"],
        help=config["tooltips"]["emissions_type_choice"],
    )

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
    chosen_fuel = col2.selectbox(
        "Pick a generation type",
        options=fuel_options,
        help=config["tooltips"]["source_choice_for_map"],
        disabled=turn_off_widget,
    )

    if chosen_year >= 2022:
        st.write("**Note**: Viewing Forecasted Emissions!")

    # Get Data and Plot Chart
    if emissions_type == "Emissions Intensity":
        file_name = "Combined-CO2e-Emissions-Intensity.csv"
        df = get_emissions_data(file_name)

        # Aggregate by state and time unit (mean aggregation for emissions intensity)
        df = df.groupby([pd.Grouper(key="date", freq="Y"), "state"]).mean().reset_index()
        data = df[df["date"].dt.year == chosen_year]

        # Map state names to state codes
        states_dict = load_yml(STATES_YML_FILEPATH)
        data.replace({"state": states_dict}, inplace=True)

        # Chart Elements + Plot
        title = "Electricity Generation Emissions Intensity by State"
        colorbar_title = "kg CO<sub>2</sub>e per MWh"
        fig = plot_map(data, "emissions_intensity", colorbar_title=colorbar_title, title=title)
    else:
        file_name = "Combined-CO2e-Total-Emissions.csv"
        df = get_emissions_data(file_name)

        # Aggregate by state and time unit (sum aggregation for total emissions)
        df = df.groupby([pd.Grouper(key="date", freq="Y"), "state"]).sum().reset_index()
        data = df[df["date"].dt.year == chosen_year]

        # Map state names to state codes
        states_dict = load_yml(STATES_YML_FILEPATH)
        data.replace({"state": states_dict}, inplace=True)

        # Chart Elements + Plot
        title = "Electricity Generation Emissions by State - {}".format(chosen_fuel.title())
        colorbar_title = "Thousand metric tons CO<sub>2</sub>e"
        fig = plot_map(data, chosen_fuel, colorbar_title=colorbar_title, title=title)
    st.plotly_chart(fig)


def get_emissions_data(file_name: str) -> pd.DataFrame:
    """
    Read combined emissions data CSV for plotting.

    Parameters
    -----------
    file_name: str
        File name of emissions CSV

    Returns
    --------
    pd.DataFrame
        Emission forecast dataframe
    """
    target_folder = "Emission_Forecasts"
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    return df
