import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

# Filter for September
df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
df_sep = df[(df['TDATE'].dt.month == 9) & (df['TDATE'].dt.year == 2025)]

# Filter for RK DIAMOND
# First get ACNO for RK DIAMOND from ACCMAST
acc_table = DBF("jwerp/1001/ACCMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
acc = pd.DataFrame(iter(acc_table))
acc.columns = [str(c).upper() for c in acc.columns]
rk_acnos = acc[acc['CNAME'].str.contains('RK DIAMOND', na=False)]['ACNO'].tolist()

df_rk = df_sep[df_sep['ACNO'].isin(rk_acnos)]
df_rk = df_rk[df_rk['VTYPE'].astype(str).str.contains('SALE', case=False, na=False)]
df_rk = df_rk[df_rk['MAINRECORD'] == 1.0]

print("Columns differing across duplicates for RK DIAMOND:")
for idx, row in df_rk.iterrows():
    print(f"TRNID: {row.get('TRNID')}, VONO: {row.get('VONO')}, SERIESID: {row.get('SERIESID')}, VTYPE: {row.get('VTYPE')}, AMOUNT: {row.get('AMOUNT')}, NARR: {row.get('NARR')}, DEL: {row.get('DEL')}")
