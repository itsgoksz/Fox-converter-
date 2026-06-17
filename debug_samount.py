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
df['BILLTYPE'] = pd.to_numeric(df['BILLTYPE'], errors='coerce').fillna(1.0)
df = df[df['BILLTYPE'].isin([1.0, 2.0])] # Exclude 3.0

print("Sum of SAMOUNT:", pd.to_numeric(df['SAMOUNT'], errors='coerce').sum())
print("Sum of AMOUNT:", pd.to_numeric(df['AMOUNT'], errors='coerce').sum())

def get_particular(row):
    vtype = str(row.get('VTYPE', 'SALE')).strip().upper()
    region = "CENTRAL" if float(row.get('IGST', 0)) > 0 else "LOCAL"
    info = str(row.get('BILLINFO', '')).upper()
    dealer = "CONSUMER" if "CONSUMER" in info else "RD"
    return f"{vtype} {region} {dealer}"

df['Particular'] = df.apply(get_particular, axis=1)

grouped = df.groupby('Particular').agg({
    'SAMOUNT': lambda x: pd.to_numeric(x, errors='coerce').sum(),
    'AMOUNT': lambda x: pd.to_numeric(x, errors='coerce').sum(),
    'CGST': lambda x: pd.to_numeric(x, errors='coerce').sum(),
})
print("\nGrouped SAMOUNT vs AMOUNT:")
print(grouped)
