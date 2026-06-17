import streamlit as st
from dbfread import DBF
import pandas as pd
import os

st.set_page_config(page_title="FoxPro Menu Engine", layout="wide")

st.title("FoxPro Menu Replication Engine")

file_path = "jwerp/1001/mnu.db"

if not os.path.exists(file_path):
    st.error(f"Cannot find menu database at {file_path}")
    st.stop()

@st.cache_data
def load_menu_data():
    try:
        table = DBF(file_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        
        # Ensure correct data types to prevent matching errors
        df['MNUID'] = df['MNUID'].astype(str).str.strip()
        df['UNDER'] = df['UNDER'].astype(str).str.strip()
        
        # FoxPro uses '\<' or '&' in captions for keyboard hotkeys, let's clean them up
        df['MNUCAP'] = df['MNUCAP'].astype(str).str.strip().str.replace(r'[\&\<]', '', regex=True) 
        
        # Sort by menu order if column exists
        if 'MNUORDER' in df.columns:
            df['MNUORDER'] = pd.to_numeric(df['MNUORDER'], errors='coerce').fillna(0)
            df = df.sort_values(by=['UNDER', 'MNUORDER'])
        
        # Filter out hidden menus (where HIDE is True or 'T')
        if 'HIDE' in df.columns:
            df = df[df['HIDE'] != True]
            df = df[df['HIDE'] != 'T']
            
        return df
    except Exception as e:
        st.error(f"Failed to load menu database: {e}")
        return pd.DataFrame()

df_menu = load_menu_data()

if df_menu.empty:
    st.stop()

st.sidebar.title("Jwelly Main Menu")

# Keep track of the selected menu item in session state
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = None

def render_menu(df):
    # Group by MNO (Main Menu)
    main_menus = df[df['SMNO1'] == 0].sort_values('MNUORDER')
    
    for _, main_row in main_menus.iterrows():
        main_mno = main_row['MNO']
        main_cap = main_row['MNUCAP']
        
        # Find children (SMNO1 > 0, SMNO2 == 0)
        sub1_items = df[(df['MNO'] == main_mno) & (df['SMNO1'] > 0) & (df['SMNO2'] == 0)].sort_values('MNUORDER')
        
        if not sub1_items.empty:
            with st.sidebar.expander(f"📂 {main_cap}", expanded=False):
                for _, sub1_row in sub1_items.iterrows():
                    sub1_val = sub1_row['SMNO1']
                    sub1_cap = sub1_row['MNUCAP']
                    
                    # Find grandchildren (SMNO2 > 0)
                    sub2_items = df[(df['MNO'] == main_mno) & (df['SMNO1'] == sub1_val) & (df['SMNO2'] > 0)].sort_values('MNUORDER')
                    
                    if not sub2_items.empty:
                        st.markdown(f"**🔽 {sub1_cap}**")
                        for _, sub2_row in sub2_items.iterrows():
                            if st.button(f"📄 {sub2_row['MNUCAP']}", key=sub2_row['MNUID'], use_container_width=True):
                                st.session_state.selected_menu = sub2_row
                    else:
                        if st.button(f"📄 {sub1_cap}", key=sub1_row['MNUID'], use_container_width=True):
                            st.session_state.selected_menu = sub1_row
        else:
            if st.button(f"📄 {main_cap}", key=main_row['MNUID'], use_container_width=True):
                st.session_state.selected_menu = main_row

with st.sidebar:
    render_menu(df_menu)

# Main Area Display
if st.session_state.selected_menu is not None:
    sel = st.session_state.selected_menu
    st.header(f"▶️ Executing: {sel['MNUCAP']}")
    
    cmd = str(sel.get('CMD', '')).strip()
    skey = str(sel.get('SKEY', '')).strip()
    
    st.markdown("### FoxPro Internal Action Discovered!")
    
    if cmd and cmd != 'nan':
        st.success(f"**Raw Command:** `{cmd}`")
    else:
        st.warning("No command specified.")
        
    if skey and skey != 'nan':
        st.info(f"**Internal Key/Shortcut:** `{skey}`")
        
    st.markdown("---")
    st.markdown("""
    **What does this mean?**
    - If the command starts with `DO FORM`, FoxPro is opening a Data Grid UI (like your Sale Tax Register). We can look at `formmst.db` to replicate this.
    - If it starts with `REPORT FORM`, it is running a printed report. The command will contain the exact `.frx` filename!
    - If it calls a `.PRG` file, it is executing custom business logic.
    """)
else:
    st.write("👈 **Open the sidebar on the left and navigate through the Jwelly FoxPro menu tree!**")
    st.write("Click on any leaf report to reveal the internal FoxPro command it executes.")
