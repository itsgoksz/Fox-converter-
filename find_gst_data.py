import glob
from dbfread import DBF

folder = "jwerp/1001"
db_files = glob.glob(f"{folder}/*.db") + glob.glob(f"{folder}/*.dbf") + glob.glob(f"{folder}/*.DB")

print("--- Searching for GST/Tax Structure ---")
for file in db_files:
    try:
        table = DBF(file, load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
        cols = [f.name.upper() for f in table.fields]
        
        # Look for files containing GST columns
        if 'CGST' in cols or 'SGST' in cols or 'IGST' in cols or 'TAX' in cols:
            print(f"\nMatch Found: {file}")
            print(f"Columns: {', '.join(cols)}")
    except:
        pass

