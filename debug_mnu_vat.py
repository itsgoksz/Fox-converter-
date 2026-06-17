import pandas as pd
from dbfread import DBF
import os

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df['MNUCAP'] = df['MNUCAP'].astype(str).str.strip().str.replace(r'[\&\<\\\>]+', '', regex=True)

vat_mno1 = df[df['MNUCAP'].str.contains('VAT', case=False, na=False)]
print(vat_mno1[['MNUCAP', 'MNO', 'SMNO1', 'SMNO2', 'CMD']])

for _, row in vat_mno1.iterrows():
    if row['SMNO2'] == 0:
        # This is a subfolder, list its children
        children = df[(df['MNO'] == row['MNO']) & (df['SMNO1'] == row['SMNO1']) & (df['SMNO2'] > 0)]
        print(f"\nChildren of {row['MNUCAP']}:")
        print(children[['MNUCAP', 'CMD']])
