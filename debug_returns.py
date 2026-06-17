from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_ret = df[(df['TDATE'] >= '2025-07-01') & (df['TDATE'] <= '2025-10-31')]
df_ret = df_ret[df_ret['MAINRECORD'] == 1.0]
df_ret = df_ret[df_ret['VTYPE'].str.strip().str.upper() == 'SALE RET.']

print("--- SALE RETURNS (Jul-Oct) ---")
for idx, row in df_ret.iterrows():
    print(f"Date: {row['TDATE'].date()} | Amount: {row['SAMOUNT']} | BILLTYPE: {row['BILLTYPE']} | IGST: {row['IGST']} | CGST: {row['CGST']}")

print("\n--- Summary by Month & BILLTYPE ---")
grouped = df_ret.groupby([df_ret['TDATE'].dt.month, 'BILLTYPE']).agg({'SAMOUNT': 'sum', 'CGST': 'sum'}).reset_index()
grouped.columns = ['Month', 'BILLTYPE', 'SAMOUNT_SUM', 'CGST_SUM']
print(grouped)

