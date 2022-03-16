import sys
import os
sys.path.append("../src/")
sys.path.append("/app/emissions-oracle/src/")
print(os.path.basename(os.getcwd()))

# Package Imports
import streamlit as st

# First Party Imports
from streamlit_pages import (
    appendix,
    emissions_on_map,
    multi_region_analysis,
    single_region_analysis,
)
from streamlit_pages.multipage import MultiPage

# Create an instance of the app
st.set_page_config(page_title="Emissions Oracle", layout="wide", page_icon="⚡")
app = MultiPage()

# Add all pages to application
app.add_page("Single Region Analysis", single_region_analysis.app)
app.add_page("Multi-Region Analysis", multi_region_analysis.app)
app.add_page("Emissions on USA Map", emissions_on_map.app)
app.add_page("Appendix", appendix.app)

# Run main app
app.run()
