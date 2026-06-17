import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
item_path = os.path.join(folder, "ITEMMAST.DB")
item = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_item = pd.DataFrame(iter(item))
df_item.columns = [str(c).upper() for c in df_item.columns]

print(df_item[df_item['INO'] == 27][['INO', 'IDESC', 'IGROUPID', 'PNAME']])
