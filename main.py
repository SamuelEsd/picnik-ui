import streamlit as st
import pandas as pd
import picnik as pnk
import numpy as np
import matplotlib.pyplot as plt


# Set page title
st.title("CSV File Upload")

# Create file uploader widget that accepts multiple files
uploaded_files = st.file_uploader("Choose CSV files (minimum 2, maximum 20)", type=['csv'], accept_multiple_files=True)

# Check number of uploaded files
num_files = len(uploaded_files)

files_names_list = []


if num_files > 0:
    # Validate number of files
    if num_files < 2:
        st.error(f"⚠️ Please upload at least 2 CSV files. Currently uploaded: {num_files}")
    elif num_files > 20:
        st.error(f"⚠️ Please upload at most 20 CSV files. Currently uploaded: {num_files}")
    else:
        st.success(f"✓ {num_files} files uploaded successfully")
        
        # Validate each file has exactly 3 columns
        all_valid = True
        invalid_files = []
        valid_files = []
        
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            if len(df.columns) != 3:
                all_valid = False
                invalid_files.append((uploaded_file.name, len(df.columns)))
            else:
                valid_files.append(df)
        
        # Display validation results
        if not all_valid:
            st.error("❌ Some files do not have exactly 3 columns:")
            for filename, num_cols in invalid_files:
                st.write(f"- {filename}: {num_cols} columns")
        else:
            st.success("✓ All files have exactly 3 columns")
            
            # Display information for each file
            for i, valid_file in enumerate(valid_files, 1):
                st.success("iterating: " + str(i))
                df = valid_file
                filename = uploaded_files[i-1].name
                files_names_list.append(filename)

                with st.expander(f"File {i}: {filename}"):
                    
                    st.write(f"**Rows:** {len(df)}")
                    st.write(f"**Columns:** {df.columns.tolist()}")
                    st.dataframe(df)
            st.button("Reset", type="primary")
            if st.button("Extrcat Data"):
                st.write("Extracting Data!")
            else:
                st.write("")
else:
    st.info("Please upload between 2 and 20 CSV files to get started.")
