import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
tran = DBF(os.path.join(folder, "TRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(tran))
df_tran.columns = [str(c).upper() for c in df_tran.columns]
df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')
df_tran = df_tran[(df_tran['TDATE'] >= '2025-04-01') & (df_tran['TDATE'] <= '2025-04-30')]
df_tran = df_tran[df_tran['VTYPE'].str.contains('SALE', na=False)]
df_tran = df_tran[df_tran['MAINRECORD'] == 1.0]

valid_trns = df_tran['TRNID'].dropna().tolist()

itran = DBF(os.path.join(folder, "ITRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran))
df_itran.columns = [str(c).upper() for c in df_itran.columns]
df_itran = df_itran[df_itran['TRNID'].isin(valid_trns)]

item = DBF(os.path.join(folder, "ITEMMAST.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(item))
df_item.columns = [str(c).upper() for c in df_item.columns]
df_item = df_item[['INO', 'IGROUPID']]

grp = DBF(os.path.join(folder, "igroup.db"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_grp = pd.DataFrame(iter(grp))
df_grp.columns = [str(c).upper() for c in df_grp.columns]
df_grp = df_grp[['IGROUPID', 'IGROUP']]

merged = df_itran.merge(df_item, on='INO', how='left').merge(df_grp, on='IGROUPID', how='left')

numeric_cols = ['PC', 'GWT', 'WT', 'FINE1', 'LAMT', 'SAMT', 'DAMT', 'TOTAL', 'DIAWT', 'STNWT']
for c in numeric_cols:
    merged[c] = pd.to_numeric(merged[c], errors='coerce').fillna(0)

records = []
for idx, row in merged.iterrows():
    grp_name = row['IGROUP'] if pd.notna(row['IGROUP']) and str(row['IGROUP']).strip() else 'UNCLASSIFIED'
    
    base_amt = row['TOTAL'] - row['DAMT']
    
    records.append({
        'Item_Group': grp_name,
        'Pieces': row['PC'],
        'Gross_Wt': row['GWT'],
        'Net_Wt': row['WT'],
        'Fine_Wt': row['FINE1'],
        'Labor_Amt': row['LAMT'],
        'Stone_Amt': row['SAMT'],
        'Amount': base_amt
    })
    
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

df_final = pd.DataFrame(records)
agg = df_final.groupby('Item_Group').sum().reset_index()
print(agg)
