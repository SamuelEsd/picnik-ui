import streamlit as st
import pandas as pd
import picnik as pnk
from picnik import DataExtraction as DE
import numpy as np
import os
import matplotlib.pyplot as plt
from common.FileUploader import FileUploader


# --- TODO: Complete picnik web ui tool ---

st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )

# Set page title
st.title("Picnik web UI")
st.write("This is a web application for picnik python package.")
st.write("Picnik - Python Isoconversional Computations for Non-Isothermal Kinetics. [GitHub Repository](https://github.com/ErickErock/pICNIK)")
st.write("Please upload your CSV files below.")


# Create an instance of FileUploader
file_uploader = FileUploader()

# Let the user choose data source (upload or select default dataset)
file_uploader.choose_input_source()

# File uploader
if (file_uploader.verify_file_count() and file_uploader.verify_file_columns()):
    file_uploader.show_valid_files()
    file_uploader.display_file_info()
    # Run conversion UI after display_file_info so conversion uses session state
    file_uploader.run_conversion()
    #file_uploader.display_all_plots()


