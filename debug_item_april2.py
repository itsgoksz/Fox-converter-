import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
tran_path = os.path.join(folder, "TRAN1.DB")
table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(table))
df_tran.columns = [str(c).upper() for c in df_tran.columns]
df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')

df_april = df_tran[(df_tran['TDATE'] >= '2025-04-01') & (df_tran['TDATE'] <= '2025-04-30')]
df_april_sale = df_april[df_april['VTYPE'].str.contains('SALE', na=False, case=False)]

print("MAINRECORD values:")
print(df_april_sale['MAINRECORD'].value_counts(dropna=False))
