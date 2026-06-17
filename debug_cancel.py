from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])
df_sales = df[(df['TDATE'] >= '2025-08-01') & (df['TDATE'] <= '2025-10-31')]
df_sales = df_sales[df_sales['MAINRECORD'] == 1.0]
df_sales = df_sales[df_sales['VTYPE'].str.strip().str.upper() == 'SALE']
df_sales = df_sales[df_sales['BILLTYPE'].isin([1.0, 2.0, 3.0])]

# Let's hunt for cancellation flags!
print("--- Hunting for Cancelled Invoices in Aug/Sep/Oct ---")
for idx, row in df_sales.iterrows():
    is_cancelled = False
    reasons = []
    
    if 'CANCEL' in str(row.get('NOTECNTR', '')).upper():
        is_cancelled = True
        reasons.append(f"NOTECNTR: {row['NOTECNTR']}")
        
    if str(row.get('DEL', '')).strip() != '':
        is_cancelled = True
        reasons.append(f"DEL flag: '{row['DEL']}'")
        
    if 'CANCEL' in str(row.get('STATUS', '')).upper():
        is_cancelled = True
        reasons.append(f"STATUS: '{row['STATUS']}'")
        
    if is_cancelled:
        print(f"Date: {row['TDATE'].date()} | Amount: {row['SAMOUNT']} | Bucket: {row['BILLTYPE']} | Reasons: {reasons}")

