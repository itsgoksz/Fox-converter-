import pandas as pd
from dbfread import DBF
import os

for f in os.listdir("jwerp/1001"):
    if f.lower().endswith(".dbf"):
        try:
            table = DBF(f"jwerp/1001/{f}", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
            df = pd.DataFrame(iter(table))
            for c in df.columns:
                if df[c].dtype == 'object' or df[c].dtype.name == 'string':
                    if df[c].astype(str).str.contains('18K', case=False, na=False).any():
                        print(f"Found '18K' in file {f}, column {c}")
        except Exception as e:
            pass
