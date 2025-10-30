import streamlit as st
import os

class FileUploader:
    def __init__(self, label="Choose CSV files (minimum 2, maximum 20)", file_types=['csv'], max_files=20):
        self.label = label
        self.file_types = file_types
        self.max_files = max_files
        self.file_paths = []

    def upload_files(self):
        # Create file uploader widget
        uploaded_files = st.file_uploader(
            self.label, 
            type=self.file_types, 
            accept_multiple_files=True
        )

        # Process uploaded files
        if uploaded_files:
            for uploaded_file in uploaded_files:
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
