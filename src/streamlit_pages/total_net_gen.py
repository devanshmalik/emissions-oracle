import streamlit as st
from prophet.serialize import model_from_json
import json

# from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config
from src.d06_reporting.create_forecasts import read_forecast
from src.d06_visualization.plot import plot, plot_plotly_individual, plot_plotly_combined

EIA_API_IDS = load_yml(EIA_API_IDS_YML_FILEPATH)


def app():
    config = load_config(STREAMLIT_CONFIG_FILEPATH)

    # Option to select prediction type
    chosen_data_type = st.radio("Select the type of data you want to analyze.",
                         options=["Net Electricity Generation (MWh)", "Electricity Fuel Consumption (BTU)"],
                         help="Write about reg and classification")
    data_type = 'Net_Gen_By_Fuel_MWh' if chosen_data_type == "Net Electricity Generation (MWh)" else "Fuel_Consumption_BTU"
    fuel_options = config["data_types"][data_type]["fuels"]

    with st.expander("One State Analysis", expanded=True):
        # Columns to select state, individual vs combined chart
        col1, col2, col3 = st.columns(3)
        chosen_state = col1.selectbox('Pick a state to visualize', STATES)
        is_combined_chart = col3.checkbox(
            "Show all fuels on chart", value=False, help="Add a help message here."
        )
        chosen_fuel = col2.selectbox(
            "Pick a fuel type", options=fuel_options, disabled=is_combined_chart
        )
        chosen_fuel_multi = st.multiselect(
            'For all fuels chart, pick curves to view.', options=fuel_options, default=fuel_options,
            disabled=not is_combined_chart
        )

        # Display figure for type of chart
        if is_combined_chart:
            fcst = read_forecast(data_type, 'combined', chosen_state)
            fig2 = plot_plotly_combined(fcst, chosen_fuel_multi)
            st.plotly_chart(fig2)
        else:
            fcst = read_forecast(data_type, 'individual', chosen_state, chosen_fuel)
            fig = plot_plotly_individual(fcst)
            st.plotly_chart(fig)

