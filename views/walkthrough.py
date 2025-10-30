import streamlit as st
import base64
from common.FileUploader import FileUploader
from common.constants import (PAGE_TITLE, HEADER_STEP_1, HEADER_STEP_2, HEADER_STEP_3, 
                       STYLE_BOLD_TEXT, STEP_1_DESCRIPTION, STEP_2_DESCRIPTION, STEP_3_DESCRIPTION)

# --- Streamlit App ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Set page title
st.title(PAGE_TITLE)

# Step 1
st.header(HEADER_STEP_1)
st.markdown(STYLE_BOLD_TEXT, unsafe_allow_html=True)
st.markdown(STEP_1_DESCRIPTION)

# Display example image
file_ = open("./resources/download_example_files.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()
st.markdown(f'<img src="data:image/gif;base64,{data_url}" alt="example gif">', unsafe_allow_html=True)

# Step 2
st.header(HEADER_STEP_2)
st.markdown(STEP_2_DESCRIPTION)

# File uploader
file_uploader = FileUploader()
list_of_files = file_uploader.upload_files()
file_uploader.verify_file_count()

# Step 3
st.header(HEADER_STEP_3)
st.markdown(STEP_3_DESCRIPTION)