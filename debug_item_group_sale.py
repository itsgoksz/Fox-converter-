import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"

print("Loading TRAN1...")
tran = DBF(os.path.join(folder, "TRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(tran))
df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')
df_tran = df_tran[(df_tran['TDATE'] >= '2025-10-01') & (df_tran['TDATE'] <= '2025-10-31')]
df_tran['VTYPE'] = df_tran['VTYPE'].astype(str).str.strip().str.upper()

sale_trns = df_tran[df_tran['VTYPE'].str.contains('SALE', na=False)]['TRNID'].dropna().tolist()
pur_trns = df_tran[df_tran['VTYPE'].str.contains('PUR', na=False)]['TRNID'].dropna().tolist()

print("Loading ITRAN1...")
itran = DBF(os.path.join(folder, "ITRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran))
df_itran = df_itran[df_itran['TRNID'].isin(sale_trns + pur_trns)]

print("Loading ITEMMAST...")
item = DBF(os.path.join(folder, "ITEMMAST.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(item))[['INO', 'IGROUPID']]

print("Loading IGROUP...")
grp = DBF(os.path.join(folder, "igroup.db"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_grp = pd.DataFrame(iter(grp))[['IGROUPID', 'IGROUP']]

# Merge
merged = df_itran.merge(df_item, on='INO', how='left').merge(df_grp, on='IGROUPID', how='left')
merged['VTYPE'] = merged['TRNID'].apply(lambda x: 'SALE' if x in sale_trns else 'PURCHASE')

sale_merged = merged[merged['VTYPE'] == 'SALE']
numeric_cols = ['PC', 'GWT', 'WT', 'FINE1', 'TOTAL', 'LAMT', 'SAMT']
for c in numeric_cols:
    sale_merged[c] = pd.to_numeric(sale_merged[c], errors='coerce').fillna(0)

agg = sale_merged.groupby('IGROUP')[numeric_cols].sum().reset_index()
print(agg)

