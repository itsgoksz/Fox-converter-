from dbfread import DBF
import os

frx = "/Users/gokulgautham/Downloads/jwerp/_gstinv.frx"

print("FRX exists:", os.path.exists(frx))
print("FRT exists:", os.path.exists("/Users/gokulgautham/Downloads/jwerp/_gstinv.FRT"))
print("frt exists:", os.path.exists("/Users/gokulgautham/Downloads/jwerp/_gstinv.frt"))

table = DBF(frx, load=False, ignore_missing_memofile=True)

print("\nField names:")
print(table.field_names)

print("\nDBF info:")
print("Record count:", len(table))

try:
    print("Memo filename:", table.memofilename)
except Exception as e:
    print("Couldn't determine memo filename:", e)
