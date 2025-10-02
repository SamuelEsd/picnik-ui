import streamlit as st
import pandas as pd

# Set page title
st.title("CSV File Upload")

# Create file uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display success message
    st.success(f"File uploaded successfully: {uploaded_file.name}")
    
    # Show basic information about the file
    st.subheader("File Information")
    st.write(f"Number of rows: {len(df)}")
    st.write(f"Number of columns: {len(df.columns)}")
    
    # Display the dataframe
    st.subheader("Data Preview")
    st.dataframe(df)
    
    # Optional: Show column names
    st.subheader("Columns")
    st.write(df.columns.tolist())
else:
    st.info("Please upload a CSV file to get started.")