from dbfread import DBF
import pandas as pd
import glob

# Load TRAN1.DB
t_table = DBF("jwerp/1001/TRAN1.DB", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
df_t = pd.DataFrame(iter(t_table))

# Find the exact transaction that generated 4207.70 CGST
# Note: 4207.70 might be the sum of multiple transactions, but let's look for anything around 4207
df_cgst = df_t[df_t['CGST'] > 0]
if len(df_cgst) > 0:
    print("--- Sample Transactions with CGST ---")
    sample = df_cgst.head(3)
    # Print all non-null columns for the first sample to find the "Type" ID
    first_row = sample.iloc[0].dropna()
    print("\nColumns with data for this transaction:")
    for col, val in first_row.items():
        if col not in ['LNARR', 'NARR', 'TRDATA', 'CPADD1']:
            print(f"{col}: {val}")
else:
    print("No CGST > 0 found in TRAN1.DB")

