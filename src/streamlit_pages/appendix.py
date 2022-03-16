# Python Libraries
from pathlib import Path

# Package Imports
import streamlit as st

# First Party Imports
from src.d00_utils.const import APPENDIX_FILEPATH


def app():
    markdown_text = Path(APPENDIX_FILEPATH).read_text()
    st.markdown(markdown_text, unsafe_allow_html=True)
