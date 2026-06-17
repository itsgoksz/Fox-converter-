import pandas as pd
from dbfread import DBF
import os

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df = df[df['PTAX'] > 0]
if not df.empty:
    print(df[['TDATE', 'PTAX', 'TAX']].head())
else:
    print("No VAT entries found!")
