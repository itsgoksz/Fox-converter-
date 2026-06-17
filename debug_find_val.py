import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
for c in df.columns:
    if df[c].dtype == 'object' or df[c].dtype.name == 'string':
        if df[c].astype(str).str.contains('18K|AAAAAAAAAA', case=False, na=False).any():
            print(f"Found in column: {c}")
