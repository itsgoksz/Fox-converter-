import os
import pandas as pd
from dbfread import DBF

tables = {}

# Load all DBF files
for file in os.listdir("."):
    if file.lower().endswith(".dbf"):
        try:
            table_name = os.path.splitext(file)[0].upper()

            df = pd.DataFrame(iter(DBF(file)))

            df.columns = [c.upper() for c in df.columns]

            tables[table_name] = df

        except Exception as e:
            print(f"Failed to load {file}: {e}")

print(f"Loaded {len(tables)} tables")
