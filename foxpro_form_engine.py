import streamlit as st
from dbfread import DBF
import pandas as pd
import glob
import os

st.set_page_config(page_title="FoxPro Form Engine", layout="wide")
st.title("FoxPro Dynamic Grid Form Engine")

folder_path = "jwerp/1001"
formmst_path = os.path.join(folder_path, "formmst.db")
formprn_path = os.path.join(folder_path, "formprn.db")

if not os.path.exists(formmst_path) or not os.path.exists(formprn_path):
    st.error("Missing formmst.db or formprn.db in the 1001 folder.")
    st.stop()

@st.cache_data
def load_form_list():
    try:
        table = DBF(formmst_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        # Drop duplicates and empty names
        forms = df['FORMNAME'].dropna().astype(str).str.strip().unique()
        return sorted([f for f in forms if f])
    except Exception as e:
        st.error(f"Failed to load form master: {e}")
        return []

@st.cache_data
def load_form_blueprint(form_name):
    try:
        table = DBF(formprn_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        
        # Filter for the selected form
        df_form = df[df['FORMNAME'].astype(str).str.strip() == form_name]
        
        if df_form.empty:
            return pd.DataFrame()
            
        # Ensure SRNO is numeric so we display columns in the exact left-to-right order FoxPro uses
        if 'SRNO' in df_form.columns:
            df_form['SRNO'] = pd.to_numeric(df_form['SRNO'], errors='coerce').fillna(999)
            df_form = df_form.sort_values('SRNO')
            
        # Extract PFILE (internal db column name) and DISPNAME (grid header)
        blueprint = df_form[['PFILE', 'DISPNAME']].copy()
        blueprint['PFILE'] = blueprint['PFILE'].astype(str).str.strip().str.upper()
        blueprint['DISPNAME'] = blueprint['DISPNAME'].astype(str).str.strip()
        
        return blueprint
    except Exception as e:
        st.error(f"Failed to load form blueprint: {e}")
        return pd.DataFrame()

# UI Layout
st.sidebar.header("1. Select Blueprint")
forms = load_form_list()
selected_form = st.sidebar.selectbox("Choose a FoxPro UI Form:", [""] + forms)

st.sidebar.header("2. Select Raw Data Source")
dbf_files = glob.glob(f"{folder_path}/*.db") + glob.glob(f"{folder_path}/*.DB") + glob.glob(f"{folder_path}/*.dbf") + glob.glob(f"{folder_path}/*.DBF")
dbf_files = sorted(list(set(dbf_files)))
file_options = {os.path.basename(f): f for f in dbf_files}
selected_data = st.sidebar.selectbox("Choose Database File to Inject:", [""] + list(file_options.keys()))

st.markdown("---")

if selected_form:
    blueprint = load_form_blueprint(selected_form)
    
    st.subheader(f"Blueprint Rules: `{selected_form}`")
    
    if blueprint.empty:
        st.warning("No columns found for this form in formprn.db.")
    else:
        # Show the blueprint mapping
        st.write("This grid requires the following internal fields and maps them to these human-readable headers:")
        st.dataframe(blueprint.T, use_container_width=True)
        
        if selected_data:
            st.markdown("---")
            st.subheader("Final Mapped Grid Engine")
            try:
                with st.spinner("Injecting raw data into blueprint..."):
                    data_path = file_options[selected_data]
                    table = DBF(data_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
                    df_data = pd.DataFrame(iter(table))
                    
                    # Convert columns to uppercase for matching
                    df_data.columns = [str(c).upper() for c in df_data.columns]
                    
                    # Find which blueprint columns actually exist in the selected data file
                    valid_cols = []
                    display_names = {}
                    
                    for _, row in blueprint.iterrows():
                        pfile = row['PFILE']
                        disp = row['DISPNAME']
                        if pfile in df_data.columns:
                            valid_cols.append(pfile)
                            # Use DISPNAME if provided, else fallback to internal PFILE name
                            display_names[pfile] = disp if disp else pfile
                            
                    if not valid_cols:
                        st.error("None of the fields expected by this Form were found in the selected database file! Are you sure this is the correct data file for this grid?")
                    else:
                        # Filter dataframe and rename columns!
                        df_view = df_data[valid_cols].rename(columns=display_names)
                        
                        st.success(f"Successfully mapped {len(valid_cols)} out of {len(blueprint)} expected fields from `{selected_data}`.")
                        st.dataframe(df_view, use_container_width=True, height=600)
            except Exception as e:
                st.error(f"Failed to load data: {e}")
else:
    st.info("👈 Select a UI Blueprint from the sidebar to begin.")
