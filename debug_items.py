import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
itran_path = os.path.join(folder, "ITRAN1.DB")
item_path = os.path.join(folder, "ITEMMAST.DB")

itran = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran))
print("ITRAN1.DB Columns:")
print(df_itran.columns.tolist())
print(df_itran.head(1).to_dict('records'))

item = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(item))
print("\nITEMMAST.DB Columns:")
print(df_item.columns.tolist())
print(df_item.head(1).to_dict('records'))
