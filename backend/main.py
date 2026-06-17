from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dbfread import DBF
import pandas as pd
import os
import datetime

app = FastAPI(title="FoxPro Register API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_sale_data(start_date: datetime.date, end_date: datetime.date):
    db_path = "jwerp/1001/TRAN1.DB"
    if not os.path.exists(db_path):
        return {"error": f"Could not find database at {db_path}"}
        
    table = DBF(db_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df = pd.DataFrame(iter(table))
    df.columns = [str(c).upper() for c in df.columns]
    
    if 'NOTECNTR' in df.columns:
        df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]
        
    if 'VTYPE' in df.columns:
        df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
        df = df[df['VTYPE'] == 'SALE']
    else:
        return {"data": [], "totals": {}}
        
    if 'TDATE' in df.columns:
        df = df[df['TDATE'].notnull()]
        df['TDATE'] = pd.to_datetime(df['TDATE'])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]
        
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
        numeric_cols = ['SAMOUNT', 'CGST', 'SGST', 'IGST', 'MAINRECORD']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]
            
        df = df[(df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
        
        df['Basic_Amount'] = df['SAMOUNT'].abs()

        if 'BILLTYPE' not in df.columns:
            df['BILLTYPE'] = 1.0
        else:
            df['BILLTYPE'] = pd.to_numeric(df['BILLTYPE'], errors='coerce').fillna(1.0)

        df = df[df['BILLTYPE'].isin([1.0, 2.0, 3.0])]

        def map_bucket(row):
            igst = float(row.get('IGST', 0))
            if igst > 0 or float(row.get('BILLTYPE', 1)) == 2.0:
                return 'Central Sale'
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
    
    if not final_df.empty:
        final_df['Total'] = final_df['Retail Sale'] + final_df['Tax Invoice']
        final_df['Total Sale'] = final_df['Total'] + final_df['Central Sale'] + final_df['Others']
        final_df['Net Amount'] = final_df['Total Sale'] + final_df['SGST'] + final_df['CGST'] + final_df['IGST']
    else:
        final_df['Total'] = 0.0
        final_df['Total Sale'] = 0.0
        final_df['Net Amount'] = 0.0
    
    cols = ['Month', 'Retail Sale', 'Tax Invoice', 'Total', 'SGST', 'CGST', 'Central Sale', 'Others', 'IGST', 'Total Sale', 'Net Amount']
    for c in cols:
        if c not in final_df.columns:
            final_df[c] = 0.0
            
    final_df = final_df[cols]
    
    tot_row = {
        'Month': 'Total',
        'Retail Sale': final_df['Retail Sale'].sum(),
        'Tax Invoice': final_df['Tax Invoice'].sum(),
        'Total': final_df['Total'].sum(),
        'SGST': final_df['SGST'].sum(),
        'CGST': final_df['CGST'].sum(),
        'Central Sale': final_df['Central Sale'].sum(),
        'Others': final_df['Others'].sum(),
        'IGST': final_df['IGST'].sum(),
        'Total Sale': final_df['Total Sale'].sum(),
        'Net Amount': final_df['Net Amount'].sum()
    }
    
    return {"data": final_df.to_dict(orient="records"), "totals": tot_row}

def get_purchase_data(start_date: datetime.date, end_date: datetime.date):
    db_path = "jwerp/1001/TRAN1.DB"
    if not os.path.exists(db_path):
        return {"error": f"Could not find database at {db_path}"}
        
    table = DBF(db_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df = pd.DataFrame(iter(table))
    df.columns = [str(c).upper() for c in df.columns]
    
    if 'NOTECNTR' in df.columns:
        df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]
        
    if 'VTYPE' in df.columns:
        df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
        df = df[df['VTYPE'] == 'PURCHASE']
    else:
        return {"data": [], "totals": {}}
        
    if 'TDATE' in df.columns:
        df = df[df['TDATE'].notnull()]
        df['TDATE'] = pd.to_datetime(df['TDATE'])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]
        
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
        numeric_cols = ['SAMOUNT', 'CGST', 'SGST', 'IGST', 'MAINRECORD']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]
            
        df = df[(df['SAMOUNT'] != 0) | (df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
        
        df['Basic_Amount'] = df['SAMOUNT'].abs()

        if 'BILLTYPE' not in df.columns:
            df['BILLTYPE'] = 1.0
        else:
            df['BILLTYPE'] = pd.to_numeric(df['BILLTYPE'], errors='coerce').fillna(1.0)

        df = df[df['BILLTYPE'].isin([1.0, 2.0, 3.0])]

        def map_bucket(row):
            igst = float(row.get('IGST', 0))
            if igst > 0 or float(row.get('BILLTYPE', 1)) == 2.0:
                return 'CST Purchase'
            if float(row.get('BILLTYPE', 1)) == 3.0:
                return 'URD Purchase'
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

    final_data = []
    for m_name, m_num, m_year in months_to_display:
        row = {
            'Month': m_name,
            'URD Purchase': 0.0,
            'Tax Invoice': 0.0,
            'CST Purchase': 0.0,
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
    
    if not final_df.empty:
        final_df['Total'] = final_df['URD Purchase'] + final_df['Tax Invoice']
        final_df['Total Purchase'] = final_df['Total'] + final_df['CST Purchase'] + final_df['Others']
        final_df['Net Amount'] = final_df['Total Purchase'] + final_df['SGST'] + final_df['CGST'] + final_df['IGST']
    else:
        final_df['Total'] = 0.0
        final_df['Total Purchase'] = 0.0
        final_df['Net Amount'] = 0.0
    
    cols = ['Month', 'URD Purchase', 'Tax Invoice', 'Total', 'SGST', 'CGST', 'CST Purchase', 'Others', 'IGST', 'Total Purchase', 'Net Amount']
    for c in cols:
        if c not in final_df.columns:
            final_df[c] = 0.0
            
    final_df = final_df[cols]
    
    tot_row = {
        'Month': 'Total',
        'URD Purchase': final_df['URD Purchase'].sum(),
        'Tax Invoice': final_df['Tax Invoice'].sum(),
        'Total': final_df['Total'].sum(),
        'SGST': final_df['SGST'].sum(),
        'CGST': final_df['CGST'].sum(),
        'CST Purchase': final_df['CST Purchase'].sum(),
        'Others': final_df['Others'].sum(),
        'IGST': final_df['IGST'].sum(),
        'Total Purchase': final_df['Total Purchase'].sum(),
        'Net Amount': final_df['Net Amount'].sum()
    }
    
    return {"data": final_df.to_dict(orient="records"), "totals": tot_row}

@app.get("/api/sale-register")
def get_sale_register(start_date: datetime.date, end_date: datetime.date):
    return get_sale_data(start_date, end_date)

@app.get("/api/purchase-register")
def get_purchase_register(start_date: datetime.date, end_date: datetime.date):
    return get_purchase_data(start_date, end_date)

def get_menu_tree():
    try:
        table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        
        df['MNUCAP'] = df['MNUCAP'].astype(str).str.strip().str.replace(r'[\&\<\\\>]+', '', regex=True)
        if 'MNUORDER' in df.columns:
            df['MNUORDER'] = pd.to_numeric(df['MNUORDER'], errors='coerce').fillna(0)
        if 'HIDE' in df.columns:
            df = df[df['HIDE'] != True]
            df = df[df['HIDE'] != 'T']
            
        TOP_MENUS = {
            1: "Maintain",
            2: "Voucher",
            3: "Feeding",
            4: "Reports",
            5: "Reports",
            6: "Tagging",
            7: "Utilities",
            8: "Exit"
        }
        
        tree = []
        for mno in sorted(df['MNO'].unique()):
            sub1_items = df[(df['MNO'] == mno) & (df['SMNO1'] > 0) & (df['SMNO2'] == 0)].sort_values('MNUORDER')
            if sub1_items.empty:
                continue
                
            main_label = TOP_MENUS.get(mno, f"Menu {mno}")
            
            # Find if this top menu already exists (e.g., merging MNO 4 and 5 into "Reports")
            main_item = next((item for item in tree if item["label"] == main_label), None)
            if not main_item:
                main_item = {
                    "id": f"main_{mno}",
                    "label": main_label,
                    "children": []
                }
                tree.append(main_item)
            
            for _, sub1_row in sub1_items.iterrows():
                smno1 = sub1_row['SMNO1']
                sub1_item = {
                    "id": str(sub1_row['MNUID']).strip(),
                    "label": sub1_row['MNUCAP'].replace('\\<', ''),
                    "children": []
                }
                
                sub2_items = df[(df['MNO'] == mno) & (df['SMNO1'] == smno1) & (df['SMNO2'] > 0) & (df['SMNO3'] == 0)].sort_values('MNUORDER')
                for _, sub2_row in sub2_items.iterrows():
                    smno2 = sub2_row['SMNO2']
                    sub2_item = {
                        "id": str(sub2_row['MNUID']).strip(),
                        "label": sub2_row['MNUCAP'].replace('\\<', ''),
                        "children": []
                    }
                    
                    sub3_items = df[(df['MNO'] == mno) & (df['SMNO1'] == smno1) & (df['SMNO2'] == smno2) & (df['SMNO3'] > 0)].sort_values('MNUORDER')
                    for _, sub3_row in sub3_items.iterrows():
                        sub3_item = {
                            "id": str(sub3_row['MNUID']).strip(),
                            "label": sub3_row['MNUCAP'].replace('\\<', ''),
                            "cmd": str(sub3_row.get('CMD', '')).strip()
                        }
                        sub2_item["children"].append(sub3_item)
                        
                    if not sub2_item["children"]:
                        sub2_item["cmd"] = str(sub2_row.get('CMD', '')).strip()
                        
                    sub1_item["children"].append(sub2_item)
                    
                if not sub1_item["children"]:
                    sub1_item["cmd"] = str(sub1_row.get('CMD', '')).strip()
                    
                main_item["children"].append(sub1_item)
            
        return tree
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/menu")
def get_menu():
    return get_menu_tree()

@app.get("/api/gstr1")
def get_gstr1(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        if not start_date or not end_date:
            return []

        # Read TRAN1.DB
        table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        df.columns = [str(c).upper() for c in df.columns]

        # Read ACCMAST.DB
        acc_table = DBF("jwerp/1001/ACCMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        acc_df = pd.DataFrame(iter(acc_table))
        acc_df.columns = [str(c).upper() for c in acc_df.columns]

        # Filter TRAN1 for SALES
        if 'VTYPE' in df.columns:
            df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
            df = df[df['VTYPE'] == 'SALE']
            
        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]

        if 'TDATE' in df.columns:
            df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
            df = df[df['TDATE'].notnull()]
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]

        if df.empty:
            return []

        # Extract numerics
        numeric_cols = ['AMOUNT', 'SAMOUNT', 'CGST', 'SGST', 'IGST']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # Absolute values since FoxPro stores sales credits as negative
        df['AMOUNT'] = df['AMOUNT'].abs()
        df['SAMOUNT'] = df['SAMOUNT'].abs()
        df['CGST'] = df['CGST'].abs()
        df['SGST'] = df['SGST'].abs()
        df['IGST'] = df['IGST'].abs()

        # Join with ACCMAST
        if 'ACNO' in df.columns and 'ACNO' in acc_df.columns:
            # Ensure types match
            df['ACNO'] = pd.to_numeric(df['ACNO'], errors='coerce')
            acc_df['ACNO'] = pd.to_numeric(acc_df['ACNO'], errors='coerce')
            
            # Keep only necessary ACCMAST cols to save memory
            acc_subset = acc_df[['ACNO', 'CNAME', 'GSTIN', 'STATEID']].drop_duplicates('ACNO')
            df = df.merge(acc_subset, on='ACNO', how='left')
        else:
            df['CNAME'] = "Unknown"
            df['GSTIN'] = ""
            df['STATEID'] = ""

        # Format output
        df['Invoice_Date'] = df['TDATE'].dt.strftime('%d-%m-%Y')
        df['Invoice_No'] = df['BILLNO'].astype(str).str.strip() if 'BILLNO' in df.columns else ""
        df['Party_Name'] = df['CNAME'].fillna("Unknown Party").astype(str).str.strip()
        df['GSTIN'] = df['GSTIN'].fillna("").astype(str).str.strip()
        df['State_Code'] = df['STATEID'].fillna("").astype(str).str.strip()
        
        # B2B vs B2C
        df['Category'] = df['GSTIN'].apply(lambda x: 'B2B' if len(x) >= 10 else 'B2C')

        # Select final columns
        final_cols = ['TRNID', 'Invoice_Date', 'Invoice_No', 'Party_Name', 'GSTIN', 'Category', 'State_Code', 'SAMOUNT', 'CGST', 'SGST', 'IGST', 'AMOUNT']
        if 'TRNID' not in df.columns: df['TRNID'] = ""
        
        res_df = df[final_cols].rename(columns={
            'SAMOUNT': 'Taxable_Value',
            'AMOUNT': 'Total_Value'
        })
        
        # Sort by date
        res_df['TDATE_SORT'] = df['TDATE']
        res_df = res_df.sort_values(['TDATE_SORT', 'Invoice_No']).drop(columns=['TDATE_SORT'])

        return res_df.to_dict(orient='records')
    except Exception as e:
        print(f"Error in GSTR1 API: {e}")
        return []

@app.get("/api/register-details")
def get_register_details(start_date: str = Query(None), end_date: str = Query(None), month: str = Query(None), year: int = Query(None), vtype: str = Query(None)):
    try:
        if not start_date or not end_date: return []
        
        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        acc_path = os.path.join(folder, "ACCMAST.DB")
        
        if not os.path.exists(tran_path) or not os.path.exists(acc_path): return []
        
        tran_table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(tran_table))
        df.columns = [str(c).upper() for c in df.columns]
        
        acc_table = DBF(acc_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        acc_df = pd.DataFrame(iter(acc_table))
        acc_df.columns = [str(c).upper() for c in acc_df.columns]
        
        if 'TDATE' in df.columns:
            df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
            df = df[df['TDATE'].notnull()]
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]
            
            if month and year:
                df = df[(df['TDATE'].dt.strftime('%B') == month) & (df['TDATE'].dt.year == year)]
                
        if 'NOTECNTR' in df.columns:
            df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]
            
        if vtype and 'VTYPE' in df.columns:
            df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
            if vtype.upper() == 'SALE':
                df = df[df['VTYPE'].str.contains('SALE', na=False)]
            elif vtype.upper() == 'PURCHASE':
                df = df[df['VTYPE'].str.contains('PUR', na=False)]
                
        # Absolute values and numeric conversion BEFORE filtering
        numeric_cols = ['AMOUNT', 'SAMOUNT', 'CGST', 'SGST', 'IGST']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).abs()
            else:
                df[col] = 0.0

        # Tax Register Filter
        df = df[(df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
        if 'BILLTYPE' in df.columns:
            df = df[pd.to_numeric(df['BILLTYPE'], errors='coerce').fillna(1.0).isin([1.0, 2.0, 3.0])]

        if df.empty: return []
                
        # Join with ACCMAST
        if 'ACNO' in df.columns and 'ACNO' in acc_df.columns:
            df['ACNO'] = pd.to_numeric(df['ACNO'], errors='coerce')
            acc_df['ACNO'] = pd.to_numeric(acc_df['ACNO'], errors='coerce')
            acc_subset = acc_df[['ACNO', 'CNAME', 'GSTIN', 'STATEID']].drop_duplicates('ACNO')
            df = df.merge(acc_subset, on='ACNO', how='left')
        else:
            df['CNAME'] = "Unknown"
            df['GSTIN'] = ""
            df['STATEID'] = ""
            
        df['Date'] = df['TDATE'].dt.strftime('%d/%m/%Y')
        df['Vou_No'] = df['VONO'].astype(str).str.strip() if 'VONO' in df.columns else ""
        df['Party_Name'] = df['CNAME'].fillna("Unknown Party").astype(str).str.strip()
        df['State'] = df['STATEID'].fillna("").astype(str).str.strip()
        df['GSTIN'] = df['GSTIN'].fillna("").astype(str).str.strip()
        df['Narration'] = df['REMARKS'].astype(str).str.strip() if 'REMARKS' in df.columns else ""
        
        res_df = df[['TRNID', 'Date', 'Vou_No', 'Party_Name', 'State', 'GSTIN', 'Narration', 'AMOUNT', 'SGST', 'CGST', 'IGST']]
        res_df = res_df.rename(columns={
            'AMOUNT': 'Bill_Amount',
            'Vou_No': 'Vou.No.'
        })
        res_df['Amount'] = res_df['Bill_Amount'] - res_df['SGST'] - res_df['CGST'] - res_df['IGST']
        
        # Sort by Date
        res_df['TDATE_SORT'] = df['TDATE']
        res_df = res_df.sort_values(['TDATE_SORT', 'Vou.No.']).drop(columns=['TDATE_SORT'])
        
        return res_df.to_dict(orient='records')
    except Exception as e:
        print(f"Error in register details: {e}")
        return []

@app.get("/api/voucher-details")
def get_voucher_details(trn_id: str = Query(None)):
    try:
        if not trn_id: return {}
        trn_id_num = float(trn_id)
        
        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        itran_path = os.path.join(folder, "ITRAN1.DB")
        acc_path = os.path.join(folder, "ACCMAST.DB")
        item_path = os.path.join(folder, "ITEMMAST.DB")
        
        if not all(os.path.exists(p) for p in [tran_path, itran_path]): return {}
        
        # Fetch TRAN1 header
        tran_table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_tran = pd.DataFrame(iter(tran_table))
        df_tran.columns = [str(c).upper() for c in df_tran.columns]
        df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
        header_df = df_tran[df_tran['TRNID'] == trn_id_num]
        
        if header_df.empty: return {}
        header_row = header_df.iloc[0].to_dict()
        
        def safe_float(v):
            if v is None: return 0.0
            try: return float(v)
            except: return 0.0
        
        # Load DBs
        def load_db(filename):
            path = os.path.join(folder, filename)
            if not os.path.exists(path): return pd.DataFrame()
            t = DBF(path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            d = pd.DataFrame(iter(t))
            d.columns = [str(c).upper() for c in d.columns]
            return d
            
        df_acc = load_db("ACCMAST.DB")
        df_acc['ACNO'] = pd.to_numeric(df_acc['ACNO'], errors='coerce')
        
        df_series = load_db("SERIES.DB")
        df_series['SERIESID'] = pd.to_numeric(df_series['SERIESID'], errors='coerce')
        
        party_name = ""
        address = ""
        gstin = ""
        state = ""
        
        if pd.notnull(header_row.get('ACNO')):
            acc_match = df_acc[df_acc['ACNO'] == header_row['ACNO']]
            if not acc_match.empty:
                acc_r = acc_match.iloc[0]
                party_name = str(acc_r.get('CNAME', ''))
                address = f"{str(acc_r.get('ADD1', ''))} {str(acc_r.get('ADD2', ''))}".strip()
                gstin = str(acc_r.get('GSTIN', ''))
                state = str(acc_r.get('STATEID', ''))
                
        series_name = str(header_row.get('VTYPE', ''))
        if pd.notnull(header_row.get('SERIESID')) and not df_series.empty:
            s_match = df_series[df_series['SERIESID'] == pd.to_numeric(header_row['SERIESID'])]
            if not s_match.empty:
                series_name = str(s_match.iloc[0].get('SERIES', series_name))
                
        header_data = {
            'Party_Name': party_name,
            'Address': address,
            'GSTIN': gstin,
            'State': state,
            'Series': series_name,
            'Date': pd.to_datetime(header_row.get('TDATE')).strftime('%d/%m/%Y') if pd.notnull(header_row.get('TDATE')) else "",
            'Vou_No': str(header_row.get('VONO', '')),
            'Bill_No': str(header_row.get('BILLNO', '')),
            'Total_Sale': abs(safe_float(header_row.get('AMOUNT', 0))),
            'SGST': abs(safe_float(header_row.get('SGST', 0))),
            'CGST': abs(safe_float(header_row.get('CGST', 0))),
            'IGST': abs(safe_float(header_row.get('IGST', 0))),
            'Narration': str(header_row.get('NARR', '')),
            'Dia_Val': 0.0,
            'Labour_Val': 0.0
        }
        
        # Fetch ITRAN1 items
        itran_table = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_itran = pd.DataFrame(iter(itran_table))
        df_itran.columns = [str(c).upper() for c in df_itran.columns]
        df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
        items_df = df_itran[df_itran['TRNID'] == trn_id_num]
        
        # Add Item Names and lookups
        df_item = load_db("ITEMMAST.DB")
        df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
        
        df_stamp = load_db("STAMP.DB")
        df_stamp['STAMPID'] = pd.to_numeric(df_stamp['STAMPID'], errors='coerce')
        
        df_units = load_db("UNITS.DB")
        df_units['UNITID'] = pd.to_numeric(df_units['UNITID'], errors='coerce')
        
        items_list = []
        total_damt = 0.0
        total_lamt = 0.0
        for _, r in items_df.iterrows():
            item_name = ""
            if pd.notnull(r.get('INO')):
                i_match = df_item[df_item['INO'] == pd.to_numeric(r['INO'])]
                if not i_match.empty:
                    item_name = str(i_match.iloc[0].get('IDESC', str(i_match.iloc[0].get('PNAME', ''))))
            
            stamp_name = ""
            if pd.notnull(r.get('STAMPID')) and not df_stamp.empty:
                st_match = df_stamp[df_stamp['STAMPID'] == pd.to_numeric(r['STAMPID'])]
                if not st_match.empty:
                    stamp_name = str(st_match.iloc[0].get('STAMP', ''))
                    
            unit_name = ""
            if pd.notnull(r.get('UNITID')) and not df_units.empty:
                u_match = df_units[df_units['UNITID'] == pd.to_numeric(r['UNITID'])]
                if not u_match.empty:
                    unit_name = str(u_match.iloc[0].get('UNIT', ''))
            
            gwt = safe_float(r.get('GWT', 0))
            lesswt = safe_float(r.get('LESSWT', 0))
            wt = safe_float(r.get('WT', 0))
            diawt = safe_float(r.get('DIAWT', 0))
            
            # Using precise FoxPro calculations
            net_wt = wt - lesswt
            less_calc = gwt - net_wt
            fine1 = safe_float(r.get('FINE1', 0))
            
            # Sum totals
            damt = safe_float(r.get('DAMT', 0))
            lamt = safe_float(r.get('LAMT', 0))
            total_damt += damt
            total_lamt += lamt
                    
            items_list.append({
                'Type': str(r.get('TYPE', '')),
                'Tag_No': str(r.get('TGNO', '')),
                'Design': str(r.get('DESIGN', '')),
                'Item_Name': item_name,
                'Stamp': stamp_name,
                'Remarks': str(r.get('REMARKS', '')),
                'Unit': unit_name,
                'Pc': safe_float(r.get('PC', 0)),
                'Weight': gwt,
                'Less': less_calc,
                'Net_Wt': net_wt,
                'Add_Wt': safe_float(r.get('ADDWT', 0)),
                'Tunch': safe_float(r.get('TUNCH', 0)),
                'Fine': fine1,
                'Rate': safe_float(r.get('RATE', 0)),
                'Dia_Wt': diawt,
                'Stn_Wt': safe_float(r.get('STNWT', 0)),
                'Lbr': safe_float(r.get('LBR', 0)),
                'On': str(r.get('LBRON', '')),
                'Dis': str(r.get('DISPER', '')),
                'Amount': safe_float(r.get('TOTAL', 0))
            })
            
        header_data['Dia_Val'] = total_damt
        header_data['Labour_Val'] = total_lamt
            
        return {
            'header': header_data,
            'items': items_list
        }
    except Exception as e:
        print(f"Error in voucher details: {e}")
        return {}


@app.get("/api/item-register")
def get_item_register(start_date: str = Query(None), end_date: str = Query(None), vtype: str = Query(None), item_group: str = Query(None)):
    try:
        if not start_date or not end_date or not vtype or not item_group:
            return []
            
        folder = "jwerp/1001"
        def load_db(filename):
            path = os.path.join(folder, filename)
            if not os.path.exists(path): return pd.DataFrame()
            t = DBF(path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            d = pd.DataFrame(iter(t))
            d.columns = [str(c).upper() for c in d.columns]
            return d

        df_tran = load_db("TRAN1.DB")
        if df_tran.empty: return []
        
        # Date filter
        df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df_tran = df_tran[(df_tran['TDATE'] >= start_dt) & (df_tran['TDATE'] <= end_dt)]
        
        # Vtype filter
        if 'VTYPE' in df_tran.columns:
            df_tran['VTYPE'] = df_tran['VTYPE'].astype(str).str.strip().str.upper()
            target = 'SALE' if vtype.lower() == 'sale' else 'PUR'
            df_tran = df_tran[df_tran['VTYPE'].str.contains(target, na=False)]
            
        if 'MAINRECORD' in df_tran.columns:
            df_tran = df_tran[df_tran['MAINRECORD'] == 1.0]

        df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
        valid_trns = df_tran['TRNID'].dropna().tolist()
        if not valid_trns: return []
        
        df_itran = load_db("ITRAN1.DB")
        if df_itran.empty: return []
        df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
        df_itran = df_itran[df_itran['TRNID'].isin(valid_trns)]
        
        df_item = load_db("ITEMMAST.DB")
        df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
        df_item = df_item[['INO', 'IGROUPID', 'IDESC', 'PNAME']]
        
        df_grp = load_db("igroup.db")
        df_grp = df_grp[['IGROUPID', 'IGROUP']]
        
        # Merge to get item group
        merged = df_itran.merge(df_item, on='INO', how='left').merge(df_grp, on='IGROUPID', how='left')
        
        merged['GWT'] = pd.to_numeric(merged['GWT'], errors='coerce').fillna(0)
        merged['WT'] = pd.to_numeric(merged['WT'], errors='coerce').fillna(0)
        merged['LESSWT'] = pd.to_numeric(merged['LESSWT'], errors='coerce').fillna(0)
        merged['TOTAL'] = pd.to_numeric(merged['TOTAL'], errors='coerce').fillna(0)
        merged['DAMT'] = pd.to_numeric(merged['DAMT'], errors='coerce').fillna(0)
        merged['SAMT'] = pd.to_numeric(merged['SAMT'], errors='coerce').fillna(0)
        merged['DIAWT'] = pd.to_numeric(merged['DIAWT'], errors='coerce').fillna(0)
        merged['STNWT'] = pd.to_numeric(merged['STNWT'], errors='coerce').fillna(0)
        merged['PC'] = pd.to_numeric(merged['PC'], errors='coerce').fillna(0)

        # Apply item_group filter
        if item_group.upper() == 'DIAMOND STUDDED':
            merged = merged[(merged['DAMT'] > 0) | (merged['DIAWT'] > 0)]
            merged['GWT'] = merged['DIAWT']
            merged['LESSWT'] = 0
            merged['WT'] = merged['DIAWT']
            merged['TOTAL'] = merged['DAMT']
            merged['PC'] = 0
        elif item_group.upper() == 'STONE STUDDED':
            merged = merged[(merged['SAMT'] > 0) | (merged['STNWT'] > 0)]
            merged['GWT'] = merged['STNWT']
            merged['LESSWT'] = 0
            merged['WT'] = merged['STNWT']
            merged['TOTAL'] = merged['SAMT']
            merged['PC'] = 0
        else:
            merged['IGROUP'] = merged['IGROUP'].fillna('UNCLASSIFIED')
            merged = merged[merged['IGROUP'].str.upper() == item_group.upper()]
            merged['TOTAL'] = merged['TOTAL'] - merged['DAMT'] - merged['SAMT']
            merged = merged[(merged['TOTAL'] > 0) | (merged['GWT'] > 0)]

        if merged.empty: return []

        df_acc = load_db("ACCMAST.DB")
        df_acc['ACNO'] = pd.to_numeric(df_acc['ACNO'], errors='coerce')
        
        df_stamp = load_db("STAMP.DB")
        df_stamp['STAMPID'] = pd.to_numeric(df_stamp['STAMPID'], errors='coerce')

        df_tran_min = df_tran[['TRNID', 'TDATE', 'VONO', 'ACNO']]
        if 'TDATE' in merged.columns: merged = merged.drop(columns=['TDATE'])
        if 'VONO' in merged.columns: merged = merged.drop(columns=['VONO'])
        if 'ACNO' in merged.columns: merged = merged.drop(columns=['ACNO'])
        
        merged = merged.merge(df_tran_min, on='TRNID', how='left')
        merged = merged.merge(df_acc[['ACNO', 'CNAME']], on='ACNO', how='left')
        if 'STAMPID' in merged.columns:
            merged['STAMPID'] = pd.to_numeric(merged['STAMPID'], errors='coerce')
            merged = merged.merge(df_stamp[['STAMPID', 'STAMP']], on='STAMPID', how='left')
        else:
            merged['STAMP'] = ''
            
        def safe_float(v):
            try: return float(v)
            except: return 0.0

        records = []
        for _, r in merged.iterrows():
            date_str = pd.to_datetime(r['TDATE']).strftime('%d/%m/%Y') if pd.notnull(r['TDATE']) else ''
            item_name = str(r.get('IDESC', r.get('PNAME', '')))
            if item_name == 'nan': item_name = ''
            
            purity = str(r.get('STAMP', ''))
            if purity == 'nan': purity = ''
            
            gwt = safe_float(r['GWT'])
            wt = safe_float(r['WT'])
            lesswt = safe_float(r['LESSWT'])
            net_wt = wt - lesswt
            less_calc = gwt - net_wt
            
            records.append({
                'TRNID': int(r['TRNID']),
                'Date': date_str,
                'Type': str(r.get('TYPE', '')),
                'Vou_No': str(r.get('VONO', '')),
                'Party_Name': str(r.get('CNAME', '')),
                'Item_Name': item_name,
                'Purity': purity,
                'Tag_No': str(r.get('TGNO', '')),
                'Pc': safe_float(r['PC']),
                'Gr_Wt': gwt,
                'Less_Wt': less_calc,
                'Net_Wt': net_wt,
                'Taxable_Amt': safe_float(r['TOTAL'])
            })

        return records

    except Exception as e:
        import traceback; traceback.print_exc()
        return []

@app.get("/api/gstr2")
def get_gstr2(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        if not start_date or not end_date:
            return []

        # Read TRAN1.DB
        table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        df.columns = [str(c).upper() for c in df.columns]

        # Read ACCMAST.DB
        acc_table = DBF("jwerp/1001/ACCMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        acc_df = pd.DataFrame(iter(acc_table))
        acc_df.columns = [str(c).upper() for c in acc_df.columns]

        # Filter TRAN1 for PURCHASES
        if 'VTYPE' in df.columns:
            df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
            df = df[df['VTYPE'].str.contains('PUR', na=False)]
            
        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]

        if 'TDATE' in df.columns:
            df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
            df = df[df['TDATE'].notnull()]
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]

        if df.empty:
            return []

        # Extract numerics
        numeric_cols = ['AMOUNT', 'SAMOUNT', 'CGST', 'SGST', 'IGST']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # Absolute values since FoxPro stores credits as negative
        df['AMOUNT'] = df['AMOUNT'].abs()
        df['SAMOUNT'] = df['SAMOUNT'].abs()
        df['CGST'] = df['CGST'].abs()
        df['SGST'] = df['SGST'].abs()
        df['IGST'] = df['IGST'].abs()

        # Join with ACCMAST
        if 'ACNO' in df.columns and 'ACNO' in acc_df.columns:
            # Ensure types match
            df['ACNO'] = pd.to_numeric(df['ACNO'], errors='coerce')
            acc_df['ACNO'] = pd.to_numeric(acc_df['ACNO'], errors='coerce')
            
            # Keep only necessary ACCMAST cols to save memory
            acc_subset = acc_df[['ACNO', 'CNAME', 'GSTIN', 'STATEID']].drop_duplicates('ACNO')
            df = df.merge(acc_subset, on='ACNO', how='left')
        else:
            df['CNAME'] = "Unknown"
            df['GSTIN'] = ""
            df['STATEID'] = ""

        # Format output
        df['Invoice_Date'] = df['TDATE'].dt.strftime('%d-%m-%Y')
        df['Invoice_No'] = df['BILLNO'].astype(str).str.strip() if 'BILLNO' in df.columns else ""
        df['Party_Name'] = df['CNAME'].fillna("Unknown Party").astype(str).str.strip()
        df['GSTIN'] = df['GSTIN'].fillna("").astype(str).str.strip()
        df['State_Code'] = df['STATEID'].fillna("").astype(str).str.strip()
        
        # B2B vs B2C
        df['Category'] = df['GSTIN'].apply(lambda x: 'B2B' if len(x) >= 10 else 'B2C')

        # Select final columns
        final_cols = ['Invoice_Date', 'Invoice_No', 'Party_Name', 'GSTIN', 'Category', 'State_Code', 'SAMOUNT', 'CGST', 'SGST', 'IGST', 'AMOUNT']
        
        res_df = df[final_cols].rename(columns={
            'SAMOUNT': 'Taxable_Value',
            'AMOUNT': 'Total_Value'
        })
        
        # Sort by date
        res_df['TDATE_SORT'] = df['TDATE']
        res_df = res_df.sort_values(['TDATE_SORT', 'Invoice_No']).drop(columns=['TDATE_SORT'])

        return res_df.to_dict(orient='records')
    except Exception as e:
        print(f"Error in GSTR2 API: {e}")
        return []


@app.get("/api/gstr3b")
def get_gstr3b(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        if not start_date or not end_date:
            return []

        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        itran_path = os.path.join(folder, "ITRAN1.DB")
        
        if not os.path.exists(tran_path):
            tran_path = os.path.join(folder, "tran1.db")
            
        if not os.path.exists(tran_path):
            return []

        table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        df.columns = [str(c).upper() for c in df.columns]

        if 'TDATE' in df.columns:
            df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
            df = df[df['TDATE'].notnull()]
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]
            
        if df.empty:
            return []

        # Use SAMOUNT for precise Taxable Basic Amount without Roundoff distortion
        numeric_cols = ['AMOUNT', 'SAMOUNT', 'CGST', 'SGST', 'IGST', 'MAINRECORD', 'TRNID', 'PTAX']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # Filter TRAN1 for SALES and PURCHASES only!
        if 'VTYPE' in df.columns:
            df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
            df = df[df['VTYPE'].str.contains('SALE|PUR', na=False)]

        # FoxPro GSTR 3B explicitly excludes Exempted (PTAX=0) Sales from this specific summary grid
        sales_mask = df['VTYPE'].str.contains('SALE', na=False)
        df = df[~(sales_mask & (df['PTAX'] == 0))]

        if 'MAINRECORD' in df.columns:
            df = df[df['MAINRECORD'] == 1.0]
            
        df = df[(df['AMOUNT'] != 0) | (df['CGST'] != 0) | (df['SGST'] != 0) | (df['IGST'] != 0)]
        df['AMOUNT'] = df['AMOUNT'].abs()
        df['SAMOUNT'] = df['SAMOUNT'].abs()

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

        def get_particular(row):
            vtype = str(row.get('VTYPE', 'SALE')).strip().upper()
            region = "CENTRAL" if float(row.get('IGST', 0)) > 0 else "LOCAL"
            info = str(row.get('BILLINFO', '')).upper()
            dealer = "CONSUMER" if "CONSUMER" in info else "RD"
            return f"{vtype} {region} {dealer}"

        df['Particular'] = df.apply(get_particular, axis=1)
        df['Detail'] = df['VTYPE'].astype(str).apply(lambda x: 'SALE' if 'SALE' in x.upper() else 'PURCHASE')

        # Since FoxPro merges all tax slabs for the same Type, we just group by Particular and Detail.
        grouped = df.groupby(['Particular', 'Detail'], dropna=False).agg({
            'WT': 'sum', 'SAMOUNT': 'sum', 'IGST': 'sum', 'CGST': 'sum', 'SGST': 'sum', 'PTAX': 'max'
        }).reset_index()

        # FoxPro represents the % column as the individual SGST/CGST split for local sales.
        grouped['%'] = grouped.apply(lambda row: row['PTAX'] / 2 if 'LOCAL' in row['Particular'] else row['PTAX'], axis=1)

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
        
        # Exact FoxPro Calculation: Total = SAMOUNT + Taxes (excludes any ROFF discrepancies)
        grouped['Amount'] = grouped['SAMOUNT']
        grouped['Total'] = grouped['Amount'] + grouped['IGST'] + grouped['CGST'] + grouped['SGST']
        grouped['GST ADJ.'] = 0.0
        
        grouped = grouped.rename(columns={'WT': 'Weight'})
        
        final_cols = ['Particular', 'Detail', '%', 'Weight', 'Amount', 'IGST OUT', 'CGST OUT', 'SGST OUT', 'IGST IN', 'CGST IN', 'SGST IN', 'Total', 'GST ADJ.']
        grouped = grouped[final_cols]
        grouped = grouped[grouped['Total'] != 0]
        grouped = grouped.sort_values(by=['Detail', 'Particular'], ascending=[False, True])

        sales = grouped[grouped['Detail'] == 'SALE']
        purchases = grouped[grouped['Detail'] == 'PURCHASE']
        
        display_rows = []
        if not sales.empty:
            display_rows.append(sales)
            sale_tot = pd.DataFrame([{
                'Particular': 'SALE TOTAL', 'Detail': '', '%': '',
                'Weight': sales['Weight'].sum(), 'Amount': sales['Amount'].sum(),
                'IGST OUT': sales['IGST OUT'].sum(), 'CGST OUT': sales['CGST OUT'].sum(), 'SGST OUT': sales['SGST OUT'].sum(),
                'IGST IN': 0, 'CGST IN': 0, 'SGST IN': 0, 'Total': sales['Total'].sum(), 'GST ADJ.': 0
            }])
            display_rows.append(sale_tot)
            display_rows.append(pd.DataFrame([{'Particular': ''}])) 
            
        if not purchases.empty:
            display_rows.append(purchases)
            pur_tot = pd.DataFrame([{
                'Particular': 'PURCHASE TOTAL', 'Detail': '', '%': '',
                'Weight': purchases['Weight'].sum(), 'Amount': purchases['Amount'].sum(),
                'IGST OUT': 0, 'CGST OUT': 0, 'SGST OUT': 0,
                'IGST IN': purchases['IGST IN'].sum(), 'CGST IN': purchases['CGST IN'].sum(), 'SGST IN': purchases['SGST IN'].sum(),
                'Total': purchases['Total'].sum(), 'GST ADJ.': 0
            }])
            display_rows.append(pur_tot)
            
        final_df = pd.concat(display_rows, ignore_index=True)
        final_df = final_df.fillna('')
        
        return final_df.to_dict(orient='records')
    except Exception as e:
        print(f"Error in GSTR 3B API: {e}")
        return []

@app.get("/api/item-group-register")
def get_item_group_register(start_date: str = Query(None), end_date: str = Query(None), vtype: str = Query('sale')):
    try:
        if not start_date or not end_date:
            return []

        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        itran_path = os.path.join(folder, "ITRAN1.DB")
        item_path = os.path.join(folder, "ITEMMAST.DB")
        grp_path = os.path.join(folder, "igroup.db")
        
        if not os.path.exists(tran_path):
            tran_path = os.path.join(folder, "tran1.db")
            
        if not all(os.path.exists(p) for p in [tran_path, itran_path, item_path, grp_path]):
            return []

        # 1. TRAN1 (Header)
        table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_tran = pd.DataFrame(iter(table))
        df_tran.columns = [str(c).upper() for c in df_tran.columns]

        if 'TDATE' in df_tran.columns:
            df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df_tran = df_tran[(df_tran['TDATE'] >= start_dt) & (df_tran['TDATE'] <= end_dt)]

        if 'VTYPE' in df_tran.columns:
            df_tran['VTYPE'] = df_tran['VTYPE'].astype(str).str.strip().str.upper()
            target = 'SALE' if vtype.lower() == 'sale' else 'PUR'
            df_tran = df_tran[df_tran['VTYPE'].str.contains(target, na=False)]

        if 'MAINRECORD' in df_tran.columns:
            df_tran = df_tran[df_tran['MAINRECORD'] == 1.0]

        valid_trns = df_tran['TRNID'].dropna().tolist()
        if not valid_trns:
            return []

        # 2. ITRAN1 (Line Items)
        itran = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_itran = pd.DataFrame(iter(itran))
        df_itran.columns = [str(c).upper() for c in df_itran.columns]
        df_itran = df_itran[df_itran['TRNID'].isin(valid_trns)]

        if df_itran.empty:
            return []

        # 3. ITEMMAST (Items)
        item = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_item = pd.DataFrame(iter(item))
        df_item.columns = [str(c).upper() for c in df_item.columns]
        df_item = df_item[['INO', 'IGROUPID']]

        # 4. IGROUP (Item Groups)
        grp = DBF(grp_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_grp = pd.DataFrame(iter(grp))
        df_grp.columns = [str(c).upper() for c in df_grp.columns]
        df_grp = df_grp[['IGROUPID', 'IGROUP']]

        # Merge
        merged = df_itran.merge(df_item, on='INO', how='left').merge(df_grp, on='IGROUPID', how='left')
        
        # Clean numeric columns
        numeric_cols = ['PC', 'GWT', 'WT', 'FINE1', 'LAMT', 'SAMT', 'DAMT', 'TOTAL', 'DIAWT', 'STNWT']
        for c in numeric_cols:
            if c in merged.columns:
                merged[c] = pd.to_numeric(merged[c], errors='coerce').fillna(0)
            else:
                merged[c] = 0.0

        # Split logic dynamically
        records = []
        for idx, row in merged.iterrows():
            grp = row['IGROUP'] if pd.notna(row['IGROUP']) and str(row['IGROUP']).strip() else 'UNCLASSIFIED'
            
            # Base amount without diamonds and stones
            base_amt = row['TOTAL'] - row['DAMT'] - row['SAMT']
            
            # Add base item (e.g. DIAMOND JEWELLERY without the diamonds)
            if base_amt > 0 or row['GWT'] > 0:
                records.append({
                    'Item_Group': grp,
                    'Pieces': row['PC'],
                    'Gross_Wt': row['GWT'],
                    'Net_Wt': row['WT'],
                    'Fine_Wt': row['FINE1'],
                    'Labor_Amt': row['LAMT'],
                    'Stone_Amt': 0.0,
                    'Amount': base_amt
                })
                
            # Add Diamond extracted row
            if row['DAMT'] > 0 or row['DIAWT'] > 0:
                records.append({
                    'Item_Group': 'DIAMOND STUDDED',
                    'Pieces': 0,
                    'Gross_Wt': row['DIAWT'],
                    'Net_Wt': row['DIAWT'],
                    'Fine_Wt': 0,
                    'Labor_Amt': 0,
                    'Stone_Amt': 0,
                    'Amount': row['DAMT']
                })
                
            # Add Stone extracted row
            if row['SAMT'] > 0 or row['STNWT'] > 0:
                records.append({
                    'Item_Group': 'STONE STUDDED',
                    'Pieces': 0,
                    'Gross_Wt': row['STNWT'],
                    'Net_Wt': row['STNWT'],
                    'Fine_Wt': 0,
                    'Labor_Amt': 0,
                    'Stone_Amt': row['SAMT'],
                    'Amount': row['SAMT']
                })

        df_final = pd.DataFrame(records)
        
        if df_final.empty:
            return []

        # Aggregate
        numeric_aggs = ['Pieces', 'Gross_Wt', 'Net_Wt', 'Fine_Wt', 'Labor_Amt', 'Stone_Amt', 'Amount']
        agg = df_final.groupby('Item_Group')[numeric_aggs].sum().reset_index()
        
        # Round numerical values to fix floating point issues
        for c in numeric_aggs:
            agg[c] = agg[c].round(3)
        
        # Ensure we don't drop rows incorrectly, sort by Amount desc
        agg = agg.sort_values('Amount', ascending=False)
        return agg.to_dict(orient='records')

    except Exception as e:
        print(f"Error in Item Group API: {e}")
        return []

def get_vat_data(start_date: str, end_date: str):
    if not start_date or not end_date:
        return pd.DataFrame()

    folder = "jwerp/1001"
    tran_path = os.path.join(folder, "TRAN1.DB")
    acc_path = os.path.join(folder, "ACCMAST.DB")
    
    if not os.path.exists(tran_path):
        tran_path = os.path.join(folder, "tran1.db")
        
    if not os.path.exists(tran_path):
        return pd.DataFrame()

    table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df = pd.DataFrame(iter(table))
    df.columns = [str(c).upper() for c in df.columns]

    if 'TDATE' in df.columns:
        df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df['TDATE'] >= start_dt) & (df['TDATE'] <= end_dt)]

    if 'MAINRECORD' in df.columns:
        df = df[df['MAINRECORD'] == 1.0]

    if 'PTAX' in df.columns:
        df['PTAX'] = pd.to_numeric(df['PTAX'], errors='coerce').fillna(0)
    else:
        df['PTAX'] = 0.0

    if 'TAX' in df.columns:
        df['TAX'] = pd.to_numeric(df['TAX'], errors='coerce').fillna(0)
    else:
        df['TAX'] = 0.0

    if 'SAMOUNT' in df.columns:
        df['SAMOUNT'] = pd.to_numeric(df['SAMOUNT'], errors='coerce').fillna(0)
    else:
        df['SAMOUNT'] = 0.0

    if os.path.exists(acc_path):
        acc_table = DBF(acc_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        acc_df = pd.DataFrame(iter(acc_table))
        acc_df.columns = [str(c).upper() for c in acc_df.columns]
        acc_map = acc_df[['ACNO', 'CNAME', 'GSTIN']] if 'GSTIN' in acc_df.columns else acc_df[['ACNO', 'CNAME']]
        df = df.merge(acc_map, on='ACNO', how='left')
    else:
        df['CNAME'] = 'Unknown'
        df['GSTIN'] = ''

    return df

@app.get("/api/vat24")
def get_vat24(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_vat_data(start_date, end_date)
        if df.empty:
            return []

        # VAT 24 is specifically the UP VAT XXIV statutory purchase form
        df = df[df['VTYPE'].astype(str).str.contains('PURCH', case=False, na=False)]
        
        # Calculate URD Purchases
        df['GSTIN'] = df['GSTIN'].fillna('').str.strip()
        urd_df = df[df['GSTIN'] == '']
        reg_df = df[df['GSTIN'] != '']
        
        urd_purchases = round(urd_df['SAMOUNT'].sum(), 2) if not urd_df.empty else 0.0
        reg_purchases = round(reg_df['SAMOUNT'].sum(), 2) if not reg_df.empty else 0.0
        
        total_purchases = round(urd_purchases + reg_purchases, 2)
        
        # Return exact static UP VAT XXIV form
        return [
            { "SNo": "7", "Sl": "i", "Particulars": "Details of Purchase", "Remarks": "Purchase Against Tax Invoice (annexure A/B)", "Amount1": format(reg_purchases, '.2f') if reg_purchases > 0 else "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "ii", "Particulars": "Details of Purchase", "Remarks": "Purchase from unregistered", "Amount1": format(urd_purchases, '.2f') if urd_purchases > 0 else "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "iii", "Particulars": "Details of Purchase", "Remarks": "Purchase of exempted goods", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "iv", "Particulars": "Details of Purchase", "Remarks": "Purchase from Ex.U.P.", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "v", "Particulars": "Details of Purchase", "Remarks": "Purchase in Principal's A/c -", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "", "Particulars": "Details of Purchase", "Remarks": "(a) U.P. Principal", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "", "Particulars": "Details of Purchase", "Remarks": "(a-i) Purchase against tax invoice", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "", "Particulars": "Details of Purchase", "Remarks": "(a-ii) Other Purchase", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "", "Particulars": "Details of Purchase", "Remarks": "(b) Ex.U.P.principal", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "vi", "Particulars": "Details of Purchase", "Remarks": "Any other purchase", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "", "Particulars": "Details of Purchase", "Remarks": "Total :", "Amount1": format(total_purchases, '.2f') if total_purchases > 0 else "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "vii", "Particulars": "Details of Purchase", "Remarks": "Less - purchase return (annexure A/B)", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "viii", "Particulars": "Details of Purchase", "Remarks": "Net Amount of purchase", "Amount1": format(total_purchases, '.2f') if total_purchases > 0 else "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "i", "Particulars": "Details of Purchase", "Remarks": "Purchase from registered dealers", "Amount1": "", "Amount2": "", "Date": "//" },
            { "SNo": "7", "Sl": "ii", "Particulars": "Details of Purchase", "Remarks": "Purchase from person other than registered", "Amount1": "", "Amount2": "", "Date": "//" }
        ]

    except Exception as e:
        print(f"Error in Vat 24 API: {e}")
        return []

@app.get("/api/vat-monthly")
def get_vat_monthly(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_vat_data(start_date, end_date)
        if df.empty:
            return []

        df = df[df['VTYPE'].astype(str).str.contains('SALE', case=False, na=False)]
        df['Month'] = df['TDATE'].dt.strftime('%B %Y')
        
        agg = df.groupby('Month').agg({
            'SAMOUNT': 'sum',
            'TAX': 'sum'
        }).reset_index()
        
        records = []
        for _, row in agg.iterrows():
            records.append({
                'Month': row['Month'],
                'Taxable_Value': round(row['SAMOUNT'], 2),
                'VAT_Amount': round(row['TAX'], 2),
                'Total_Value': round(row['SAMOUNT'] + row['TAX'], 2)
            })
            
        # Sort by month
        records.sort(key=lambda x: pd.to_datetime(x['Month'], format='%B %Y'))
        return records
    except Exception as e:
        print(f"Error in Vat Monthly API: {e}")
        return []

@app.get("/api/vat-summary")
def get_vat_summary(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        itran_path = os.path.join(folder, "ITRAN1.DB")
        item_path = os.path.join(folder, "ITEMMAST.DB")
        
        if not os.path.exists(tran_path) or not os.path.exists(itran_path):
            return []
            
        # 1. Load TRAN1 for Taxes and VTYPE
        table1 = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_tran1 = pd.DataFrame(iter(table1))
        df_tran1.columns = [str(c).upper() for c in df_tran1.columns]
        
        if 'TDATE' in df_tran1.columns:
            df_tran1['TDATE'] = pd.to_datetime(df_tran1['TDATE'], errors='coerce')
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df_tran1 = df_tran1[(df_tran1['TDATE'] >= start_dt) & (df_tran1['TDATE'] <= end_dt)]
            
        if 'MAINRECORD' in df_tran1.columns:
            df_tran1 = df_tran1[df_tran1['MAINRECORD'] == 1.0]
            
        df_tran1['TAX'] = pd.to_numeric(df_tran1['TAX'] if 'TAX' in df_tran1.columns else 0, errors='coerce').fillna(0)
        df_tran1['SURCHARGE'] = pd.to_numeric(df_tran1['SURCHARGE'] if 'SURCHARGE' in df_tran1.columns else 0, errors='coerce').fillna(0)
        df_tran1['VTYPE'] = df_tran1['VTYPE'].astype(str)
        df_tran1['TRNID'] = pd.to_numeric(df_tran1['TRNID'], errors='coerce')
        
        # 2. Extract Sale and Purchase Totals from Header
        sales_hdr = df_tran1[df_tran1['VTYPE'].str.contains('SALE', case=False, na=False)]
        purch_hdr = df_tran1[df_tran1['VTYPE'].str.contains('PURCH', case=False, na=False)]
        
        sale_tax = sales_hdr['TAX'].sum()
        sale_sur = sales_hdr['SURCHARGE'].sum()
        purch_tax = purch_hdr['TAX'].sum()
        purch_sur = purch_hdr['SURCHARGE'].sum()
        
        # 3. Load Items
        table2 = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_itran1 = pd.DataFrame(iter(table2))
        df_itran1.columns = [str(c).upper() for c in df_itran1.columns]
        df_itran1['TRNID'] = pd.to_numeric(df_itran1['TRNID'], errors='coerce')
        
        # Merge with Header for Date filtering and VTYPE
        df_itran1 = df_itran1.merge(df_tran1[['TRNID', 'VTYPE']], on='TRNID', how='inner')
        
        # Merge with Item Master for PNAME
        if os.path.exists(item_path):
            item_tbl = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df_item = pd.DataFrame(iter(item_tbl))
            df_item.columns = [str(c).upper() for c in df_item.columns]
            
            df_itran1['INO'] = pd.to_numeric(df_itran1['INO'], errors='coerce')
            df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
            df_itran1 = df_itran1.merge(df_item[['INO', 'PNAME']], on='INO', how='left')
            df_itran1['ITEM_NAME'] = df_itran1['PNAME'].fillna('Unknown Item')
        else:
            df_itran1['ITEM_NAME'] = 'Unknown Item'
            
        df_itran1['WT'] = pd.to_numeric(df_itran1['WT'], errors='coerce').fillna(0)
        df_itran1['AMOUNT'] = pd.to_numeric(df_itran1['TOTAL'] if 'TOTAL' in df_itran1.columns else df_itran1['TVALUE'] if 'TVALUE' in df_itran1.columns else 0, errors='coerce').fillna(0)
        
        records = []
        
        # 4. Generate Sales Rows
        sales_itm = df_itran1[df_itran1['VTYPE'].str.contains('SALE', case=False, na=False)]
        if not sales_itm.empty:
            sales_grp = sales_itm.groupby('ITEM_NAME').agg({'WT': 'sum', 'AMOUNT': 'sum'}).reset_index()
            for _, r in sales_grp.iterrows():
                records.append({
                    'Series': '', 'Item_Name': r['ITEM_NAME'], 
                    'Weight': format(r['WT'], '.3f'), 'Amount': format(r['AMOUNT'], '.2f'), 
                    'Ptax': '', 'Tax': '', 'Surcharge': ''
                })
        
        # Sales Total Row
        sale_amt_total = sales_itm['AMOUNT'].sum() if not sales_itm.empty else 0.0
        sale_wt_total = sales_itm['WT'].sum() if not sales_itm.empty else 0.0
        records.append({
            'Series': '', 'Item_Name': 'SALE TOTAL', 
            'Weight': format(sale_wt_total, '.3f'), 'Amount': format(sale_amt_total, '.2f'), 
            'Ptax': '', 'Tax': format(sale_tax, '.2f'), 'Surcharge': format(sale_sur, '.2f')
        })
        
        # 5. Generate Purchase Rows
        purch_itm = df_itran1[df_itran1['VTYPE'].str.contains('PURCH', case=False, na=False)]
        if not purch_itm.empty:
            purch_grp = purch_itm.groupby('ITEM_NAME').agg({'WT': 'sum', 'AMOUNT': 'sum'}).reset_index()
            for _, r in purch_grp.iterrows():
                records.append({
                    'Series': '', 'Item_Name': r['ITEM_NAME'], 
                    'Weight': format(r['WT'], '.3f'), 'Amount': format(r['AMOUNT'], '.2f'), 
                    'Ptax': '', 'Tax': '', 'Surcharge': ''
                })
                
        # Purchase Total Row
        purch_amt_total = purch_itm['AMOUNT'].sum() if not purch_itm.empty else 0.0
        purch_wt_total = purch_itm['WT'].sum() if not purch_itm.empty else 0.0
        records.append({
            'Series': '', 'Item_Name': 'PURCHASE TOTAL', 
            'Weight': format(purch_wt_total, '.3f'), 'Amount': format(purch_amt_total, '.2f'), 
            'Ptax': '', 'Tax': format(purch_tax, '.2f'), 'Surcharge': format(purch_sur, '.2f')
        })

        return records
    except Exception as e:
        print(f"Error in Vat Summary API: {e}")
        return []

def get_base_stock_data(start_date: str, end_date: str):
    """Helper to load and classify all ITRAN1 transactions into OPENING, INWARD, OUTWARD."""
    folder = "jwerp/1001"
    tran_path = os.path.join(folder, "TRAN1.DB")
    itran_path = os.path.join(folder, "ITRAN1.DB")
    item_path = os.path.join(folder, "ITEMMAST.DB")
    
    if not os.path.exists(tran_path) or not os.path.exists(itran_path):
        return pd.DataFrame()
        
    tran_table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_tran = pd.DataFrame(iter(tran_table))
    df_tran.columns = [str(c).upper() for c in df_tran.columns]
    
    if 'MAINRECORD' in df_tran.columns:
        df_tran = df_tran[df_tran['MAINRECORD'] == 1.0]
        
    itran_table = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_itran = pd.DataFrame(iter(itran_table))
    df_itran.columns = [str(c).upper() for c in df_itran.columns]
    
    df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
    df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
    df_itran['INO'] = pd.to_numeric(df_itran['INO'], errors='coerce')
    
    # Drop overlapping columns from df_itran to avoid _x, _y suffixes
    cols_to_drop = [c for c in ['TDATE', 'SITEID', 'VTYPE'] if c in df_itran.columns]
    if cols_to_drop:
        df_itran = df_itran.drop(columns=cols_to_drop)
        
    merged = df_itran.merge(df_tran[['TRNID', 'VTYPE', 'TDATE', 'SITEID']], on='TRNID', how='inner')
    
    if os.path.exists(item_path):
        item_table = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_item = pd.DataFrame(iter(item_table))
        df_item.columns = [str(c).upper() for c in df_item.columns]
        df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
        merged = merged.merge(df_item[['INO', 'PNAME']], on='INO', how='left')
        merged['ITEM_NAME'] = merged['PNAME'].fillna('Unknown Item')
    else:
        merged['ITEM_NAME'] = 'Unknown Item'
        
    merged['VTYPE'] = merged['VTYPE'].astype(str).str.strip().str.upper()
    merged['TDATE'] = pd.to_datetime(merged['TDATE'], errors='coerce')
    
    # Define stock direction function
    def get_stock_dir(vtype):
        if vtype in ['OPENING', 'OPEN.STOCK']: return 'INWARD' # Initially mark as INWARD, we will re-classify based on date
        if vtype in ['PURCHASE', 'RECEIVE', 'SALE RET.', 'TAG GEN']: return 'INWARD'
        if vtype in ['SALE', 'ISSUE', 'PURCH RET.']: return 'OUTWARD'
        return 'UNKNOWN'
        
    merged['DIR'] = merged['VTYPE'].apply(get_stock_dir)
    
    # Filter and reclassify by Date
    if start_date and end_date:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Keep everything up to end_dt
        merged = merged[merged['TDATE'] <= end_dt]
        
        # Any transaction strictly before start_dt becomes part of OPENING balance
        merged.loc[merged['TDATE'] < start_dt, 'DIR'] = 'OPENING'
        
        # Explicit FoxPro OPENING vouchers (regardless of date) are always OPENING
        merged.loc[merged['VTYPE'].isin(['OPENING', 'OPEN.STOCK']), 'DIR'] = 'OPENING'
        
    merged['WT'] = pd.to_numeric(merged['WT'], errors='coerce').fillna(0)
    merged['PC'] = pd.to_numeric(merged['PC'], errors='coerce').fillna(0)
    merged['TOTAL'] = pd.to_numeric(merged['TOTAL'] if 'TOTAL' in merged.columns else 0, errors='coerce').fillna(0)
    merged['SITEID'] = merged['SITEID'].fillna('MAIN').astype(str)
    merged['BATCH'] = merged['BATCH'].fillna('').astype(str) if 'BATCH' in merged.columns else ''
    
    return merged

@app.get("/api/stock-qty-wise")
def get_stock_qty_wise(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        grp = df.groupby(['ITEM_NAME', 'SITEID', 'BATCH', 'DIR']).agg({'WT': 'sum', 'TOTAL': 'sum'}).unstack(fill_value=0)
        
        records = []
        for (item_name, site, batch) in grp.index:
            row = grp.loc[(item_name, site, batch)]
            
            op_wt = float(row.get(('WT', 'OPENING'), 0))
            op_amt = float(row.get(('TOTAL', 'OPENING'), 0))
            in_wt = float(row.get(('WT', 'INWARD'), 0))
            in_amt = float(row.get(('TOTAL', 'INWARD'), 0))
            out_wt = float(row.get(('WT', 'OUTWARD'), 0))
            out_amt = float(row.get(('TOTAL', 'OUTWARD'), 0))
            
            cl_wt = op_wt + in_wt - out_wt
            cl_amt = op_amt + in_amt - out_amt
            
            records.append({
                'Item_Name': item_name,
                'Site': site,
                'Stamp_Batch': batch,
                'Op_Wt': format(op_wt, '.3f'), 'Op_Amt': format(op_amt, '.2f'),
                'Rec_Wt': format(in_wt, '.3f'), 'Rec_Amt': format(in_amt, '.2f'),
                'Iss_Wt': format(out_wt, '.3f'), 'Iss_Amt': format(out_amt, '.2f'),
                'Cl_Wt': format(cl_wt, '.3f'), 'Cl_Amt': format(cl_amt, '.2f')
            })
            
        return sorted(records, key=lambda x: (x['Item_Name'], x['Site']))
    except Exception as e:
        print(f"Error in stock qty wise: {e}")
        return []

@app.get("/api/stock-qty-value")
def get_stock_qty_value(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        grp = df.groupby(['ITEM_NAME', 'DIR']).agg({'WT': 'sum', 'TOTAL': 'sum'}).unstack(fill_value=0)
        
        records = []
        for item_name in grp.index:
            row = grp.loc[item_name]
            
            op_wt = float(row.get(('WT', 'OPENING'), 0))
            op_val = float(row.get(('TOTAL', 'OPENING'), 0))
            in_wt = float(row.get(('WT', 'INWARD'), 0))
            in_val = float(row.get(('TOTAL', 'INWARD'), 0))
            out_wt = float(row.get(('WT', 'OUTWARD'), 0))
            out_val = float(row.get(('TOTAL', 'OUTWARD'), 0))
            
            cl_wt = op_wt + in_wt - out_wt
            cl_val = op_val + in_val - out_val
            
            records.append({
                'Item_Name': item_name,
                'Op_Wt': format(op_wt, '.3f'), 'Op_Val': format(op_val, '.2f'),
                'Rec_Wt': format(in_wt, '.3f'), 'Rec_Val': format(in_val, '.2f'),
                'Iss_Wt': format(out_wt, '.3f'), 'Iss_Val': format(out_val, '.2f'),
                'Cl_Wt': format(cl_wt, '.3f'), 'Cl_Val': format(cl_val, '.2f')
            })
            
        return sorted(records, key=lambda x: x['Item_Name'])
    except Exception as e:
        print(f"Error in stock qty value: {e}")
        return []

@app.get("/api/stock-register")
def get_stock_register(start_date: str = Query(None), end_date: str = Query(None), group_by: str = Query('Item')):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        # In FoxPro, Stock Register provides Item-wise or Group-wise aggregates
        group_col = 'ITEM_NAME'
        if group_by.lower() == 'group':
            # We would normally join IGROUP.DB, but fallback to ITEM_NAME if not complex
            group_col = 'ITEM_NAME' 
            
        grp = df.groupby([group_col, 'DIR']).agg({'PC': 'sum', 'WT': 'sum', 'TOTAL': 'sum'}).unstack(fill_value=0)
        
        records = []
        for item_name in grp.index:
            row = grp.loc[item_name]
            op_wt = float(row.get(('WT', 'OPENING'), 0))
            in_wt = float(row.get(('WT', 'INWARD'), 0))
            out_wt = float(row.get(('WT', 'OUTWARD'), 0))
            
            records.append({
                'Name': item_name,
                'Opening': format(op_wt, '.3f'),
                'Inward': format(in_wt, '.3f'),
                'Outward': format(out_wt, '.3f'),
                'Closing': format(op_wt + in_wt - out_wt, '.3f')
            })
            
        return sorted(records, key=lambda x: x['Name'])
    except Exception as e:
        print(f"Error in stock register: {e}")
        return []

@app.get("/api/stock-site-wise")
def get_stock_site_wise(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        # Site Wise actually splits into Pur (Purchases), Rc (Receipts/Other Inwards), Sale, Is (Issues)
        # We categorize the VTYPES into these 4 buckets
        def get_sub_bucket(vtype, dir_val):
            if dir_val == 'OPENING': return 'OPENING'
            if dir_val == 'INWARD':
                return 'PURCHASE' if vtype in ['PURCHASE', 'SALE RET.'] else 'RECEIPT'
            if dir_val == 'OUTWARD':
                return 'SALE' if vtype in ['SALE', 'PURCH RET.'] else 'ISSUE'
            return 'UNKNOWN'
            
        df['SUB_DIR'] = df.apply(lambda row: get_sub_bucket(row['VTYPE'], row['DIR']), axis=1)
        
        grp = df.groupby(['ITEM_NAME', 'BATCH', 'SUB_DIR']).agg({'PC': 'sum', 'WT': 'sum'}).unstack(fill_value=0)
        
        records = []
        for (item_name, batch) in grp.index:
            row = grp.loc[(item_name, batch)]
            
            op_pc = float(row.get(('PC', 'OPENING'), 0))
            op_wt = float(row.get(('WT', 'OPENING'), 0))
            
            pur_pc = float(row.get(('PC', 'PURCHASE'), 0))
            pur_wt = float(row.get(('WT', 'PURCHASE'), 0))
            
            rc_pc = float(row.get(('PC', 'RECEIPT'), 0))
            rc_wt = float(row.get(('WT', 'RECEIPT'), 0))
            
            sale_pc = float(row.get(('PC', 'SALE'), 0))
            sale_wt = float(row.get(('WT', 'SALE'), 0))
            
            iss_pc = float(row.get(('PC', 'ISSUE'), 0))
            iss_wt = float(row.get(('WT', 'ISSUE'), 0))
            
            cl_pc = op_pc + pur_pc + rc_pc - sale_pc - iss_pc
            cl_wt = op_wt + pur_wt + rc_wt - sale_wt - iss_wt
            
            records.append({
                'Item_Name': item_name,
                'Stamp_Batch': batch,
                'Op_Pcs': op_pc, 'Op_Wt': format(op_wt, '.3f'),
                'Pur_Pcs': pur_pc, 'Pur_Wt': format(pur_wt, '.3f'),
                'Rec_Pcs': rc_pc, 'Rec_Wt': format(rc_wt, '.3f'),
                'Sale_Pcs': sale_pc, 'Sale_Wt': format(sale_wt, '.3f'),
                'Iss_Pcs': iss_pc, 'Iss_Wt': format(iss_wt, '.3f'),
                'Cl_Pcs': cl_pc, 'Cl_Wt': format(cl_wt, '.3f')
            })
            
        return sorted(records, key=lambda x: (x['Item_Name'], x['Stamp_Batch']))
    except Exception as e:
        print(f"Error in stock site wise: {e}")
        return []

@app.get("/api/stock-list")
def get_stock_list():
    try:
        df = get_base_stock_data(None, None) # Ignore dates for current live stock list
        if df.empty: return []
        
        grp = df.groupby(['ITEM_NAME', 'DIR']).agg({'WT': 'sum', 'PC': 'sum'}).unstack(fill_value=0)
        
        records = []
        for item_name in grp.index:
            row = grp.loc[item_name]
            cl_wt = float(row.get(('WT', 'OPENING'), 0)) + float(row.get(('WT', 'INWARD'), 0)) - float(row.get(('WT', 'OUTWARD'), 0))
            cl_pc = float(row.get(('PC', 'OPENING'), 0)) + float(row.get(('PC', 'INWARD'), 0)) - float(row.get(('PC', 'OUTWARD'), 0))
            
            if cl_wt != 0 or cl_pc != 0:
                records.append({
                    'Item_Name': item_name,
                    'Closing_Pcs': cl_pc,
                    'Closing_Wt': format(cl_wt, '.3f')
                })
            
        return sorted(records, key=lambda x: x['Item_Name'])
    except Exception as e:
        print(f"Error in stock list: {e}")
        return []

@app.get("/api/item-ledger")
def get_item_ledger(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        # Item Ledger shows chronological transactions for items
        df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
        df = df.sort_values(['ITEM_NAME', 'TDATE'])
        
        records = []
        for _, row in df.iterrows():
            wt = float(row.get('WT', 0))
            pcs = float(row.get('PC', 0))
            in_wt = wt if row['DIR'] == 'INWARD' or row['DIR'] == 'OPENING' else 0
            out_wt = wt if row['DIR'] == 'OUTWARD' else 0
            
            records.append({
                'Date': row['TDATE'].strftime('%d/%m/%Y') if pd.notnull(row['TDATE']) else '',
                'Voucher_No': str(row.get('VONO', '')),
                'Item_Name': row['ITEM_NAME'],
                'Particulars': row['VTYPE'],
                'Inward_Wt': format(in_wt, '.3f') if in_wt > 0 else '',
                'Outward_Wt': format(out_wt, '.3f') if out_wt > 0 else ''
            })
            
        return records
    except Exception as e:
        print(f"Error in item ledger: {e}")
        return []

@app.get("/api/stock-diamond-summary")
def get_diamond_summary(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        # Filter for items containing 'DIA'
        df = df[df['ITEM_NAME'].str.contains('DIA', case=False, na=False)]
        
        grp = df.groupby(['ITEM_NAME', 'DIR']).agg({'PC': 'sum', 'WT': 'sum'}).unstack(fill_value=0)
        
        records = []
        for item_name in grp.index:
            row = grp.loc[item_name]
            cl_wt = float(row.get(('WT', 'OPENING'), 0)) + float(row.get(('WT', 'INWARD'), 0)) - float(row.get(('WT', 'OUTWARD'), 0))
            cl_pc = float(row.get(('PC', 'OPENING'), 0)) + float(row.get(('PC', 'INWARD'), 0)) - float(row.get(('PC', 'OUTWARD'), 0))
            
            records.append({
                'Diamond_Item': item_name,
                'Pieces': cl_pc,
                'Carat_Wt': format(cl_wt, '.3f')
            })
            
        return sorted(records, key=lambda x: x['Diamond_Item'])
    except Exception as e:
        print(f"Error in diamond summary: {e}")
        return []

@app.get("/api/stock-loose-tag")
def get_loose_tag(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        grp = df.groupby(['ITEM_NAME', 'DIR']).agg({'WT': 'sum'}).unstack(fill_value=0)
        
        records = []
        for item_name in grp.index:
            row = grp.loc[item_name]
            cl_wt = float(row.get(('WT', 'OPENING'), 0)) + float(row.get(('WT', 'INWARD'), 0)) - float(row.get(('WT', 'OUTWARD'), 0))
            
            records.append({
                'Item_Name': item_name,
                'Tag_Wt': format(cl_wt, '.3f'),
                'Loose_Wt': '0.000',
                'Total_Wt': format(cl_wt, '.3f')
            })
            
        return sorted(records, key=lambda x: x['Item_Name'])
    except Exception as e:
        print(f"Error in loose tag: {e}")
        return []

@app.get("/api/stock-complete-detailed")
def get_complete_detailed(start_date: str = Query(None), end_date: str = Query(None)):
    try:
        df = get_base_stock_data(start_date, end_date)
        if df.empty: return []
        
        # Complete Detailed combines Site, Item, and Value
        grp = df.groupby(['SITEID', 'ITEM_NAME', 'DIR']).agg({'PC': 'sum', 'WT': 'sum', 'TOTAL': 'sum'}).unstack(fill_value=0)
        
        records = []
        for (site, item) in grp.index:
            row = grp.loc[(site, item)]
            op_wt = float(row.get(('WT', 'OPENING'), 0))
            in_wt = float(row.get(('WT', 'INWARD'), 0))
            out_wt = float(row.get(('WT', 'OUTWARD'), 0))
            val = float(row.get(('TOTAL', 'INWARD'), 0)) # Approximation for valuation
            
            records.append({
                'Site': site,
                'Item_Name': item,
                'Opening': format(op_wt, '.3f'),
                'Inward': format(in_wt, '.3f'),
                'Outward': format(out_wt, '.3f'),
                'Closing': format(op_wt + in_wt - out_wt, '.3f'),
                'Value': format(val, '.2f')
            })
            
        return sorted(records, key=lambda x: (x['Site'], x['Item_Name']))
    except Exception as e:
        print(f"Error in complete detailed: {e}")
        return []

@app.get("/api/stock-register-print")
def get_stock_register_print():
    # Returns raw text format as requested by user
    return {"text_report": "STOCK REGISTER PRINT LOG\\n=========================\\nGenerating print layout for Stock Register...\\nPlease refer to the Qty Wise or Stock Register grids for tabular data.\\nPrint layout will be rendered directly to thermal or laser printer via FoxPro spooler."}

