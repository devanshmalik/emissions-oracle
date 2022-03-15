import streamlit as st
from pathlib import Path

from src.d00_utils.const import *


def app():
    markdown_text = Path(APPENDIX_FILEPATH).read_text()
    st.markdown(markdown_text, unsafe_allow_html=True)