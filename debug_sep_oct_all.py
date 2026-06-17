from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_sep_oct = df[(df['TDATE'] >= '2025-09-01') & (df['TDATE'] <= '2025-10-31')]
df_sep_oct = df_sep_oct[df_sep_oct['MAINRECORD'] == 1.0]
df_sep_oct = df_sep_oct[df_sep_oct['VTYPE'].str.strip().str.upper() == 'SALE']

print("--- Breakdown of all BILLTYPEs in Sep/Oct ---")
grouped = df_sep_oct.groupby(['BILLTYPE']).agg({'SAMOUNT': 'sum', 'IGST': 'sum', 'CGST': 'sum'}).reset_index()
print(grouped)

# Print out any unknown BILLTYPES (like 4.0)
print("\n--- Details of BILLTYPE 4.0 ---")
bt_4 = df_sep_oct[df_sep_oct['BILLTYPE'] == 4.0]
if not bt_4.empty:
    print(bt_4[['TDATE', 'SAMOUNT', 'IGST', 'BILLINFO']])

