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

# Call the upload_files method to display the widget and get file paths
list_of_files = file_uploader.upload_files()

# File uploader
step_2_completed = False
if (file_uploader.verify_file_count() and file_uploader.verify_file_columns()):
    file_uploader.show_valid_files()
    file_uploader.display_file_info()


