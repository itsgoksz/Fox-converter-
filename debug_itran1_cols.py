import pandas as pd
from dbfread import DBF
table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print(list(df.columns))
