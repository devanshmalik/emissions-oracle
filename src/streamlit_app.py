import os
import streamlit as st

# Custom imports
from streamlit_pages.multipage import MultiPage
from streamlit_pages import emissions_on_map,  single_region_analysis, multi_region_analysis, appendix

st.set_page_config(page_title="Emissions Oracle", layout="wide")

# Create an instance of the app
app = MultiPage()

# Add all your application here
app.add_page("Single Region Analysis", single_region_analysis.app)
app.add_page("Multi-Region Analysis", multi_region_analysis.app)
app.add_page("Emissions on USA Map", emissions_on_map.app)
app.add_page("Appendix", appendix.app)

# The main app
app.run()