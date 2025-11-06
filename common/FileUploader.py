import streamlit as st
import os
import pandas as pd
import picnik as pnk
from picnik import DataExtraction as DE

class FileUploader:
    def __init__(self, label="Choose CSV files (minimum 2, maximum 20)", file_types=['csv'], max_files=20):
        self.label = label
        self.file_types = file_types
        self.max_files = max_files
        self.file_paths = []
        self.valid_files = []
        self.uploaded_files = []
        self.files_names_list = []

    def upload_files(self):
        # Create file uploader widget
        self.uploaded_files = st.file_uploader(
            self.label, 
            type=self.file_types, 
            accept_multiple_files=True
        )

        # Process uploaded files
        if self.uploaded_files:
            for uploaded_file in self.uploaded_files:
                with open(os.path.join("/tmp", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                self.file_paths.append(os.path.join("/tmp", uploaded_file.name))
        
        return self.file_paths
    
    def verify_file_count(self):
        num_files = len(self.file_paths)
        if num_files < 2:
            st.error(f"⚠️ Please upload at least 2 CSV files. Currently uploaded: {num_files}")
            return False
        elif num_files > self.max_files:
            st.error(f"⚠️ Please upload at most {self.max_files} CSV files. Currently uploaded: {num_files}")
            return False
        else:
            st.success(f"✓ {num_files} files uploaded successfully")
            return True
        
    def verify_file_columns(self):
        all_valid = True
        invalid_files = []
        self.valid_files = []

        for uploaded_file in self.file_paths:
            df = pd.read_csv(uploaded_file)
            if len(df.columns) != 3:
                all_valid = False
                invalid_files.append((uploaded_file, len(df.columns)))
            else:
                self.valid_files.append(df)

        # Display validation results
        if not all_valid:
            st.error("❌ Some files do not have exactly 3 columns:")
            for filename, num_cols in invalid_files:
                st.write(f"- the file {filename} has {num_cols} columns")
        else:
            st.success("✓ All files have exactly 3 columns")
            return True

    def show_valid_files(self):
        """
        Display the contents of valid files using Streamlit in a single component with multiple tabs.
        """
        if not self.valid_files:
            st.warning("No valid files to display. Please upload and validate files first.")
            return

        st.header("Valid Files Preview")

        # Create tabs for each valid file
        tabs = st.tabs([f"File {i+1}: {os.path.basename(self.file_paths[i])}" for i in range(len(self.valid_files))])

        # Display each file in its respective tab
        for i, (tab, valid_file) in enumerate(zip(tabs, self.valid_files)):
            with tab:
                st.dataframe(valid_file)  # Display the full DataFrame            

    def display_file_info(self):
        """
        Display file information with Reset and Extract Data buttons in the same row.
        The extracted data is displayed in a new row below the buttons.
        """
        # Create two columns for the buttons
        col1, col2 = st.columns(2)

        # Place the Reset button in the first column
        with col1:
            if st.button("Reset", type="primary"):
                st.write("Resetting the file uploader...")

        # Place the Extract Data button in the second column
        with col2:
            extract_data_clicked = st.button("Extract Data")

        # Display extracted data in a new row
        if extract_data_clicked:

            """             
            st.write("Uploaded file names:")
            st.write(self.valid_files)

            st.write("File paths:")
            st.write(self.file_paths) 
            """

            st.write("Extracting Data!")
            # Extract data from uploaded files

            data_extractor = DE()
            Bnum, T0num = data_extractor.read_files(self.file_paths)
            st.write("Files to be used: \n{}\n ".format(self.file_paths))

            data_extractor.plot_data(x_data='temperature',
                                        y_data='TG',
                                        x_units='K',
                                        y_units='%')
            st.pyplot()  # Display the plot in Streamlit

            data_extractor.Conversion(
                [data_extractor.DFlis[k]['Temperature [K]'].values[0] for k in range(len(Bnum))],
                [data_extractor.DFlis[k]['Temperature [K]'].values[-1] for k in range(len(Bnum))]
            )  # Calculation of the conversion degree in the temperature range (Ti, Tf)
            st.pyplot()  # Display the plot in Streamlit
            isoTables_num = data_extractor.Isoconversion(d_a=0.02)