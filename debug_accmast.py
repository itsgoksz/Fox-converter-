from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/ACCMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

print(df.columns)
print(df.head(2).to_dict('records'))
