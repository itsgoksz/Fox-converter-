from dbfread import DBF
table = DBF("jwerp/1001/items.db", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
print(", ".join([f.name for f in table.fields]))
