from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]
df['TDATE'] = pd.to_datetime(df['TDATE'])

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_aug = df[(df['TDATE'] >= '2025-08-01') & (df['TDATE'] <= '2025-08-31')]
df_aug = df_aug[df_aug['MAINRECORD'] == 1.0]
df_aug = df_aug[df_aug['VTYPE'].str.strip().str.upper() == 'SALE']
df_aug = df_aug[df_aug['BILLTYPE'] == 3.0]

print("--- August Retail Sales (Confirmed Correct by User) ---")
for idx, row in df_aug.iterrows():
    print(f"SAMOUNT: {row['SAMOUNT']} | CGST: {row['CGST']} | SGST: {row['SGST']}")

