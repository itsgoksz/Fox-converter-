import pandas as pd
from dbfread import DBF
table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print([c for c in df.columns if 'WT' in c or 'SUR' in c or 'TAX' in c or 'PTAX' in c])
