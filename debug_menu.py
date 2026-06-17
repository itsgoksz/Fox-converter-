from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

print("--- Top Level Menus (SMNO1 == 0) ---")
mains = df[df['SMNO1'] == 0]
for idx, row in mains.iterrows():
    print(f"MNO: {row['MNO']} | CAPTION: {row['MNUCAP']} | HIDE: {row.get('HIDE', 'N/A')}")

