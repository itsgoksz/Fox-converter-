import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
table = DBF(f"{folder}/STAMP.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print(df.head())
