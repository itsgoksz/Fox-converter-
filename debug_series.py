import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
table = DBF(f"{folder}/SERIES.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df['SERIESID'] = pd.to_numeric(df['SERIESID'], errors='coerce')
match = df[df['SERIESID'] == 156.0]
if not match.empty:
    for k, v in match.iloc[0].to_dict().items():
        if pd.notnull(v) and v != '':
            print(f"{k}: {v}")
