import streamlit as st
from dbfread import DBF
import pandas as pd
import glob
import os

st.set_page_config(page_title="FoxPro Grid Engine", layout="wide")

st.title("FoxPro Grid Engine - Interactive Data Grid")
st.markdown("Select a database from the sidebar to view the interactive FoxPro Data Grid.")

# Find all DB and DBF files
folder_path = "jwerp/1001"
dbf_files = glob.glob(f"{folder_path}/*.db") + glob.glob(f"{folder_path}/*.DB") + glob.glob(f"{folder_path}/*.dbf") + glob.glob(f"{folder_path}/*.DBF")
dbf_files = sorted(list(set(dbf_files))) # Remove duplicates, just in case

if not dbf_files:
    st.warning(f"No database files found in {folder_path}!")
    st.stop()

# Create a clean display name list (e.g. 'saltrn1.db')
file_options = {os.path.basename(f): f for f in dbf_files}

st.sidebar.header("Navigation")
# Sidebar selection menu
selected_file = st.sidebar.selectbox("Select Data Table:", list(file_options.keys()))

if selected_file:
    file_path = file_options[selected_file]
    
    st.subheader(f"Viewing: {selected_file}")
    
    # Load the data table
    try:
        # We pass char_decode_errors='ignore' to prevent Unicode errors if the file has corrupted data
        # We pass ignore_missing_memofile=True so the app doesn't crash if an .fpt is missing
        with st.spinner("Loading FoxPro Data..."):
            table = DBF(file_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df = pd.DataFrame(iter(table))
        
        # Display table statistics
        st.write(f"**Total Records:** {len(df):,} &nbsp;&nbsp;|&nbsp;&nbsp; **Total Columns:** {len(df.columns)}")
        
        # Render the massive interactive grid!
        st.dataframe(
            df, 
            use_container_width=True, 
            height=600  # Give it a nice tall height like the FoxPro window
        )
        
    except Exception as e:
        st.error(f"Failed to read the database file: {e}")
