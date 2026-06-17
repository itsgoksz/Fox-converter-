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

def get_particular(row):
    vtype = str(row.get('VTYPE', 'SALE')).strip().upper()
    region = "CENTRAL" if float(row.get('IGST', 0)) > 0 else "LOCAL"
    info = str(row.get('BILLINFO', '')).upper()
    dealer = "CONSUMER" if "CONSUMER" in info else "RD"
    return f"{vtype} {region} {dealer}"

df['Particular'] = df.apply(get_particular, axis=1)

print(df[df['Particular'] == 'SALE LOCAL RD']['SAMOUNT'].astype(float).sum())
print(df[df['Particular'] == 'SALE LOCAL CONSUMER']['SAMOUNT'].astype(float).sum())
