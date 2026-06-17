import pandas as pd
from dbfread import DBF

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df_stock = df[(df['MNUCAP'].str.contains('Stock Summary', case=False, na=False)) | 
              (df['MNUCAP'].str.contains('Qty Wise', case=False, na=False)) |
              (df['MNUCAP'].str.contains('Item Ledger', case=False, na=False)) |
              (df['UNDER'].str.contains('10', na=False))] # Just guessing 'UNDER' might be ID
print(df[df['MNUCAP'].str.contains('Stock Summary|Qty Wise|Item Ledger|Stock Register|Site Wise|Complete Detailed|Stock List', case=False, na=False)][['MNUID', 'UNDER', 'MNUCAP', 'CMD']])
