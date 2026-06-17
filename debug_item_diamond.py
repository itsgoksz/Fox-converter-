import pandas as pd
from dbfread import DBF
item_table = DBF("jwerp/1001/ITEMMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(item_table))
print(df[df['PNAME'].str.contains('DIA', case=False, na=False)].dropna(axis=1, how='all').head())
