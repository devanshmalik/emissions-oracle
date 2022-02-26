import streamlit as st
from prophet.serialize import model_from_json
import json

from prophet.plot import plot_plotly, plot_components_plotly
from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath


def app():
    save_folder = 'Net_Gen_By_State'
    file_name = 'net_generation_{}.{}'
    models_file_path = get_filepath(MODELS_FOLDER, save_folder, file_name)
    reporting_file_path = get_filepath(REPORTING_FOLDER, save_folder, file_name)

    chosen_state = st.selectbox('Pick a state to visualize', STATES)
    st.write(f"State Chosen: {chosen_state}")


    @st.cache
    def refresh_plots(state):
        with open(models_file_path.format(state, 'json'), 'r') as fin:
            model = model_from_json(json.load(fin))

            future = model.make_future_dataframe(periods=16, freq='Q')
            forecast = model.predict(future)
            # forecast = pd.read_csv(reporting_file_path.format('AL', 'csv'))

            return model, forecast


    model, forecast = refresh_plots(chosen_state)
    fig1 = plot_plotly(model, forecast)
    st.write(fig1)

    fig2 = plot_components_plotly(model, forecast)
    st.write(fig2)


