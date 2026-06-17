from dbfread import DBF
import os
file = "jwerp/1001/vtypemst.db"
if os.path.exists(file):
    table = DBF(file, load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
    print("VTYPEMST Columns:", ", ".join([f.name for f in table.fields]))
else:
    print("VTYPEMST not found.")
