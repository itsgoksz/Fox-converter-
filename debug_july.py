from dbfread import DBF
import pandas as pd

# Load TRAN1.DB
table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

# Load SERIES.DB
s_table = DBF("jwerp/1001/series.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_s = pd.DataFrame(iter(s_table))
df_s.columns = [str(c).upper() for c in df_s.columns]
df_s = df_s.rename(columns={'BILLTYPE': 'SERIES_BILLTYPE', 'VTYPE': 'SERIES_VTYPE'})

# Filter for July
df['TDATE'] = pd.to_datetime(df['TDATE'])
df_july = df[(df['TDATE'] >= '2025-07-01') & (df['TDATE'] <= '2025-07-31')]

# Filter MAINRECORD
df_july = df_july[df_july['MAINRECORD'] == 1.0]

# Join series
df_july = df_july.merge(df_s[['SERIESID', 'SERIES_BILLTYPE', 'SERIES', 'SERIES_VTYPE']], on='SERIESID', how='left')

# Group by VTYPE, SERIES, SERIES_VTYPE to see all transactions in July
print("--- JULY TRANSACTIONS GROUPED ---")
grouped = df_july.groupby(['VTYPE', 'SERIES_VTYPE', 'SERIES', 'SERIES_BILLTYPE'])['SAMOUNT'].agg(['sum', 'count']).reset_index()
print(grouped)

# Print specific breakdown to see what adds up to 1992722
print("\n--- Let's look at IGST == 0 and BILLTYPE == 1 (Tax Invoice Bucket) ---")
tax_inv = df_july[(df_july['IGST'] == 0) & (df_july['SERIES_BILLTYPE'] == 1)]
print(tax_inv.groupby(['VTYPE', 'SERIES'])['SAMOUNT'].agg(['sum', 'count']))

