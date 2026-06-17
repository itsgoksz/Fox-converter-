import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
df_sep = df[(df['TDATE'].dt.month == 9) & (df['TDATE'].dt.year == 2025)]
df_sep = df_sep[df_sep['VTYPE'].astype(str).str.contains('SALE', case=False, na=False)]
df_sep = df_sep[df_sep['MAINRECORD'] == 1.0]

for c in ['CGST', 'SGST', 'IGST']:
    df_sep[c] = pd.to_numeric(df_sep[c], errors='coerce').fillna(0)

# 1. Sum of all 33 valid sales
print(f"Sum of 33 rows (Amount): {df_sep['AMOUNT'].sum()}")
print(f"Sum of 33 rows (SAmount): {df_sep['SAMOUNT'].sum()}")

# 2. Filter for Tax Invoices
df_tax = df_sep[(df_sep['CGST'] != 0) | (df_sep['SGST'] != 0) | (df_sep['IGST'] != 0)]
if 'BILLTYPE' in df_sep.columns:
    df_tax = df_tax[pd.to_numeric(df_tax['BILLTYPE'], errors='coerce').fillna(1.0).isin([1.0, 2.0, 3.0])]

print(f"Sum of 14 Tax rows (Amount): {df_tax['AMOUNT'].sum()}")
print(f"Sum of 14 Tax rows (SAmount): {df_tax['SAMOUNT'].sum()}")
