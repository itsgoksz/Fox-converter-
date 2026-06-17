from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

s_table = DBF("jwerp/1001/series.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_s = pd.DataFrame(iter(s_table))
df_s.columns = [str(c).upper() for c in df_s.columns]
df_s = df_s.rename(columns={'BILLTYPE': 'SERIES_BILLTYPE', 'VTYPE': 'SERIES_VTYPE'})

df['TDATE'] = pd.to_datetime(df['TDATE'])
df_aug = df[(df['TDATE'] >= '2025-08-01') & (df['TDATE'] <= '2025-08-31')]
df_aug = df_aug[df_aug['MAINRECORD'] == 1.0]
df_aug = df_aug[df_aug['VTYPE'].str.strip().str.upper() == 'SALE']

# Merge to get the Series name
df_aug = df_aug.merge(df_s[['SERIESID', 'SERIES']], on='SERIESID', how='left')

print("--- August BILLTYPE 5 Transactions ---")
aug_5 = df_aug[df_aug['BILLTYPE'] == 5.0]
if not aug_5.empty:
    print(aug_5[['SAMOUNT', 'SERIES', 'BILLINFO']])

print("\n--- August BILLTYPE 1 Transactions ---")
aug_1 = df_aug[df_aug['BILLTYPE'] == 1.0]
if not aug_1.empty:
    print(aug_1[['SAMOUNT', 'SERIES', 'BILLINFO']])

