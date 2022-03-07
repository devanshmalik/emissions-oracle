import os
import streamlit as st
import numpy as np
from PIL import  Image

# Custom imports
from streamlit_pages.multipage import MultiPage
from streamlit_pages import total_net_gen, test_page

# Create an instance of the app
app = MultiPage()

st.set_page_config(page_title="Emissions Oracle", layout="wide")

# Add all your application here
app.add_page("Total Net Generation", total_net_gen.app)
app.add_page("Change Metadata", test_page.app)

# The main app
app.run()