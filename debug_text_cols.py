import pandas as pd
from dbfread import DBF
itran_table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(itran_table))
text_cols = df.select_dtypes(include=['object']).columns
print(text_cols)
for c in text_cols:
    vals = df[c].dropna().unique()
    if len(vals) > 0 and len(vals) < 50:
        print(f"{c}: {vals[:5]}")
