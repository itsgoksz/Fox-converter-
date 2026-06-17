import pandas as pd
from dbfread import DBF

# 1. Load data
tran_table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(tran_table))
itran_table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran_table))
item_table = DBF("jwerp/1001/ITEMMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(item_table))

df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
df_itran['INO'] = pd.to_numeric(df_itran['INO'], errors='coerce')
df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')

# Merge
merged = df_itran.merge(df_tran[['TRNID', 'VTYPE', 'TDATE', 'MAINRECORD']], on='TRNID', how='inner')
merged = merged.merge(df_item[['INO', 'PNAME']], on='INO', how='left')

# Filter MAINRECORD
merged = merged[merged['MAINRECORD'] == 1.0]

merged['VTYPE'] = merged['VTYPE'].astype(str).str.strip().str.upper()
merged['WT'] = pd.to_numeric(merged['WT'], errors='coerce').fillna(0)
merged['PC'] = pd.to_numeric(merged['PC'], errors='coerce').fillna(0)

# Classify
def get_stock_dir(vtype):
    if vtype in ['OPENING', 'OPEN.STOCK']: return 'OPENING'
    if vtype in ['PURCHASE', 'RECEIVE', 'SALE RET.', 'TAG GEN']: return 'INWARD'
    if vtype in ['SALE', 'ISSUE', 'PURCH RET.']: return 'OUTWARD'
    return 'UNKNOWN'

merged['DIR'] = merged['VTYPE'].apply(get_stock_dir)

# Aggregate
grp = merged.groupby(['PNAME', 'DIR']).agg({'WT': 'sum', 'PC': 'sum'}).unstack(fill_value=0)
print(grp.head())
