import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

for mno in [4, 6]:
    print(f"--- MNO {mno} Submenus ---")
    submenus = df[(df['MNO'] == mno) & (df['SMNO1'] > 0) & (df['SMNO2'] == 0)]
    for idx, row in submenus.head(5).iterrows():
        print(row['MNUCAP'])

