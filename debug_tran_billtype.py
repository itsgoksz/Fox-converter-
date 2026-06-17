from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])
df_april = df[(df['TDATE'] >= '2025-04-01') & (df['TDATE'] <= '2025-04-30')]
df_april = df_april[df_april['MAINRECORD'] == 1.0]
df_april = df_april[df_april['VTYPE'].str.strip().str.upper() == 'SALE']

print("--- April Transactions ---")
print(df_april[['SAMOUNT', 'BILLTYPE']])

df_july = df[(df['TDATE'] >= '2025-07-01') & (df['TDATE'] <= '2025-07-31')]
df_july = df_july[df_july['MAINRECORD'] == 1.0]
df_july = df_july[df_july['VTYPE'].str.strip().str.upper() == 'SALE']

print("\n--- July Transactions ---")
print(df_july[['SAMOUNT', 'BILLTYPE']])

