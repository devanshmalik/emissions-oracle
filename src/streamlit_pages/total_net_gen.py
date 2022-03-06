import streamlit as st
from prophet.serialize import model_from_json
import json

from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_visualization.plot import plot

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Option to select prediction type
    chosen_data_type = st.radio("Select the type of data you want to analyze.",
                         options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
                         help="Write about reg and classification")
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"

    # Use two column technique
    col1, col2 = st.columns(2)
    # Design column 1
    chosen_state = col1.selectbox('Pick a state to visualize', STATES)
    chosen_fuel = col2.selectbox('Pick a fuel type', config["data_types"][data_type]["fuels"])


    forecast_type = 'individual'
    df = read_forecast(data_type, forecast_type, chosen_state, chosen_fuel)

    fig = plot(df)
    st.write(fig)


