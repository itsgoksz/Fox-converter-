import streamlit as st
from dbfread import DBF
import pandas as pd
import os
import datetime

st.set_page_config(page_title="GST Summary Report", layout="wide")
st.title("FoxPro Replica: Sale/Purchase Summary (GSTR 3B)")
st.markdown("This engine filters double-entries using `MAINRECORD`, pulls weights from `ITRAN1.DB`, dynamically constructs GST Types, and subtracts taxes to find the true Basic Amount.")

folder = "jwerp/1001"
tran_path = os.path.join(folder, "TRAN1.DB")
itran_path = os.path.join(folder, "ITRAN1.DB")

if not os.path.exists(tran_path):
    tran_path = os.path.join(folder, "tran1.db")

@st.cache_data
def load_and_aggregate_gst(start_date, end_date):
    with st.spinner("Aggregating GST records and performing tax deductions..."):
        if not os.path.exists(tran_path):
            return pd.DataFrame()
            
        # 1. Load Main Transactions (TRAN1.DB)
        table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        df.columns = [str(c).upper() for c in df.columns]
        
        # Date Filtering
        if 'TDATE' in df.columns:
            df = df[df['TDATE'].notnull()]
            df = df[(df['TDATE'] >= start_date) & (df['TDATE'] <= end_date)]
            
        if df.empty:
            return pd.DataFrame()
            
        # Extract numeric columns
        numeric_cols = ['AMOUNT', 'CGST', 'SGST', 'IGST', 'MAINRECORD', 'TRNID', 'PTAX']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # Remove Double-Entry Accounting Duplicates!
        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]
            
        df = df[(df['AMOUNT'] != 0) | (df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
        
        # FoxPro stores Sales as negative credits. We need absolute values for the GST report.
        df['AMOUNT'] = df['AMOUNT'].abs()

        # 2. Fetch Weights from ITRAN1.DB
        if os.path.exists(itran_path):
            i_table = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df_i = pd.DataFrame(iter(i_table))
            df_i.columns = [str(c).upper() for c in df_i.columns]
            
            if 'TRNID' in df_i.columns and 'WT' in df_i.columns:
                df_i['TRNID'] = pd.to_numeric(df_i['TRNID'], errors='coerce').fillna(0)
                df_i['WT'] = pd.to_numeric(df_i['WT'], errors='coerce').fillna(0)
                
                weights = df_i.groupby('TRNID')['WT'].sum().reset_index()
                df = df.merge(weights, on='TRNID', how='left')
                df['WT'] = df['WT'].fillna(0.0)
            else:
                df['WT'] = 0.0
        else:
            df['WT'] = 0.0

        # 3. Dynamically Construct "Particular" (e.g. SALE LOCAL RD)
        def get_particular(row):
            vtype = str(row.get('VTYPE', 'SALE')).strip().upper()
            region = "CENTRAL" if float(row.get('IGST', 0)) > 0 else "LOCAL"
            info = str(row.get('BILLINFO', '')).upper()
            dealer = "CONSUMER" if "CONSUMER" in info else "RD"
            return f"{vtype} {region} {dealer}"

        df['Particular'] = df.apply(get_particular, axis=1)
        
        # Detail is SALE or PURCHASE
        df['Detail'] = df['VTYPE'].astype(str).apply(lambda x: 'SALE' if 'SALE' in x.upper() else ('PURCHASE' if 'PUR' in x.upper() else 'OTHER'))
        
        # Calculate Tax Percentage (PTAX is usually half for local (CGST only), so we double it)
        df['TAX_PCT'] = df.apply(lambda row: row['PTAX'] * 2 if row['IGST'] == 0 else row['PTAX'], axis=1)
        
        # 4. Group By: Particular, Detail, Tax Percentage
        grouped = df.groupby(['Particular', 'Detail', 'TAX_PCT'], dropna=False).agg({
            'WT': 'sum',
            'AMOUNT': 'sum',
            'IGST': 'sum',
            'CGST': 'sum',
            'SGST': 'sum'
        }).reset_index()

        # 5. Route Taxes
        grouped['IGST OUT'] = 0.0
        grouped['CGST OUT'] = 0.0
        grouped['SGST OUT'] = 0.0
        grouped['IGST IN'] = 0.0
        grouped['CGST IN'] = 0.0
        grouped['SGST IN'] = 0.0
        
        sales_mask = grouped['Detail'] == 'SALE'
        grouped.loc[sales_mask, 'IGST OUT'] = grouped.loc[sales_mask, 'IGST']
        grouped.loc[sales_mask, 'CGST OUT'] = grouped.loc[sales_mask, 'CGST']
        grouped.loc[sales_mask, 'SGST OUT'] = grouped.loc[sales_mask, 'SGST']
        
        pur_mask = grouped['Detail'] == 'PURCHASE'
        grouped.loc[pur_mask, 'IGST IN'] = grouped.loc[pur_mask, 'IGST']
        grouped.loc[pur_mask, 'CGST IN'] = grouped.loc[pur_mask, 'CGST']
        grouped.loc[pur_mask, 'SGST IN'] = grouped.loc[pur_mask, 'SGST']
        
        # 6. Reverse-Engineer Basic Amount and Total
        # FoxPro AMOUNT is the Grand Total (Basic + Taxes)
        grouped['Total'] = grouped['AMOUNT']
        # Basic Amount = Total - Taxes
        grouped['Basic_Amount'] = grouped['Total'] - grouped['IGST'] - grouped['CGST'] - grouped['SGST']
        
        grouped = grouped.rename(columns={'TAX_PCT': '%', 'WT': 'Weight', 'Basic_Amount': 'Amount'})
        
        final_cols = ['Particular', 'Detail', '%', 'Weight', 'Amount', 
                      'IGST OUT', 'CGST OUT', 'SGST OUT', 
                      'IGST IN', 'CGST IN', 'SGST IN', 'Total']
                      
        grouped = grouped[final_cols]
        
        # Remove absolute 0 rows
        grouped = grouped[grouped['Total'] != 0]
        
        return grouped.sort_values(by=['Detail', 'Particular'], ascending=[False, True])

# Sidebar Filter
st.sidebar.header("Filter Criteria")
start_d = st.sidebar.date_input("Start Date", datetime.date(2025, 5, 1))
end_d = st.sidebar.date_input("End Date", datetime.date(2025, 5, 31))

try:
    gst_df = load_and_aggregate_gst(start_d, end_d)
    
    if gst_df.empty:
        st.warning(f"No GST transactions found between {start_d.strftime('%d/%m/%Y')} and {end_d.strftime('%d/%m/%Y')}!")
    else:
        st.success(f"Successfully replicated the FoxPro GSTR 3B Summary!")
        
        # Add FoxPro "SALE TOTAL" and "PURCHASE TOTAL" rows dynamically
        sales = gst_df[gst_df['Detail'] == 'SALE']
        purchases = gst_df[gst_df['Detail'] == 'PURCHASE']
        
        # Create a display dataframe with subtotals
        display_rows = []
        
        if not sales.empty:
            display_rows.append(sales)
            sale_tot = pd.DataFrame([{
                'Particular': 'SALE TOTAL',
                'Detail': '',
                '%': '',
                'Weight': sales['Weight'].sum(),
                'Amount': sales['Amount'].sum(),
                'IGST OUT': sales['IGST OUT'].sum(),
                'CGST OUT': sales['CGST OUT'].sum(),
                'SGST OUT': sales['SGST OUT'].sum(),
                'IGST IN': '', 'CGST IN': '', 'SGST IN': '',
                'Total': sales['Total'].sum()
            }])
            display_rows.append(sale_tot)
            display_rows.append(pd.DataFrame([{'Particular': ''}])) # Blank row
            
        if not purchases.empty:
            display_rows.append(purchases)
            pur_tot = pd.DataFrame([{
                'Particular': 'PURCHASE TOTAL',
                'Detail': '',
                '%': '',
                'Weight': purchases['Weight'].sum(),
                'Amount': purchases['Amount'].sum(),
                'IGST OUT': '', 'CGST OUT': '', 'SGST OUT': '',
                'IGST IN': purchases['IGST IN'].sum(),
                'CGST IN': purchases['CGST IN'].sum(),
                'SGST IN': purchases['SGST IN'].sum(),
                'Total': purchases['Total'].sum()
            }])
            display_rows.append(pur_tot)
            
        final_display_df = pd.concat(display_rows, ignore_index=True)
        
        # Format the numbers perfectly to match FoxPro
        def format_currency(x):
            if pd.isna(x) or x == '': return ''
            if x == 0: return ''
            return f"{float(x):.2f}"
            
        def format_weight(x):
            if pd.isna(x) or x == '': return ''
            if x == 0: return ''
            return f"{float(x):.3f}"
            
        final_display_df['%'] = final_display_df['%'].apply(lambda x: f"{float(x):.2f}" if isinstance(x, (int, float)) and x != '' else x)
        final_display_df['Weight'] = final_display_df['Weight'].apply(format_weight)
        
        for col in ['Amount', 'IGST OUT', 'CGST OUT', 'SGST OUT', 'IGST IN', 'CGST IN', 'SGST IN', 'Total']:
            final_display_df[col] = final_display_df[col].apply(format_currency)
        
        # Display Interactive Grid
        st.dataframe(
            final_display_df,
            width='stretch',
            height=500,
            hide_index=True
        )

except Exception as e:
    st.error(f"Failed to generate GST report: {e}")
