import pandas as pd
from dbfread import DBF
tran_table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_tran = pd.DataFrame(iter(tran_table))
print([c for c in ['TRNID', 'VTYPE', 'TDATE', 'SITEID'] if c not in df_tran.columns])
