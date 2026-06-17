from dbfread import DBF
import pandas as pd

s_table = DBF("jwerp/1001/series.db", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
df_s = pd.DataFrame(iter(s_table))

print("--- SERIES.DB BILLTYPE and TAXTYPE ---")
print(df_s[['SERIESID', 'SERIES', 'BILLTYPE', 'TAXTYPE', 'INCL']].head(15))

