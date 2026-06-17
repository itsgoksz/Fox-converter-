from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

print("--- All Unique MNOs ---")
print(df['MNO'].unique())

print("\n--- Looking for 'Sale Typewise' anywhere in DB ---")
print(df[df['MNUCAP'].astype(str).str.contains('Sale Typewise', case=False, na=False)][['MNO', 'SMNO1', 'SMNO2', 'MNUCAP', 'CMD']])

