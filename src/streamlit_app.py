import streamlit as st

from streamlit_pages.multipage import MultiPage
from streamlit_pages import emissions_on_map,  single_region_analysis, multi_region_analysis, appendix


# Create an instance of the app
st.set_page_config(page_title="Emissions Oracle", layout="wide")
app = MultiPage()

# Add all pages to application
app.add_page("Single Region Analysis", single_region_analysis.app)
app.add_page("Multi-Region Analysis", multi_region_analysis.app)
app.add_page("Emissions on USA Map", emissions_on_map.app)
app.add_page("Appendix", appendix.app)

# Run main app
app.run()