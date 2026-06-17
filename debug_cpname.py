from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

df_sale = df[df['VTYPE'].astype(str).str.strip().str.upper() == 'SALE']
print("CPNAME/GSTIN sample:")
print(df_sale[['TDATE', 'BILLNO', 'CPNAME', 'CPGSTIN', 'SAMOUNT']].head(5).to_string())
