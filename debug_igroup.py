import os
import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
grp = DBF(os.path.join(folder, "igroup.db"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_grp = pd.DataFrame(iter(grp))
print(df_grp.head())
