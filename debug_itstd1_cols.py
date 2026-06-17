import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/ITSTD1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print(df.columns)
