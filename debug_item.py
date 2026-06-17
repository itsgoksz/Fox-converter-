import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
table = DBF(f"{folder}/ITEMMAST.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df['INO'] = pd.to_numeric(df['INO'], errors='coerce')
print("ITEMMAST for INO=27:")
match = df[df['INO'] == 27]
if not match.empty:
    for k, v in match.iloc[0].to_dict().items():
        if pd.notnull(v) and v != '':
            print(f"{k}: {v}")
else:
    print("Not found")

print("\nFinding Stamp for STAMPID 2 and 3...")
import os
for file in os.listdir(folder):
    if file.lower().endswith(".dbf"):
        try:
            t = DBF(f"{folder}/{file}", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df_t = pd.DataFrame(iter(t))
            if 'ID' in [c.upper() for c in df_t.columns] and 'NAME' in [c.upper() for c in df_t.columns]:
                df_t.columns = [c.upper() for c in df_t.columns]
                res = df_t[df_t['ID'].astype(str).isin(['2', '2.0', '3', '3.0'])]
                if not res.empty:
                    print(f"Found in {file}:")
                    print(res[['ID', 'NAME']])
        except:
            pass
