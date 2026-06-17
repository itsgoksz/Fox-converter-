import pandas as pd
from dbfread import DBF
import os

folder = "jwerp/1001"
itran = DBF(os.path.join(folder, "ITRAN1.DB"), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df_itran = pd.DataFrame(iter(itran))
df_itran.columns = [str(c).upper() for c in df_itran.columns]

print(df_itran[df_itran['TRNID'] == 212].to_dict('records'))
