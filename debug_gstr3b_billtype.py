import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
table = DBF(os.path.join(folder, "TRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
df = df[(df['TDATE'] >= '2025-10-01') & (df['TDATE'] <= '2025-10-31')]

df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
df = df[df['VTYPE'].str.contains('SALE', na=False)]
df = df[df['MAINRECORD'] == 1.0]

print("Total SALE Amount (No Billtype filter):", df['AMOUNT'].sum())

df_tax = df[pd.to_numeric(df['BILLTYPE'], errors='coerce').isin([1.0, 2.0, 3.0])]
print("Total SALE Amount (BILLTYPE 1,2,3):", df_tax['AMOUNT'].sum())

# Let's also check basic amount
df_tax['Basic'] = df_tax['AMOUNT'] - pd.to_numeric(df_tax['CGST'], errors='coerce').fillna(0) - pd.to_numeric(df_tax['SGST'], errors='coerce').fillna(0) - pd.to_numeric(df_tax['IGST'], errors='coerce').fillna(0)
print("Total SALE Basic Amount (BILLTYPE 1,2,3):", df_tax['Basic'].sum())
