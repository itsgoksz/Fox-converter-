import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
table = DBF(f"{folder}/UNITS.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print("UNITS.DB:")
print(df.head())

table2 = DBF(f"{folder}/VTYPE.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df2 = pd.DataFrame(iter(table2))
print("\nVTYPE.DB:")
print(df2[df2['VTYPE'] == 'SALE'].head())
