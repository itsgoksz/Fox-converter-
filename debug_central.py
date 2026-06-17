from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

# Filter for May
df['TDATE'] = pd.to_datetime(df['TDATE'])
df_may = df[(df['TDATE'] >= '2025-05-01') & (df['TDATE'] <= '2025-05-31')]
df_may = df_may[df_may['MAINRECORD'] == 1.0]
df_may = df_may[df_may['VTYPE'].str.strip().str.upper() == 'SALE']

print("--- May Transactions with IGST ---")
central = df_may[df_may['IGST'] > 0]
if not central.empty:
    print(central[['SAMOUNT', 'IGST', 'BILLTYPE']])
else:
    print("NO IGST TRANSACTIONS FOUND IN MAY?!")

# Let's also check August because the user said "for august the retail sale is correct... but other rows still need to be fixed"
df_aug = df[(df['TDATE'] >= '2025-08-01') & (df['TDATE'] <= '2025-08-31')]
df_aug = df_aug[df_aug['MAINRECORD'] == 1.0]
df_aug = df_aug[df_aug['VTYPE'].str.strip().str.upper() == 'SALE']
print("\n--- August Transactions Breakdown ---")
print(df_aug[['SAMOUNT', 'IGST', 'BILLTYPE']])

