import pandas as pd
from dbfread import DBF
itran_table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran_table))
print(df_itran[['PCLASS', 'KTBATCH']].dropna().head())
