import pandas as pd
from dbfread import DBF

tran_table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(tran_table))
df_tran['TDATE'] = pd.to_datetime(df_tran['TDATE'], errors='coerce')
print(f"Total TRAN1 records: {len(df_tran)}")
print(f"TRAN1 records on 2026-03-31: {len(df_tran[df_tran['TDATE'] == '2026-03-31'])}")
print(f"TRAN1 records before 2026-03-31: {len(df_tran[df_tran['TDATE'] < '2026-03-31'])}")

print("Unique VTYPES for records before 2026-03-31:")
print(df_tran[df_tran['TDATE'] < '2026-03-31']['VTYPE'].value_counts())

