import streamlit as st
from dbfread import DBF
import pandas as pd
import os

st.set_page_config(page_title="Stock Status Report", layout="wide")
st.title("FoxPro Replica: In Hand Stock Status")
st.markdown("This engine mathematically aggregates the live balances from `itstd1.db` to reconstruct the FoxPro report.")

folder = "jwerp/1001"
itstd_path = os.path.join(folder, "itstd1.db")
items_path = os.path.join(folder, "items.db")

if not os.path.exists(itstd_path):
    st.error(f"Cannot find the stock transaction file at {itstd_path}")
    st.stop()

@st.cache_data
def load_and_calculate_stock():
    with st.spinner("Aggregating live stock balances from thousands of transactions. This may take a moment..."):
        # 1. Load the raw transactions
        table = DBF(itstd_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        
        # 2. Extract only the math columns we need for Stock Status
        numeric_cols = ['PC', 'GWT', 'WT', 'DIAWT', 'STNWT', 'RATE', 'MAMT']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # 3. Load Items Master to get the human-readable names
        if os.path.exists(items_path):
            item_table = DBF(items_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df_items = pd.DataFrame(iter(item_table))
            
            if 'ITEMSID' in df_items.columns and 'ITEMS' in df_items.columns:
                df_items['ITEMSID'] = df_items['ITEMSID'].astype(str).str.strip()
                df['INO'] = df.get('INO', '').astype(str).str.strip()
                
                # Merge Item Name and Purity (TUNCH)
                df = df.merge(df_items[['ITEMSID', 'ITEMS', 'TUNCH']], left_on='INO', right_on='ITEMSID', how='left')
                df['Item Name'] = df['ITEMS'].fillna('Unknown Item')
                df['Purity'] = df['TUNCH'].fillna('')
            else:
                df['Item Name'] = df.get('INO', 'Unknown')
                df['Purity'] = ''
        else:
            df['Item Name'] = df.get('INO', 'Unknown')
            df['Purity'] = ''
            
        # 4. Handle the Unit column securely
        unit_file1 = os.path.join(folder, "unitmst.db")
        unit_file2 = os.path.join(folder, "units.db")
        df['Unit'] = df.get('UNITID', '')
        
        for uf in [unit_file1, unit_file2]:
            if os.path.exists(uf):
                u_table = DBF(uf, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
                df_u = pd.DataFrame(iter(u_table))
                # Find the ID and Name columns dynamically
                uid_col = [c for c in df_u.columns if 'ID' in c.upper()]
                uname_col = [c for c in df_u.columns if 'NAME' in c.upper() or c.upper() == 'UNIT']
                
                if uid_col and uname_col:
                    df_u[uid_col[0]] = df_u[uid_col[0]].astype(str).str.strip()
                    df['UNITID'] = df['UNITID'].astype(str).str.strip()
                    df = df.merge(df_u[[uid_col[0], uname_col[0]]], left_on='UNITID', right_on=uid_col[0], how='left')
                    df['Unit'] = df[uname_col[0]].fillna(df['UNITID'])
                    break
        
        # 5. Group By exactly like the FoxPro screenshot!
        grouped = df.groupby(['Item Name', 'Purity', 'Unit'], dropna=False).agg({
            'PC': 'sum',
            'GWT': 'sum',
            'WT': 'sum',
            'DIAWT': 'sum',
            'STNWT': 'sum',
            'RATE': 'mean', # Rate is usually an average or latest, we'll use mean
            'MAMT': 'sum'
        }).reset_index()
        
        # 6. Rename columns to match the FoxPro Screenshot exactly
        grouped = grouped.rename(columns={
            'PC': 'Pc',
            'GWT': 'Gr.Wt.',
            'WT': 'Net Wt.',
            'DIAWT': 'Dia Wt',
            'STNWT': 'Stn Wt',
            'RATE': 'Rate',
            'MAMT': 'Amount'
        })
        
        # Clean up floating point math (round to 3 decimals like FoxPro)
        for col in ['Gr.Wt.', 'Net Wt.', 'Dia Wt', 'Stn Wt', 'Rate', 'Amount']:
            grouped[col] = grouped[col].round(3)
            
        # Optional: Replace 0.0 with blank strings if you prefer a cleaner look like the FoxPro screenshot
        # grouped = grouped.replace(0.0, '')
        
        # Sort Alphabetically by Item Name
        grouped = grouped.sort_values(by=['Item Name'])
        
        return grouped

try:
    stock_df = load_and_calculate_stock()
    
    st.success("Successfully replicated the FoxPro live stock aggregation algorithms!")
    
    # Calculate Grand Totals to show at the bottom
    total_pc = stock_df['Pc'].sum()
    total_gwt = stock_df['Gr.Wt.'].sum()
    total_nwt = stock_df['Net Wt.'].sum()
    total_amt = stock_df['Amount'].sum()
    
    st.write(f"**Grand Totals:** &nbsp;&nbsp; Pc: `{total_pc}` | Gr.Wt.: `{total_gwt:.3f}` | Net Wt.: `{total_nwt:.3f}` | Amount: `₹{total_amt:,.2f}`")
    
    # Render with Streamlit's awesome interactive features
    st.dataframe(
        stock_df,
        use_container_width=True,
        height=700,
        hide_index=True
    )
    
except Exception as e:
    st.error(f"Failed to generate report: {e}")
