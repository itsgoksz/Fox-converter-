from dbfread import DBF

def inspect_db(filename):
    print(f"\n--- Structure for {filename} ---")
    try:
        # load=False ensures we do not load the actual data rows into memory
        table = DBF(filename, load=False, ignore_missing_memofile=True)
        print("SUCCESS! It is a valid DBF file.")
        print(f"Columns ({len(table.fields)}):")
        print(", ".join([field.name for field in table.fields]))
    except Exception as e:
        print(f"Failed: {e}")

inspect_db("jwerp/1001/formmst.db")
inspect_db("jwerp/1001/saltrn1.db")
