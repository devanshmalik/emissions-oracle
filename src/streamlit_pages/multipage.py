"""
This file is the framework for generating multiple Streamlit applications
through an object oriented framework.

This code is borrowed from https://github.com/prakharrathi25/data-storyteller
"""
import streamlit as st
from src.d00_utils.utils import load_config
from src.d00_utils.const import *


# Define the multipage class to manage the multiple apps in our program
class MultiPage:
    """Framework for combining multiple streamlit applications."""

    def __init__(self) -> None:
        """Constructor class to generate a list which will store all our applications as an instance variable."""
        self.pages = []
        self.config = load_config(STREAMLIT_CONFIG_FILEPATH)

    def add_page(self, title, func) -> None:
        """Class Method to Add pages to the project

        Parameters
        ------------
        title: str
            The title of page which we are adding to the list of apps
        func:
            Python function to render this page in Streamlit
        """
        self.pages.append(
            {
                "title": title,
                "function": func
            }
        )

    def run(self):
        st.sidebar.title("Emissions Oracle")

        # Dropdown to select the page to run
        page = st.sidebar.selectbox(
            'App Navigation',
            self.pages,
            format_func=lambda page: page['title'],
            help=self.config["tooltips"]["app_page_choice"]
        )

        # run the app function
        page['function']()
        