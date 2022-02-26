import streamlit as st
from prophet.serialize import model_from_json
import json

from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *


def app():

    st.title("Test Page")
    chosen_state = st.selectbox('Pick a state to visualize', STATES)
    st.write(f"State Chosen: {chosen_state}")


