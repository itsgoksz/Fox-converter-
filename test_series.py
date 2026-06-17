from dbfread import DBF
import pandas as pd

# 1. Load Series
s_table = DBF("jwerp/1001/series.db", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
df_s = pd.DataFrame(iter(s_table))

print("--- SERIES.DB Sample ---")
# Find the column that might contain 'SALE LOCAL RD'
name_cols = [c for c in df_s.columns if 'NAME' in c.upper() or 'DESC' in c.upper() or 'SERIES' in c.upper()]
print("Possible Name Columns:", name_cols)
if len(df_s) > 0:
    for c in name_cols:
        print(f"{c}: {df_s[c].head(3).tolist()}")

# 2. Let's look at TRAN1.DB to see how to filter duplicates
t_table = DBF("jwerp/1001/TRAN1.DB", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
df_t = pd.DataFrame(iter(t_table))
print("\n--- TRAN1.DB Double Entry Check ---")
# Filter a single voucher
df_t = df_t[df_t['AMOUNT'] != 0]
if len(df_t) > 0:
    sample_vono = df_t['VONO'].iloc[0]
    sample = df_t[df_t['VONO'] == sample_vono]
    print(sample[['VONO', 'SERIESID', 'AMOUNT', 'CGST', 'TAX', 'MAINRECORD', 'FLAG']].head(5))

