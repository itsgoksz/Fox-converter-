import pandas as pd
from dbfread import DBF
import os

tran1 = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran1 = pd.DataFrame(iter(tran1))
df_tran1['TDATE'] = pd.to_datetime(df_tran1['TDATE'], errors='coerce')
df_tran1 = df_tran1[(df_tran1['TDATE'] >= '2025-04-01') & (df_tran1['TDATE'] <= '2026-03-31')]
df_tran1 = df_tran1[df_tran1['MAINRECORD'] == 1.0]

itran1 = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran1 = pd.DataFrame(iter(itran1))

itemmast = DBF("jwerp/1001/ITEMMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(itemmast))
df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
df_itran1['INO'] = pd.to_numeric(df_itran1['INO'], errors='coerce')

df_itran1 = df_itran1.merge(df_item[['INO', 'INAME']], on='INO', how='left')

# Merge
df_tran1['TRNID'] = pd.to_numeric(df_tran1['TRNID'], errors='coerce')
df_itran1['TRNID'] = pd.to_numeric(df_itran1['TRNID'], errors='coerce')
merged = df_itran1.merge(df_tran1[['TRNID', 'VTYPE', 'PTAX', 'TAX']], on='TRNID', how='inner')

merged['WT'] = pd.to_numeric(merged['WT'], errors='coerce').fillna(0)
merged['TOTAL'] = pd.to_numeric(merged['TOTAL'], errors='coerce').fillna(0)

# Filter Sale
sales = merged[merged['VTYPE'].str.contains('SALE', case=False, na=False)]
sales_grp = sales.groupby('INAME').agg({'WT': 'sum', 'TOTAL': 'sum'}).reset_index()
print("Sales:")
print(sales_grp.head())

# Filter Purchase
purchases = merged[merged['VTYPE'].str.contains('PURCH', case=False, na=False)]
purchases_grp = purchases.groupby('INAME').agg({'WT': 'sum', 'TOTAL': 'sum'}).reset_index()
print("Purchases:")
print(purchases_grp.head())

