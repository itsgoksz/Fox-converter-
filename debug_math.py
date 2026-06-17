from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

df['TDATE'] = pd.to_datetime(df['TDATE'])

if 'NOTECNTR' in df.columns:
    df = df[~df['NOTECNTR'].astype(str).str.upper().str.contains('CANCEL')]

df_sep = df[(df['TDATE'] >= '2025-09-01') & (df['TDATE'] <= '2025-09-30')]
df_sep = df_sep[df_sep['MAINRECORD'] == 1.0]
df_sep = df_sep[df_sep['VTYPE'].str.strip().str.upper() == 'SALE']
df_sep = df_sep[df_sep['BILLTYPE'] == 3.0]

print("--- September Retail Sales Math Check ---")
for idx, row in df_sep.iterrows():
    samount = row.get('SAMOUNT', 0)
    cgst = row.get('CGST', 0)
    sgst = row.get('SGST', 0)
    amount = row.get('AMOUNT', 0)
    discount = row.get('DISCOUNT', 0)
    diff = row.get('DIFF', 0)
    
    calc_total = samount + cgst + sgst - discount
    print(f"SAMOUNT: {samount} | CGST: {cgst} | SGST: {sgst} | DISCOUNT: {discount} | DIFF: {diff} | EXPECTED: {calc_total} | ACTUAL AMOUNT: {amount}")

