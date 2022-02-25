import streamlit as st
import os
from prophet.serialize import model_from_json
import json
import yaml

from prophet.plot import plot_plotly, plot_components_plotly

YML_FILE_PATH = os.path.join(os.getcwd(), '../conf/base/', 'states.yml')
MODELS_FOLDER = os.path.join(os.getcwd(), '../data/04_models/')
REPORTING_FOLDER = os.path.join(os.getcwd(), '../data/06_reporting/')

file_path = 'Net_Gen_By_State/net_generation_{}.{}'
models_file_path = os.path.join(MODELS_FOLDER, file_path)
reporting_file_path = os.path.join(REPORTING_FOLDER, file_path)


states_yaml = open(YML_FILE_PATH)
states = yaml.load(states_yaml, Loader=yaml.FullLoader)
chosen_state = st.selectbox(
     'Pick a state to visualize', states)
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


