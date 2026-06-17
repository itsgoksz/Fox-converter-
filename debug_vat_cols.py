import pandas as pd
from dbfread import DBF
import os

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
cols = [str(c).upper() for c in df.columns]
vat_cols = [c for c in cols if 'VAT' in c or 'TAX' in c]
print("VAT/TAX Columns in TRAN1:", vat_cols)
