from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_pur = df[(df['TDATE'] >= '2025-10-01') & (df['TDATE'] <= '2025-10-31')]
df_pur = df_pur[df_pur['MAINRECORD'] == 1.0]

# Check VTYPEs related to purchases
print("--- Unique Purchase VTYPES in Oct ---")
pur_vtypes = df_pur[df_pur['VTYPE'].astype(str).str.strip().str.upper().str.contains('PURCHASE')]['VTYPE'].unique()
print(pur_vtypes)

df_pur = df_pur[df_pur['VTYPE'].str.strip().str.upper() == 'PURCHASE']

print("\n--- October Purchases ---")
for idx, row in df_pur.iterrows():
    print(f"Date: {row['TDATE'].date()} | Amount: {row['SAMOUNT']} | BILLTYPE: {row['BILLTYPE']} | IGST: {row['IGST']} | CGST: {row['CGST']} | SGST: {row['SGST']} | BILLINFO: {row.get('BILLINFO', '')}")

