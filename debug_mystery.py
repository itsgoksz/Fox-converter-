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
df_july = df[(df['TDATE'] >= '2025-07-01') & (df['TDATE'] <= '2025-07-31')]
df_july = df_july[df_july['MAINRECORD'] == 1.0]
df_july = df_july.merge(df_s[['SERIESID', 'SERIES_BILLTYPE', 'SERIES', 'SERIES_VTYPE']], on='SERIESID', how='left')

mystery = df_july[df_july['SAMOUNT'] == 1700229.00]
if not mystery.empty:
    print("--- The 1.7M Mystery Transaction ---")
    row = mystery.iloc[0].dropna()
    for col, val in row.items():
        if col not in ['LNARR', 'NARR', 'TRDATA', 'CPADD1']:
            print(f"{col}: {val}")

