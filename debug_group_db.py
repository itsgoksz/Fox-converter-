import os
import pandas as pd
from dbfread import DBF

folder = "jwerp/1001"
dbs = [f for f in os.listdir(folder) if f.upper().endswith('.DB')]
group_dbs = [f for f in dbs if 'GRP' in f.upper() or 'GROUP' in f.upper()]
print("Group DBs:", group_dbs)

if 'ITEMGRP.DB' in [f.upper() for f in group_dbs]:
    actual_name = next(f for f in group_dbs if f.upper() == 'ITEMGRP.DB')
    grp = DBF(os.path.join(folder, actual_name), load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_grp = pd.DataFrame(iter(grp))
    print(df_grp.head())
