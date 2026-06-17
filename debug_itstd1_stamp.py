import pandas as pd
from dbfread import DBF
import os

try:
    table = DBF("jwerp/1001/ITSTD1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df = pd.DataFrame(iter(table))
    for c in df.columns:
        if df[c].dtype == 'object' or df[c].dtype.name == 'string':
            print(f"Col {c} in ITSTD1: {df[c].dropna().unique()[:5]}")
except Exception as e:
    print(e)
