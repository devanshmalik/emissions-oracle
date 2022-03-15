import streamlit as st
from pathlib import Path

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath, load_yml, load_config


def app():

    markdown_text = Path(APPENDIX_FILEPATH).read_text()
    st.markdown(markdown_text, unsafe_allow_html=True)