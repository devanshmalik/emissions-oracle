from dotenv import load_dotenv, find_dotenv
import logging
import os
from pathlib import Path
import yaml

from typing import Any, Dict, Tuple

import io
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import toml

# from src.d00_utils.const import *

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def setup_env_vars():
    log.info("Finding .env file to load entries as environment variables...")
    # find .env automagically by walking up directories until it's found
    dotenv_path = find_dotenv()

    # load up the entries as environment variables
    load_dotenv(dotenv_path)
    log.info("Finished loading environment variables.")
    return


def get_filepath(parent_folder, save_folder, file_name):
    """Create folder for saving data (if not exists already) and
    return final filepath.

    Eg: For parent_folder = 'data/01_raw/', save_folder = 'Net_Generation'
     and file_name = 'net_generation_{}.{}'
    - Create following folders: 'data/01_raw/Net_Generation'
    - Return filepath: 'data/01_raw/Net_Generation/net_generation_{}.{}'
    """
    folder_path = os.path.join(parent_folder, save_folder)
    Path(folder_path).mkdir(parents=True, exist_ok=True)

    return os.path.join(folder_path, file_name)


def load_yml(filepath):
    yaml_file = open(filepath)
    return yaml.load(yaml_file, Loader=yaml.FullLoader)


@st.cache(allow_output_mutation=True, ttl=300)
def load_config(filepath) -> dict:
    """Loads configuration files.
    Parameters
    ----------
    config_streamlit_filename : str
        Filename of lib configuration file.
    config_instructions_filename : str
        Filename of custom config instruction file.
    config_readme_filename : str
        Filename of readme configuration file.
    Returns
    -------
    dict
        Lib configuration file.
    dict
        Readme configuration file.
        :param filepath:
    """
    return dict(toml.load(filepath))


def reduce_streamlit_padding():
    padding = 0
    st.markdown(f""" <style>
                .reportview-container .main .block-container{{
                    padding-top: {padding}rem;
                    padding-right: {padding}rem;
                    padding-left: {padding}rem;
                    padding-bottom: {padding}rem;
                }} </style> """, unsafe_allow_html=True)