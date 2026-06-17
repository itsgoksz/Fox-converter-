from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
df.columns = [str(c).upper() for c in df.columns]

# Filter for SALES
if 'VTYPE' in df.columns:
    df['VTYPE'] = df['VTYPE'].astype(str).str.strip().str.upper()
    df = df[df['VTYPE'] == 'SALE']
    
# Keep only main records
if 'MAINRECORD' in df.columns:
    df = df[df['MAINRECORD'] == 1.0]

print("Available Columns for GSTR1:")
print([c for c in df.columns if c in ['TDATE', 'VNO', 'BILLNO', 'ACNAME', 'PARTY', 'GSTIN', 'SAMOUNT', 'AMOUNT', 'CGST', 'SGST', 'IGST', 'PTAX', 'STATE']])

print("\nSample Data:")
print(df[[c for c in df.columns if c in ['TDATE', 'VNO', 'ACNAME', 'GSTIN', 'SAMOUNT', 'AMOUNT', 'CGST', 'SGST', 'IGST']]].head(3).to_dict('records'))

