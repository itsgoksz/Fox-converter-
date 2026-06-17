from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

# Filter for May
df['TDATE'] = pd.to_datetime(df['TDATE'])
df_may = df[(df['TDATE'] >= '2025-05-01') & (df['TDATE'] <= '2025-05-31')]

# Filter MAINRECORD
df_may = df_may[df_may['MAINRECORD'] == 1.0]
df_may = df_may[(df_may['AMOUNT'] != 0) | (df_may['CGST'] != 0) | (df_may['SGST'] != 0) | (df_may['IGST'] != 0)]
df_may = df_may[df_may['VTYPE'].astype(str).str.upper().str.contains('SALE')]

# Map buckets
def map_bucket(row):
    if float(row.get('IGST', 0)) > 0:
        return 'Central Sale'
    if 'CONSUMER' in str(row.get('BILLINFO', '')).upper():
        return 'Retail Sale'
    return 'Tax Invoice'

df_may['Bucket'] = df_may.apply(map_bucket, axis=1)

# Sum SAMOUNT
grouped = df_may.groupby('Bucket')['SAMOUNT'].sum()
print("--- May SAMOUNT Totals ---")
print(grouped)

