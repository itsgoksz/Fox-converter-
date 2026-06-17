from dbfread import DBF
import pandas as pd
import glob

# 1. Find the VTYPE Master file
folder = "jwerp/1001"
print("--- VTYPE Master Files ---")
v_files = glob.glob(f"{folder}/*vtype*.db", recursive=True) + glob.glob(f"{folder}/*VTYPE*.DB", recursive=True) + glob.glob(f"{folder}/*VTYPE*.db", recursive=True)
for f in v_files:
    print(f)

print("\n--- Let's look for SALE LOCAL RD in any master file ---")
# If no vtype, look at any master file
db_files = glob.glob(f"{folder}/*.db") + glob.glob(f"{folder}/*.DB")
for f in db_files:
    if 'TRAN' not in f.upper() and 'STD' not in f.upper():
        try:
            t = DBF(f, load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
            cols = [c.name.upper() for c in t.fields]
            if 'VTYPE' in cols or 'VTYPEID' in cols or 'VTYPECODE' in cols or 'VTYPENAME' in cols:
                print(f"Found VTYPE column in: {f}")
                # Print a few rows
                df = pd.DataFrame(iter(t))
                print(df.head(2))
        except:
            pass

