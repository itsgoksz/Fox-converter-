from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])

# Filter out CANCEL
if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_sep_oct = df[(df['TDATE'] >= '2025-09-01') & (df['TDATE'] <= '2025-10-31')]
df_sep_oct = df_sep_oct[df_sep_oct['MAINRECORD'] == 1.0]
df_sep_oct = df_sep_oct[df_sep_oct['VTYPE'].str.strip().str.upper() == 'SALE']

print("--- September & October BILLTYPE 3.0 (Retail Sales) ---")
ret_sales = df_sep_oct[df_sep_oct['BILLTYPE'] == 3.0]
for idx, row in ret_sales.iterrows():
    print(f"Date: {row['TDATE'].date()} | Amount: {row['SAMOUNT']} | VTYPECODE: {row['VTYPECODE']} | DEL: '{row.get('DEL', '')}' | STATUS: '{row.get('STATUS', '')}'")

print("\n--- Summary ---")
print(f"Total September Retail: {ret_sales[ret_sales['TDATE'].dt.month == 9]['SAMOUNT'].sum()}")
print(f"Total October Retail: {ret_sales[ret_sales['TDATE'].dt.month == 10]['SAMOUNT'].sum()}")

