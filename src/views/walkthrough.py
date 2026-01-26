import streamlit as st
import base64
from pathlib import Path

from src.config import APP_TITLE, RESOURCES_DIR
from src.ui.WorkflowUI import WorkflowUI

# --- Streamlit App Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Initialize WorkflowUI
workflow_ui = WorkflowUI()

# Set page title
st.title(f"{APP_TITLE} - Tutorial")

# Step 1: Introduction
st.header("Step 1: Download Example Files")
st.markdown(
    """
    <span style='font-weight: bold;'>
    Learn how to download and prepare your thermal analysis data files
    </span>
    """, 
    unsafe_allow_html=True
)
st.markdown(
    """
    1. Navigate to the resources folder in the project
    2. Download the example CSV files from `resources/default_files/`
    3. Files must have exactly 3 columns: Temperature, TG, and DTG
    4. Ensure CSV encoding is UTF-8 or UTF-16 LE for compatibility
    """
)

# Display example image if available
gif_path = RESOURCES_DIR / "download_example_files.gif"
if gif_path.exists():
    with open(gif_path, "rb") as file_:
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="example gif">', 
            unsafe_allow_html=True
        )
else:
    st.info("Example GIF not found. Continue to Step 2 to upload your files.")

# Step 2: File Upload and Validation
st.header("Step 2: Upload Your Data Files")
st.markdown(
    f"""
    Upload your CSV files for thermal analysis. 
    Each file must contain exactly **3 columns**.
    """
)

# Use WorkflowUI to handle file selection
file_paths = workflow_ui.choose_input_source()

step_2_completed = False
valid_files = []

if file_paths:
    # Verify file count
    if workflow_ui.verify_file_count(file_paths):
        # Verify file structure
        valid_files, invalid_files = workflow_ui.verify_file_structure(file_paths)
        
        if valid_files:
            step_2_completed = True
            workflow_ui.display_file_preview(valid_files, file_paths)

# Step 3: Next Steps
st.header("Step 3: Proceed to Analysis")
st.markdown(
    """
    Your data has been validated and is ready for analysis!
    
    Next steps:
    1. Go to the **Tool** page from the navigation menu
    2. Click "Extract Data" to process the files
    3. Visualize and analyze your thermal data with interactive plots
    4. Run conversion and isoconversion analysis
    """
)

if step_2_completed:
    st.success("Your files are ready! Navigate to the Tool page to continue with data analysis.")
else:
    st.warning("Please ensure your files are valid before proceeding to the Tool page.")
