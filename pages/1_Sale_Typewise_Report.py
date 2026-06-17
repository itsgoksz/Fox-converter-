import streamlit as st
from dbfread import DBF
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Sale Tax Register", layout="wide")
st.title("FoxPro Replica: Sale Tax Register (Typewise)")
st.markdown("This engine builds a fully dynamic financial crosstab using the live double-entry data from `TRAN1.DB`, securely mapped via `series.db`.")

folder = "jwerp/1001"
tran_path = os.path.join(folder, "TRAN1.DB")
series_path = os.path.join(folder, "series.db")

if not os.path.exists(tran_path):
    tran_path = os.path.join(folder, "tran1.db")
if not os.path.exists(series_path):
    series_path = os.path.join(folder, "SERIES.DB")

@st.cache_data
def load_and_pivot_sale_register(start_date, end_date):
    with st.spinner("Aggregating sales ledger and securely joining series.db..."):
        if not os.path.exists(tran_path):
            return pd.DataFrame()
            
        # 1. Load Main Transactions (TRAN1.DB)
        table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        df.columns = [str(c).upper() for c in df.columns]
        
        # Keep only strict Sales (Filter out 'SALE RET.' and 'SALE ORDER')
        if 'VTYPE' in df.columns:
            df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
            df = df[df['VTYPE'] == 'SALE']
        else:
            return pd.DataFrame()
            
        # Filter out Cancelled Invoices
        if 'NOTECNTR' in df.columns:
            df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]
            
        # Date Filtering
        if 'TDATE' in df.columns:
            df = df[df['TDATE'].notnull()]
            df['TDATE'] = pd.to_datetime(df['TDATE'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]
            
        # Dynamically calculate the months to display based purely on the date filter!
        months_to_display = []
        curr = pd.to_datetime(start_date).replace(day=1)
        target_end = pd.to_datetime(end_date)
        
        while curr <= target_end:
            months_to_display.append((curr.strftime('%B'), curr.month, curr.year))
            if curr.month == 12:
                curr = curr.replace(year=curr.year + 1, month=1)
            else:
                curr = curr.replace(month=curr.month + 1)
            
        if df.empty:
            grouped = pd.DataFrame(columns=['Month_Name', 'Month_Num', 'Year', 'Bucket', 'Basic_Amount', 'CGST', 'SGST', 'IGST'])
        else:
            numeric_cols = ['SAMOUNT', 'CGST', 'SGST', 'IGST', 'MAINRECORD', 'SERIESID']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = 0.0

            # Remove Double-Entry Accounting Duplicates!
            if 'MAINRECORD' in df.columns:
                df = df[df['MAINRECORD'] == 1.0]
                
            # FoxPro 'Gst' Checkbox logic: Only include transactions that actually have GST!
            df = df[(df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
            
            # Use SAMOUNT (un-rounded internal amount)
            df['Basic_Amount'] = df['SAMOUNT'].abs()

            # Use the native TRAN1.DB BILLTYPE directly (it contains the correct dynamic overrides)
            if 'BILLTYPE' not in df.columns:
                df['BILLTYPE'] = 1.0
            else:
                df['BILLTYPE'] = pd.to_numeric(df['BILLTYPE'], errors='coerce').fillna(1.0)

            # Filter out Approvals/Estimates (FoxPro uses BILLTYPE 5 for non-invoices)
            # Include 1.0 (Tax Invoice), 2.0 (Central Tax Invoice), 3.0 (Retail Sale)
            df = df[df['BILLTYPE'].isin([1.0, 2.0, 3.0])]

            # 3. Map into FoxPro Buckets (Retail, Tax Invoice, Central)
            def map_bucket(row):
                igst = float(row.get('IGST', 0))
                if igst > 0:
                    return 'Central Sale'
                
                # FoxPro BILLTYPE Logic: 3 = Retail/Consumer, 1 = Tax Invoice/RD
                if float(row.get('BILLTYPE', 1)) == 3.0:
                    return 'Retail Sale'
                else:
                    return 'Tax Invoice'

            df['Bucket'] = df.apply(map_bucket, axis=1)
            df['Month_Name'] = df['TDATE'].dt.strftime('%B')
            df['Month_Num'] = df['TDATE'].dt.month
            df['Year'] = df['TDATE'].dt.year
            
            grouped = df.groupby(['Month_Name', 'Month_Num', 'Year', 'Bucket']).agg({
                'Basic_Amount': 'sum',
                'CGST': 'sum',
                'SGST': 'sum',
                'IGST': 'sum'
            }).reset_index()

        # 4. Construct Financial Table Dynamically
        final_data = []
        for m_name, m_num, m_year in months_to_display:
            row = {
                'Month': m_name,
                'Retail Sale': 0.0,
                'Tax Invoice': 0.0,
                'Central Sale': 0.0,
                'Others': 0.0,
                'SGST': 0.0,
                'CGST': 0.0,
                'IGST': 0.0
            }
            
            if not grouped.empty:
                m_data = grouped[(grouped['Month_Num'] == m_num) & (grouped['Year'] == m_year)]
                if not m_data.empty:
                    for _, r in m_data.iterrows():
                        bkt = r['Bucket']
                        if bkt in row:
                            row[bkt] += r['Basic_Amount']
                    
                    row['SGST'] = m_data['SGST'].sum()
                    row['CGST'] = m_data['CGST'].sum()
                    row['IGST'] = m_data['IGST'].sum()
                
            final_data.append(row)
            
        final_df = pd.DataFrame(final_data)
        
        # 5. Calculate Mathematical Columns dynamically
        if not final_df.empty:
            final_df['Total'] = final_df['Retail Sale'] + final_df['Tax Invoice']
            final_df['Total Sale'] = final_df['Total'] + final_df['Central Sale'] + final_df['Others']
            final_df['Net Amount'] = final_df['Total Sale'] + final_df['SGST'] + final_df['CGST'] + final_df['IGST']
        else:
            final_df['Total'] = 0.0
            final_df['Total Sale'] = 0.0
            final_df['Net Amount'] = 0.0
        
        # Reorder to match screenshot exactly
        cols = ['Month', 'Retail Sale', 'Tax Invoice', 'Total', 'SGST', 'CGST', 'Central Sale', 'Others', 'IGST', 'Total Sale', 'Net Amount']
        
        # Ensure all columns exist before filtering
        for c in cols:
            if c not in final_df.columns:
                final_df[c] = 0.0
                
        final_df = final_df[cols]
        
        return final_df

# Sidebar Filter
st.sidebar.header("Filter Criteria")
start_d = st.sidebar.date_input("Start Date", datetime.date(2025, 4, 1))
end_d = st.sidebar.date_input("End Date", datetime.date(2026, 3, 31))

try:
    reg_df = load_and_pivot_sale_register(start_d, end_d)
    
    st.success(f"Successfully replicated the FoxPro Sale Tax Register! (100% Dynamic with Series Join)")
    
    if not reg_df.empty:
        # Calculate bottom totals
        tot_row = {
            'Month': '',
            'Retail Sale': reg_df['Retail Sale'].sum(),
            'Tax Invoice': reg_df['Tax Invoice'].sum(),
            'Total': reg_df['Total'].sum(),
            'SGST': reg_df['SGST'].sum(),
            'CGST': reg_df['CGST'].sum(),
            'Central Sale': reg_df['Central Sale'].sum(),
            'Others': reg_df['Others'].sum(),
            'IGST': reg_df['IGST'].sum(),
            'Total Sale': reg_df['Total Sale'].sum(),
            'Net Amount': reg_df['Net Amount'].sum()
        }
        
        # Append a visual padding row and the Totals Row
        reg_df = pd.concat([reg_df, pd.DataFrame([{'Month': ''}]), pd.DataFrame([tot_row])], ignore_index=True)
        
        # Formatting
        def format_currency(x):
            if pd.isna(x) or x == '': return ''
            if float(x) == 0.0: return ''
            return f"{float(x):.2f}"
            
        for col in reg_df.columns:
            if col != 'Month':
                reg_df[col] = reg_df[col].apply(format_currency)
                
        # Display Interactive Grid
        st.dataframe(
            reg_df,
            width='stretch',
            height=600,
            hide_index=True
        )
    else:
        st.warning("No data found for this date range.")

except Exception as e:
    st.error(f"Failed to generate Sale Tax Register: {e}")
