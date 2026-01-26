import streamlit as st
import pandas as pd
import picnik as pnk
from picnik import DataExtraction as DE
import numpy as np
import os
import matplotlib.pyplot as plt

from src.config import APP_TITLE
from src.ui.WorkflowUI import WorkflowUI


# --- Streamlit Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Set page title
st.title(APP_TITLE)
st.write("Web-based data analysis and visualization platform for thermal analysis.")
st.write("Built with Streamlit, Pandas, Plotly, and SciPy for interactive thermal data processing.")
st.write("Learn more about thermal analysis: [GitHub - Picnik](https://github.com/ErickErock/pICNIK)")


# Initialize WorkflowUI
workflow_ui = WorkflowUI()

# Step 1: Data source selection
file_paths = workflow_ui.choose_input_source()

# Step 2: File validation
if file_paths:
    if workflow_ui.verify_file_count(file_paths):
        valid_files, invalid_files = workflow_ui.verify_file_structure(file_paths)
        
        if valid_files:
            # Display preview of validated files
            workflow_ui.display_file_preview(valid_files, file_paths)
            
            # Step 3: Data extraction controls
            workflow_ui.display_extraction_controls()
            
            # Step 4: Handle data extraction
            if workflow_ui.handle_data_extraction():
                # Step 5: Display plots
                workflow_ui.display_plots()
                
                # Step 6: Display conversion controls
                workflow_ui.display_conversion_controls()


