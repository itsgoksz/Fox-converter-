import pandas as pd
from dbfread import DBF
import os

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
df = df[(df['TDATE'] >= '2025-04-01') & (df['TDATE'] <= '2026-03-31')]
df = df[df['VTYPE'].str.contains('PURCH', case=False, na=False)]
df = df[df['MAINRECORD'] == 1.0]

acc_table = DBF("jwerp/1001/ACCMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
acc_df = pd.DataFrame(iter(acc_table))
acc_df['ACNO'] = pd.to_numeric(acc_df['ACNO'], errors='coerce')
df['ACNO'] = pd.to_numeric(df['ACNO'], errors='coerce')
df = df.merge(acc_df[['ACNO', 'GSTIN']], on='ACNO', how='left')

df['GSTIN'] = df['GSTIN'].fillna('').str.strip()
urd_purchases = df[df['GSTIN'] == '']
print("URD Purchases Sum:", urd_purchases['SAMOUNT'].sum())
print("Total Purchases Sum:", df['SAMOUNT'].sum())
