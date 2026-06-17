from dbfread import DBF
import pandas as pd

s_table = DBF("jwerp/1001/series.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_s = pd.DataFrame(iter(s_table))

print("Total rows in series.db:", len(df_s))
print("Unique SERIESID count:", df_s['SERIESID'].nunique())

# Find duplicates
dupes = df_s[df_s.duplicated(subset=['SERIESID'], keep=False)].sort_values('SERIESID')
if not dupes.empty:
    print("\n--- DUPLICATE SERIES IDs FOUND! ---")
    print(dupes[['SERIESID', 'SERIES', 'BILLTYPE']])
