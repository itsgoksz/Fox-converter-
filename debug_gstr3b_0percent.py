import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
table = DBF(os.path.join(folder, "TRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

df['TDATE'] = pd.to_datetime(df['TDATE'], errors='coerce')
df = df[(df['TDATE'] >= '2025-10-01') & (df['TDATE'] <= '2025-10-31')]
df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
df = df[df['VTYPE'].str.contains('SALE', na=False)]
df = df[df['MAINRECORD'] == 1.0]

print("0% Sales VTYPES:")
print(df[df['PTAX'] == 0]['VTYPE'].value_counts())
print("\n0% Sales BILLTYPE:")
print(df[df['PTAX'] == 0]['BILLTYPE'].value_counts())
print("\n0% Sales BILLINFO:")
print(df[df['PTAX'] == 0]['BILLINFO'].value_counts())

