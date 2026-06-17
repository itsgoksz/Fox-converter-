from dbfread import DBF
import pandas as pd
import glob

print("--- Looking for Bill Type Master ---")
b_files = glob.glob("jwerp/1001/*bill*.db", recursive=True) + glob.glob("jwerp/1001/*type*.db", recursive=True)
for f in b_files:
    print(f)
    try:
        table = DBF(f, load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
        cols = [c.name.upper() for c in table.fields]
        print(cols)
        if 'BILLTYPE' in cols or 'TYPE' in cols:
            df = pd.DataFrame(iter(table))
            print(df.head())
    except:
        pass

