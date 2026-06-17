import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
stock_summary = df[(df['PROMPT'].str.contains('Stock Summary', case=False, na=False)) | 
                   (df['PAD'].str.contains('STK_SUM', case=False, na=False)) |
                   (df['PROMPT'].str.contains('Qty Wise', case=False, na=False))]
print(df[df['PROMPT'].str.contains('Stock Summary', case=False, na=False)][['PROMPT', 'PAD', 'BAR']])
