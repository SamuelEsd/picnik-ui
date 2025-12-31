import streamlit as st
import os
import pandas as pd
import picnick_dev as pnk
from picnick_dev import DataExtraction as DE
import matplotlib.pyplot as plt
import plotly.express as px
from .PlotPlotly import PlotlyPlotter as PP


class FileUploader:
    def __init__(self, label="Choose CSV files (minimum 2, maximum 20)", file_types=['csv'], max_files=20, default_dir="./resources/default_files"):
        self.label = label
        self.file_types = file_types
        self.max_files = max_files
        self.default_dir = default_dir
        self.file_paths = []
        self.valid_files = []
        self.uploaded_files = []
        self.files_names_list = []
        self.data_extractor = None


    def load_default_files(self):
        """
        Load default files from the specified directory.
        """
        if os.path.exists(self.default_dir) and os.path.isdir(self.default_dir):
            default_files = [os.path.join(self.default_dir, f) for f in os.listdir(self.default_dir) if f.endswith(tuple(self.file_types))]
            self.file_paths.extend(default_files)
            st.info(f"Loaded default files from: {self.default_dir}")
        else:
            st.warning(f"Default directory '{self.default_dir}' does not exist or is not accessible.")


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

    def choose_input_source(self):
        """
        Display a toggle (radio) between uploading files and selecting the default dataset.
        - If 'Upload files' is chosen, render the uploader widget (via `upload_files`).
        - If 'Select default dataset' is chosen, show available default file names and
          allow selecting which ones to use. Selected default files are set to
          `self.file_paths` so the rest of the class can operate on them.
        """
        st.divider()
        st.subheader("Data Source Selection")
        
        choice = st.radio("Data source:", ["Select default dataset", "Upload files"], index=0, key="input_source_radio")

        
        if choice == "Select default dataset":  # Select default dataset
            # Gather folders and files from the default directory
            if os.path.exists(self.default_dir) and os.path.isdir(self.default_dir):
                # List subdirectories
                subdirs = [d for d in os.listdir(self.default_dir) if os.path.isdir(os.path.join(self.default_dir, d))]

                # Present a folder chooser (include root as an option)
                folder_options = subdirs
                chosen_folder = st.selectbox("Choose default folder:", folder_options, index=0)

                # Determine folder path to list files from
                folder_path = os.path.join(self.default_dir, chosen_folder)

                # Gather files in the selected folder
                default_files = [f for f in os.listdir(folder_path) if f.endswith(tuple(self.file_types))]
                if not default_files:
                    st.warning("No default files found in the selected folder.")
                    return

                # Display the available default files and allow the user to pick which ones to use
                chosen = st.multiselect("Choose default files to use:", default_files, default=default_files)
                # Map chosen basenames to full paths
                chosen_paths = [os.path.join(folder_path, c) for c in chosen]
                if chosen_paths:
                    self.file_paths = chosen_paths
                    st.session_state['file_paths'] = self.file_paths
                    st.session_state['file_paths_source'] = 'default'
                    st.session_state['file_paths_folder'] = folder_path
                    st.success(f"Selected {len(chosen_paths)} default file(s) from '{os.path.basename(folder_path)}'")
                    # Optionally show the selected names
                    st.write("Files to be used:")
                    for p in chosen_paths:
                        st.write(f"- {os.path.basename(p)}")
                else:
                    st.info("No default files selected.")
            else:
                st.error(f"Default directory '{self.default_dir}' does not exist.")
        else:
            # Clear previous default file selection when switching
            if 'file_paths' in st.session_state and st.session_state.get('file_paths_source') == 'default':
                st.session_state.pop('file_paths', None)
                st.session_state.pop('file_paths_source', None)
                self.file_paths = []
            # Render uploader widget (this will append uploaded paths to self.file_paths)
            self.upload_files()

    
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
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            except UnicodeDecodeError as ue:
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-16le')
                except Exception as e:
                    st.error(f"Failed to read {uploaded_file}: {e}")
                    all_valid = False
                    invalid_files.append((uploaded_file, 'Unreadable'))
                    continue
            except Exception as e:
                st.error(f"Failed to read {uploaded_file}: {e}")
                all_valid = False
                invalid_files.append((uploaded_file, 'Unreadable'))
                continue
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
                # Clear stored state so the app resets cleanly
                for k in [
                    'data_extractor', 'Bnum', 'T0num', 'conversion_ready', 'last_conversion_figure', 'file_paths'
                ]:
                    if k in st.session_state:
                        del st.session_state[k]
                # Also clear instance state
                self.file_paths = []
                self.valid_files = []
                self.uploaded_files = []
                #st.experimental_rerun()

        # Place the Extract Data button in the second column
        with col2:
            st.button(
                "Extract Data",
                key="extract_data_btn",
                on_click=lambda: st.session_state.update({"extract_data_clicked": True})
            )

        # Display extracted data in a new row
        if st.session_state.get('extract_data_clicked'):
            st.write("Extracting Data!")
            # Extract data from uploaded files


            self.data_extractor = DE()
            try:
                Bnum, T0num = self.data_extractor.read_files(self.file_paths)
            except UnicodeDecodeError:
                st.warning("Default encoding failed, retrying with utf-16le...")
                # Try to re-read all files as utf-16le and save to temp, then retry
                import tempfile
                import shutil
                temp_paths = []
                for f in self.file_paths:
                    try:
                        df = pd.read_csv(f, encoding='utf-16le')
                        # Save to a new temp file as utf-8
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                        df.to_csv(tmp.name, index=False, encoding='utf-8')
                        temp_paths.append(tmp.name)
                    except Exception as e:
                        st.error(f"Failed to re-encode {f} as utf-8: {e}")
                if temp_paths:
                    Bnum, T0num = self.data_extractor.read_files(temp_paths)
                    st.info("Files reloaded as utf-16le and re-encoded to utf-8 for processing.")
                    # Optionally clean up temp files after use
                    for t in temp_paths:
                        try:
                            os.remove(t)
                        except Exception:
                            pass
                else:
                    st.error("Could not process any files as utf-16le.")
                    return
            st.write("Files to be used: \n{}\n ".format(self.file_paths))

            # Persist extraction results in session state so they survive reruns
            st.session_state['data_extractor'] = self.data_extractor
            st.session_state['Bnum'] = Bnum
            st.session_state['T0num'] = T0num
            st.session_state['conversion_ready'] = True
            st.session_state['file_paths'] = self.file_paths

            simple_figure = self.data_extractor.plot_data(x_data='temperature',
                                        y_data='TG',
                                        x_units='K',
                                        y_units='%')
            #st.pyplot(simple_figure)  # Display the plot in Streamlit

            plotly_plotter = PP(title="TG vs Temperature", x_label="Temperature [K]", y_label="TG [%]", from_matplotlib_fig=simple_figure)
            plotly_plotter.show()

            self.display_all_plots()

# TODO: before running the conversion, give inputs for ranges in each data set, 
# for each tab of a graph give the option to set the lower and upper limits of x axes.
# This would in turn affect the conversion function which should also


# dar opcion de conjunto inicial de datos o seleccionar archivos locales,
# después de eso seguir

    def run_conversion(self):
        """
        Display a button to run the conversion and isoconversion calculations.
        Uses `st.session_state` to retrieve the previously-extracted data so
        the conversion survives Streamlit reruns triggered by widgets.
        """
        if not st.session_state.get('conversion_ready'):
            st.info("Conversion not available. Click 'Extract Data' first.")
            return

        st.divider()
        st.subheader("Conversion Settings")

        # Provide a button to configure conversion ranges 
        if st.button("Configure Ranges", key="configure_ranges_button"):
            self.choose_conversion_ranges()

        # Display preview of selected ranges if they exist
        ranges = st.session_state.get('conversion_ranges')
        Bnum = st.session_state.get('Bnum')
        if ranges and Bnum:
            st.write("**Selected Temperature Ranges:**")
            for idx, (min_temp, max_temp) in enumerate(ranges):
                st.write(f"  Dataset {idx+1}: {min_temp:.2f} K → {max_temp:.2f} K")
        else:
            st.info("No custom ranges set. Default first-to-last temperature will be used.")

        st.divider()

        # Show the Run Conversion button. When clicked the page will rerun,
        # but needed objects are stored in session_state.
        if st.button("Run Conversion", key="run_conversion_button", type="primary"):
            try:
                data_extractor = st.session_state.get('data_extractor')
                Bnum = st.session_state.get('Bnum')
                if data_extractor is None or Bnum is None:
                    st.error("No extracted data available for conversion.")
                    return

                # Use user-selected ranges if available, otherwise default to first/last
                ranges = st.session_state.get('conversion_ranges')
                if ranges and len(ranges) == len(Bnum):
                    Ti_list = [r[0] for r in ranges]
                    Tf_list = [r[1] for r in ranges]
                else:
                    Ti_list = [data_extractor.DFlis[k]['Temperature [K]'].values[0] for k in range(len(Bnum))]
                    Tf_list = [data_extractor.DFlis[k]['Temperature [K]'].values[-1] for k in range(len(Bnum))]

                conversion_figure = data_extractor.Conversion(Ti_list, Tf_list)  # Calculation of conversion degree

                isoTables_num = data_extractor.Isoconversion(d_a=0.02)

                # Persist last conversion figure so it can survive further reruns
                st.session_state['last_conversion_figure'] = conversion_figure
                st.success("✓ Conversion and isoconversion calculations completed successfully")

                # Display the conversion plot if it was returned
                if conversion_figure is not None:
                    st.pyplot(conversion_figure)
            except Exception as e:
                st.error(f"❌ Error during conversion: {str(e)}")


    def choose_conversion_ranges(self):
        """
        Open a modal that displays temperature values for each dataset and lets
        the user pick a min and max for each. The result is stored in
        `st.session_state['conversion_ranges']` as a list of `(min, max)` tuples
        and must have the same length as `Bnum`.
        """
        if not st.session_state.get('conversion_ready'):
            st.info("No extracted data available. Click 'Extract Data' first.")
            return

        data_extractor = st.session_state.get('data_extractor') or self.data_extractor
        Bnum = st.session_state.get('Bnum')
        if data_extractor is None or Bnum is None:
            st.error("No extracted data available for selecting ranges.")
            return

        # Open modal for selecting ranges
        st.write("Pick a minimum and maximum temperature for each dataset.")
        temp_ranges = []

        # For each dataset, present slider-based temperature range selection
        for k in range(len(Bnum)):
            # Retrieve temperature values for dataset k
            try:
                temps = data_extractor.DFlis[k]['Temperature [K]'].values
            except Exception:
                st.error(f"Could not read temperatures for dataset index {k}")
                return

            # Ensure temps is a sorted list of unique values
            temps_list = sorted(list(dict.fromkeys([float(t) for t in temps])))
            min_temp = temps_list[0]
            max_temp = temps_list[-1]

            st.markdown(f"**Dataset {k+1}** ({os.path.basename(st.session_state.get('file_paths', [f'file_{k}'])[k]) if 'file_paths' in st.session_state and k < len(st.session_state['file_paths']) else 'unknown file'})")

            # Use a range slider for this dataset
            range_key = f"conv_range_{k}"
            range_vals = st.slider(
                f"Temperature range (dataset {k+1})",
                min_value=min_temp,
                max_value=max_temp,
                value=(min_temp, max_temp),
                step=None,
                key=range_key
            )
            temp_ranges.append((float(range_vals[0]), float(range_vals[1])))

        # Buttons at bottom of modal
        ok = st.button("Apply ranges")
        cancel = st.button("Cancel")

        if cancel:
            st.info("Conversion range selection cancelled.")
            return

        if ok:
            # Validate count
            if len(temp_ranges) != len(Bnum):
                st.error("Number of ranges does not match number of datasets.")
                return

            # Final validation: ensure min <= max for all
            for idx, (mn, mx) in enumerate(temp_ranges):
                if mn > mx:
                    st.error(f"Dataset {idx+1}: min ({mn}) is greater than max ({mx}). Fix and apply again.")
                    return

            st.session_state['conversion_ranges'] = temp_ranges
            st.success("Conversion ranges saved")



    def display_all_plots(self):
        """
        Display all available plots from the DataExtraction class using Streamlit, with interactive x-range selection for each curve.
        Always plot the graph, and only recalculate curve data on Truncate click. Store curve values and x-ranges in session_state.
        """
        x_data_options = ['time', 'temperature']
        y_data_options = ['TG', 'DTG', 'dT/dt']
        x_units_options = {'time': ['min'], 'temperature': ['K']}
        y_units_options = {
            'TG': ['%'],
            'DTG': ['%/min'],
            'dT/dt': ['K/min']
        }

        tabs = []
        for x_data in x_data_options:
            for y_data in y_data_options:
                for x_unit in x_units_options[x_data]:
                    for y_unit in y_units_options[y_data]:
                        tabs.append(f"{x_data} ({x_unit}) vs {y_data} ({y_unit})")

        st.markdown(
            """
            <style>
            .streamlit-tabs {
                display: flex;
                overflow-x: auto;
                white-space: nowrap;
            }
            .streamlit-tabs::-webkit-scrollbar {
                height: 8px;
            }
            .streamlit-tabs::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            .streamlit-tabs::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.container():
            st.markdown('<div class="streamlit-tabs">', unsafe_allow_html=True)
            tab_objects = st.tabs(tabs)
            st.markdown('</div>', unsafe_allow_html=True)

            for i, tab in enumerate(tab_objects):
                with tab:
                    x_data, x_unit, y_data, y_unit = tabs[i].split(" ")[0], tabs[i].split("(")[1].split(")")[0], tabs[i].split("vs")[1].split("(")[0].strip(), tabs[i].split("vs")[1].split("(")[1].split(")")[0]
                    st.subheader(f"Plot: {x_data} ({x_unit}) vs {y_data} ({y_unit})")
                    try:
                        # Call the plot_data method with the current combination
                        current_figure = self.data_extractor.plot_data(x_data=x_data, y_data=y_data, x_units=x_unit, y_units=y_unit)
                        #st.pyplot(current_figure)  # Render the plot in Streamlit

                        plotly_plotter = PP(title=f"{x_data} ({x_unit}) vs {y_data} ({y_unit})", x_label=f"{x_data} [{x_unit}]", y_label=f"{y_data} [{y_unit}]", from_matplotlib_fig=current_figure)
                        plotly_plotter.show()
                    except KeyError:
                        st.error(f"Invalid combination: {x_data} ({x_unit}) vs {y_data} ({y_unit})")