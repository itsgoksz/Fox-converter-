import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
table = DBF(os.path.join(folder, "TRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

print([col for col in df.columns if 'RO' in col or 'ROUND' in col])
print(df[['AMOUNT', 'CGST', 'SGST', 'IGST']].head())
