import streamlit as st
from prophet.serialize import model_from_json
import json
from st_aggrid import AgGrid
import pandas as pd

from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config


def app():

    st.title("Test Page")
    chosen_state = st.selectbox('Pick a state to visualize', STATES)
    st.write(f"State Chosen: {chosen_state}")
    test = st.sidebar.radio("Select the type of data you want to analyze.",
                            options=[" (MWh)", "nsumption (BTU)"],
                            help="Write about reg and classification", key="test")

    target_folder = 'Emission_Forecasts'
    file_name = 'Combined-CO2e-Total-Emissions.csv'
    file_path = get_filepath(REPORTING_FOLDER, target_folder, file_name)
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    AgGrid(df)