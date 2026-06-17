from dbfread import DBF
import pandas as pd

file_path = "jwerp/1001/silver.frx"
print(f"Loading {file_path}...")
df = pd.DataFrame(list(DBF(file_path, load=True, ignore_missing_memofile=True)))

print("\nVisual Objects in silver.frx:")
for idx, row in df.iterrows():
    if row.get("OBJTYPE") in [5, 8, 17]:
        print(f"Record {idx} | Type: {row['OBJTYPE']} | Name: {repr(row.get('NAME'))} | Expr: {repr(row.get('EXPR'))} | Picture: {repr(row.get('PICTURE'))}")
