import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df['MNUCAP'] = df['MNUCAP'].astype(str).str.strip().str.replace(r'[\&\<\\\>]+', '', regex=True)

print(df[df['MNUCAP'].str.contains('GST Reports', case=False, na=False)][['MNO', 'SMNO1', 'SMNO2', 'MNUCAP']])
