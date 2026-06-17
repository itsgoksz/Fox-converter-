import pandas as pd
from dbfread import DBF
import os

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print(df['PTAX'].value_counts())
