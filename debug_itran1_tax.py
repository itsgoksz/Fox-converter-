import pandas as pd
from dbfread import DBF
table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df = df[df['PTAX'] > 0]
print(df[['INO', 'WT', 'TVALUE', 'TOTAL', 'PTAX', 'SGST', 'CGST']].head())
